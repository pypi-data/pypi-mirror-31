#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import logging
import sys

from packageurl import PackageURL
from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import BooleanType
from schematics.types import DateTimeType
from schematics.types import LongType
from schematics.types import StringType
from schematics.types.compound import DictType
from schematics.types.compound import ListType
from schematics.types.compound import ModelType

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str = unicode  # NOQA
    basestring = basestring  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA
    basestring = (bytes, str,)  # NOQA

"""
Data models for package information and dependencies, abstracting the
differences existing between package formats and tools.

A package has a somewhat fuzzy definition and is code that can be consumed and
provisioned by a package manager or can be installed.

It can be a single file such as script; more commonly a package is stored in an
archive or directory.

A package contains:
 - information typically in a "manifest" file,
 - a payload of code, doc, data.

Structured package information are found in multiple places:
- in manifest file proper (such as a Maven POM, NPM package.json and many others)
- in binaries (such as an Elf or LKM, Windows PE or RPM header).
- in code (JavaDoc tags or Python __copyright__ magic)
There are collectively named "manifests" in ScanCode.

We handle package information at two levels:
1.- package information collected in a "manifest" at a file level
2.- aggregated package information based on "manifest" at a directory or archive
level (or in some rarer cases file level)

The second requires the first to be computed.
The schema for these two is the same.
"""

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


class OrderedDictType(DictType):
    """
    An ordered dictionary type.
    If a value is an ordered dict, it is sorted or
    """

    def __init__(self, field, coerce_key=None, **kwargs):
        kwargs['default'] = OrderedDict()
        super(OrderedDictType, self).__init__(field, coerce_key=None, **kwargs)

    def to_native(self, value, safe=False, context=None):
        if not value:
            value = OrderedDict()

        if not isinstance(value, (dict, OrderedDict)):
            raise ValidationError(u'Only dictionaries may be used in an OrderedDictType')

        items = value.iteritems()
        if not isinstance(value, OrderedDict):
            items = sorted(value.iteritems())

        return OrderedDict((self.coerce_key(k), self.field.to_native(v, context))
                    for k, v in items)

    def export_loop(self, dict_instance, field_converter,
                    role=None, print_none=False):
        """Loops over each item in the model and applies either the field
        transform or the multitype transform.  Essentially functions the same
        as `transforms.export_loop`.
        """
        data = OrderedDict()

        items = dict_instance.iteritems()
        if not isinstance(dict_instance, OrderedDict):
            items = sorted(dict_instance.iteritems())

        for key, value in items:
            if hasattr(self.field, 'export_loop'):
                shaped = self.field.export_loop(value, field_converter,
                                                role=role)
                feels_empty = shaped and len(shaped) == 0
            else:
                shaped = field_converter(self.field, value)
                feels_empty = shaped is None

            if feels_empty and self.field.allow_none():
                data[key] = shaped
            elif shaped is not None:
                data[key] = shaped
            elif print_none:
                data[key] = shaped

        if len(data) > 0:
            return data
        elif len(data) == 0 and self.allow_none():
            return data
        elif print_none:
            return data


class BaseListType(ListType):
    """
    ListType with a default of an empty list.
    """

    def __init__(self, field, **kwargs):
        kwargs['default'] = []
        super(BaseListType, self).__init__(field=field, **kwargs)


class BaseModel(Model):
    """
    Base class for all schematics models.
    """

    def __init__(self, **kwargs):
        super(BaseModel, self).__init__(raw_data=kwargs)

    def to_dict(self, **kwargs):
        """
        Return a dict of primitive Python types for this model instance.
        This is an OrderedDict because each model has a 'field_order' option.
        """
        return self.to_primitive(**kwargs)


party_person = 'person'
# often loosely defined
party_project = 'project'
# more formally defined
party_org = 'organization'
PARTY_TYPES = (party_person, party_project, party_org,)


class Party(BaseModel):
    metadata = dict(
        label='party',
        description='A party is a person, project or organization related to a package.')

    type = StringType(choices=PARTY_TYPES)
    type.metadata = dict(
        label='party type',
        description='the type of this party: One of: ' + ', '.join(PARTY_TYPES))

    name = StringType()
    name.metadata = dict(
        label='name',
        description='Name of this party.')

    role = StringType()
    role.metadata = dict(
        label='party role',
        description='A role for this party. Something such as author, '
        'maintainer, contributor, owner, packager, distributor, '
        'vendor, developer, owner, etc.')

    url = StringType()
    url.metadata = dict(
        label='url',
        description='URL to a primary web page for this party.')

    email = StringType()
    email.metadata = dict(
        label='email',
        description='Email for this party.')

    class Options:
        fields_order = 'type', 'role', 'name', 'email', 'url'


class PackageRelationship(BaseModel):
    metadata = dict(
        label='relationship between two packages',
        description='A directed relationship between two packages. '
            'This consiste of three attributes:'
            'The "from" (or subject) package "purl" in the relationship, '
            'the "to" (or object) package "purl" in the relationship, '
            'and the "relationship" (or predicate) string that specifies the relationship.'
            )

    from_purl = StringType()
    from_purl.metadata = dict(
        label='"From" purl package URL in the relationship',
        description='A compact purl package URL.')

    relationship = StringType()
    relationship.metadata = dict(
        label='Relationship between two packages.',
        description='Relationship between the from and to package '
            'URLs such as "source_of" when a package is the source '
            'code package for another package')

    to_purl = StringType()
    to_purl.metadata = dict(
        label='"To" purl package URL in the relationship',
        description='A compact purl package URL.')

    class Options:
        # this defines the important serialization order in schematics
        fields_order = [
            'from_purl',
            'relationship',
            'to_purl',
        ]


class BasePackage(BaseModel):
    metadata = dict(
        label='base package',
        description='A base identifiable package object using discrete '
            'identifying attributes as specified here '
            'https://github.com/package-url/purl-spec.')

    # class-level attributes used to recognize a package
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()
    # list of known metafiles for a package type
    metafiles = []

    # Optional. Public default web base URL for package homepages of this
    # package type on the default repository.
    default_web_baseurl = None

    # Optional. Public default download base URL for direct downloads of this
    # package type the default repository.
    default_download_baseurl = None

    # Optional. Public default API repository base URL for package API calls of
    # this package type on the default repository.
    default_api_baseurl = None

    type = StringType()
    type.metadata = dict(
        label='package type',
        description='Optional. A short code to identify what is the type of this '
            'package. For instance gem for a Rubygem, docker for container, '
            'pypi for Python Wheel or Egg, maven for a Maven Jar, '
            'deb for a Debian package, etc.')

    namespace = StringType()
    namespace.metadata = dict(
        label='package namespace',
        description='Optional namespace for this package.')

    name = StringType(required=True)
    name.metadata = dict(
        label='package name',
        description='Name of the package.')

    version = StringType()
    version.metadata = dict(
        label='package version',
        description='Optional version of the package as a string.')

    qualifiers = DictType(StringType)
    qualifiers.metadata = dict(
        label='package qualifiers',
        description='Optional mapping of key=value pairs qualifiers for this package')

    subpath = StringType()
    subpath.metadata = dict(
        label='extra package subpath',
        description='Optional extra subpath inside a package and relative to the root of this package')

    class Options:
        # this defines the important serialization order in schematics
        fields_order = [
            'type',
            'namespace',
            'name',
            'version',
            'qualifiers',
            'subpath',
        ]

    @property
    def purl(self):
        """
        Return a compact purl package URL string.
        """
        return PackageURL(
            self.type, self.namespace, self.name, self.version,
            self.qualifiers, self.subpath).to_string()

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        """
        Return the package repository homepage URL for this package, e.g. the
        URL to the page for this package in its package repository. This is
        typically different from the package homepage URL proper.
        Subclasses should override to provide a proper value.
        """
        return

    def repository_download_url(self, baseurl=default_download_baseurl):
        """
        Return the package repository download URL to download the actual
        archive of code of this package. This may be different than the actual
        download URL and is computed from the default public respoitory baseurl.
        Subclasses should override to provide a proper value.
        """
        return

    def api_data_url(self, baseurl=default_api_baseurl):
        """
        Return the package repository API URL to obtain structured data for this
        package such as the URL to a JSON or XML api.
        Subclasses should override to provide a proper value.
        """
        return


class DependentPackage(BaseModel):
    metadata = dict(
        label='dependent package',
        description='An identifiable dependent package package object.')

    purl = StringType()
    purl.metadata = dict(
        label='Dependent package URL',
        description='A compact purl package URL')

    requirement = StringType()
    requirement.metadata = dict(
        label='dependent package version requirement',
        description='A string defining version(s)requirements. Package-type specific.')

    scope = StringType()
    scope.metadata = dict(
        label='dependency scope',
        description='The scope of this dependency, such as runtime, install, etc. '
        'This is package-type specific and is the original scope string.')

    is_runtime = BooleanType(default=True)
    is_runtime.metadata = dict(
        label='is runtime flag',
        description='True if this dependency is a runtime dependency.')

    is_optional = BooleanType(default=False)
    is_runtime.metadata = dict(
        label='is optional flag',
        description='True if this dependency is an optional dependency')

    is_resolved = BooleanType(default=False)
    is_resolved.metadata = dict(
        label='is resolved flag',
        description='True if this dependency version requirement has '
        'been resolved and this dependency url points to an '
        'exact version.')

    class Options:
        # this defines the important serialization order in schematics
        fields_order = [
            'purl',
            'requirement',
            'scope',
            'is_runtime',
            'is_optional',
            'is_resolved',
        ]


code_type_src = 'source'
code_type_bin = 'binary'
code_type_doc = 'documentation'
code_type_data = 'data'
CODE_TYPES = (
    code_type_src,
    code_type_bin,
    code_type_doc,
    code_type_data,
)


class Package(BasePackage):
    metadata = dict(
        label='package',
        description='A package object.')

    description = StringType()
    description.metadata = dict(
        label='Description',
        description='Description for this package. '
        'By convention the first should be a summary when available.')

    release_date = DateTimeType()
    release_date.metadata = dict(
        label='release date',
        description='Release date of the package')

    primary_language = StringType()
    primary_language.metadata = dict(label='Primary programming language')

    code_type = StringType(choices=CODE_TYPES)
    code_type.metadata = dict(
        label='code type',
        description='Primary type of code in this Package such as source, binary, data, documentation.'
    )

    parties = BaseListType(ModelType(Party))
    parties.metadata = dict(
        label='parties',
        description='A list of parties such as a person, project or organization.'
    )

    # FIXME: consider using tags rather than keywords
    keywords = BaseListType(StringType())
    keywords.metadata = dict(
        label='keywords',
        description='A list of keywords.')

    size = LongType()
    size.metadata = dict(
        label='download size',
        description='size of the package download in bytes')

    download_url = StringType()
    download_url.metadata = dict(
        label='Download URL',
        description='A direct download URL.')

    download_checksums = BaseListType(StringType())
    download_checksums.metadata = dict(
        label='download checksums',
        description='A list of checksums for this download in '
        'hexadecimal and prefixed by the lowercased checksum algorithm and a colon '
        'e.g. sha1:c5095691347bd5ad3b5e180238c3914d16f05812')

    homepage_url = StringType()
    homepage_url.metadata = dict(
        label='homepage URL',
        description='URL to the homepage for this package.')

    # FIXME: use a simpler, compact VCS URL instead???
#     vcs_url = StringType()
#     vcs_url.metadata = dict(
#         label='Version control URL',
#         description='Version control URL for this package using the SPDX VCS URL conventions.')

    VCS_CHOICES = ['git', 'svn', 'hg', 'bzr', 'cvs']
    vcs_tool = StringType(choices=VCS_CHOICES)
    vcs_tool.metadata = dict(
        label='Version control system tool',
        description='The type of VCS tool for this package. One of: ' + ', '.join(VCS_CHOICES))

    vcs_repository = StringType()
    vcs_repository.metadata = dict(
        label='VCS Repository URL',
        description='a URL to the VCS repository in the SPDX form of:'
        'git+https://github.com/nexb/scancode-toolkit.git')

    vcs_revision = StringType()
    vcs_revision.metadata = dict(
        label='VCS revision',
        description='a revision, commit, branch or tag reference, etc. '
        '(can also be included in the URL)')

    code_view_url = StringType()
    code_view_url.metadata = dict(
        label='code view URL',
        description='a URL where the code can be browsed online')

    bug_tracking_url = StringType()
    bug_tracking_url.metadata = dict(
        label='bug tracking URL',
        description='URL to the issue or bug tracker for this package')

    copyright = StringType()
    copyright.metadata = dict(
        label='Copyright',
        description='Copyright statements for this package. Typically one per line.')

    license_expression = StringType()
    license_expression.metadata = dict(
        label='license expression',
        description='The license expression for this package.')

    declared_licensing = StringType()
    declared_licensing.metadata = dict(
        label='declared licensing',
        description='The licensing text as declared in a package manifest.')

    notice_text = StringType()
    notice_text.metadata = dict(
        label='notice text',
        description='A notice text for this package.')

    dependencies = BaseListType(ModelType(DependentPackage))
    dependencies.metadata = dict(
        label='dependencies',
        description='A list of DependentPackage for this package. ')

    related_packages = BaseListType(ModelType(PackageRelationship))
    related_packages.metadata = dict(
        label='related packages',
        description='A list of package relationships for this package. '
        'For instance an SRPM is the "source of" a binary RPM.')

    class Options:
        # this defines the important serialization order in schematics
        fields_order = [
            'type',
            'namespace',
            'name',
            'version',
            'qualifiers',
            'subpath',
            'primary_language',
            'code_type',
            'description',
            'size',
            'release_date',
            'parties',
            'keywords',
            'homepage_url',
            'download_url',
            'download_checksums',
            'bug_tracking_url',
            'code_view_url',
            'vcs_tool',
            'vcs_repository',
            'vcs_revision',
            'copyright',
            'license_expression',
            'declared_licensing',
            'notice_text',
            'dependencies',
            'related_packages'
        ]

        # we use for now a "role" that excludes deps and relationships from the
        # serialization
        roles = {'no_deps': blacklist('dependencies', 'related_packages')}

    def __init__(self, location=None, **kwargs):
        """
        Initialize a new Package. Subclass can override but should override the
        recognize method to populate a package accordingly.
        """
        # path to a file or directory where this Package is found in a scan
        self.location = location
        super(Package, self).__init__(**kwargs)

    @classmethod
    def recognize(cls, location):
        """
        Return a Package object or None given a file location pointing to a
        package archive, manifest or similar.

        Sub-classes should override to implement their own package recognition.
        """
        return cls(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        """
        Return the Resource for the package root given a `manifest_resource`
        Resource object that represents a manifest in the `codebase` Codebase.

        Each package type and instance have different conventions on how a
        package manifest realtes to the toor of a package.

        For instance, given a "package.json" file, the root of an npm is the
        parent directory. The same applies with a Maven "pom.xml". In the case
        of a "xyz.pom" file found inside a JAR META-INF/ directory, the root is
        the JAR itself which may not be the direct parent

        Each package type should subclass as needed. This deafult to return the
        same path.
        """
        return manifest_resource
#

# Package types
# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here


class DebianPackage(Package):
    metafiles = ('*.control',)
    extensions = ('.deb',)
    filetypes = ('debian binary package',)
    mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
    type = StringType(default='deb')

# class AlpinePackage(Package):
#     metafiles = ('*.control',)
#     extensions = ('.apk',)
#     filetypes = ('debian binary package',)
#     mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
#     type = StringType(default='apk')


class JavaJar(Package):
    metafiles = ('META-INF/MANIFEST.MF',)
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    type = StringType(default='jar')
    primary_language = StringType(default='Java')


class JavaWar(Package):
    metafiles = ('WEB-INF/web.xml',)
    extensions = ('.war',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='war')
    primary_language = StringType(default='Java')


class JavaEar(Package):
    metafiles = ('META-INF/application.xml', 'META-INF/ejb-jar.xml')
    extensions = ('.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='ear')
    primary_language = StringType(default='Java')


class Axis2Mar(Package):
    """Apache Axis2 module"""
    metafiles = ('META-INF/module.xml',)
    extensions = ('.mar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='axis2')
    primary_language = StringType(default='Java')


class JBossSar(Package):
    metafiles = ('META-INF/jboss-service.xml',)
    extensions = ('.sar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='jboss')
    primary_language = StringType(default='Java')


class IvyJar(JavaJar):
    metafiles = ('ivy.xml',)
    type = StringType(default='ivy')
    primary_language = StringType(default='Java')


class BowerPackage(Package):
    metafiles = ('bower.json',)
    type = StringType(default='bower')
    primary_language = StringType(default='JavaScript')

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


class MeteorPackage(Package):
    metafiles = ('package.js',)
    type = StringType(default='meteor')
    primary_language = StringType(default='JavaScript')

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


class CpanModule(Package):
    metafiles = ('*.pod', '*.pm', 'MANIFEST', 'Makefile.PL', 'META.yml', 'META.json', '*.meta', 'dist.ini')
    # TODO: refine me
    extensions = ('.tar.gz',)
    type = StringType(default='cpan')
    primary_language = StringType(default='Perl')


# TODO: refine me: Go packages are a mess but something is emerging
# TODO: move to and use godeps.py
class Godep(Package):
    metafiles = ('Godeps',)
    type = StringType(default='go')
    primary_language = StringType(default='Go')

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


class RubyGem(Package):
    metafiles = ('*.control', '*.gemspec', 'Gemfile', 'Gemfile.lock',)
    filetypes = ('.tar', 'tar archive',)
    mimetypes = ('application/x-tar',)
    extensions = ('.gem',)
    type = StringType(default='gem')
    primary_language = StringType(default='gem')

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


class AndroidApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)
    type = StringType(default='android')
    primary_language = StringType(default='Java')


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
class AndroidLibrary(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this could be decided based on internal structure
    extensions = ('.aar',)
    type = StringType(default='android-lib')
    primary_language = StringType(default='Java')


class MozillaExtension(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)
    type = StringType(default='mozilla')
    primary_language = StringType(default='JavaScript')


class ChromeExtension(Package):
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)
    type = StringType(default='chrome')
    primary_language = StringType(default='JavaScript')


class IOSApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)
    type = StringType(default='ios')
    primary_language = StringType(default='Objective-C')


class CabPackage(Package):
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)
    type = StringType(default='cab')


class MsiInstallerPackage(Package):
    filetypes = ('msi installer',)
    mimetypes = ('application/x-msi',)
    extensions = ('.msi',)
    type = StringType(default='msi')


class InstallShieldPackage(Package):
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    type = StringType(default='installshield')


class NSISInstallerPackage(Package):
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    type = StringType(default='nsis')


class SharPackage(Package):
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin',)
    type = StringType(default='shar')


class AppleDmgPackage(Package):
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)
    type = StringType(default='dmg')


class IsoImagePackage(Package):
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img',)
    type = StringType(default='iso')


class SquashfsPackage(Package):
    filetypes = ('squashfs',)
    type = StringType(default='squashfs')

#
# these very generic archive packages must come last in recogniztion order
#


class RarPackage(Package):
    filetypes = ('rar archive',)
    mimetypes = ('application/x-rar',)
    extensions = ('.rar',)
    type = StringType(default='rar')


class TarPackage(Package):
    filetypes = (
        '.tar', 'tar archive',
        'xz compressed', 'lzma compressed',
        'gzip compressed',
        'bzip2 compressed',
        '7-zip archive',
        "compress'd data",
    )
    mimetypes = (
        'application/x-xz',
        'application/x-tar',
        'application/x-lzma',
        'application/x-gzip',
        'application/x-bzip2',
        'application/x-7z-compressed',
        'application/x-compress',
    )
    extensions = (
        '.tar', '.tar.xz', '.txz', '.tarxz',
        'tar.lzma', '.tlz', '.tarlz', '.tarlzma',
        '.tgz', '.tar.gz', '.tar.gzip', '.targz', '.targzip', '.tgzip',
        '.tar.bz2', '.tar.bz', '.tar.bzip', '.tar.bzip2', '.tbz',
        '.tbz2', '.tb2', '.tarbz2',
        '.tar.7z', '.tar.7zip', '.t7z',
        '.tz', '.tar.z', '.tarz',
    )
    type = StringType(default='tarball')


class PlainZipPackage(Package):
    filetypes = ('zip archive', '7-zip archive',)
    mimetypes = ('application/zip', 'application/x-7z-compressed',)
    extensions = ('.zip', '.zipx', '.7z',)
    type = StringType(default='zip')

# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
