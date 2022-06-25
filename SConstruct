import SCons
import os
import os.path
import platform
import re
import sys

# supported platform names
supported_platforms = [
    'linux',
    'unix',
    'darwin',
    'android',
]

# supported compiler names (without version)
supported_compilers = [
    'clang',
    'gcc',
    'cc',
]

# supported sanitizers
supported_sanitizers = [
    'undefined',
    'address',
]

# default installation prefix
default_prefix = '/usr/local'

AddOption('--prefix',
          dest='prefix',
          action='store',
          type='string',
          default=default_prefix,
          help="installation prefix, '%s' by default" % default_prefix)

AddOption('--bindir',
          dest='bindir',
          action='store',
          type='string',
          default=os.path.join(GetOption('prefix'), 'bin'),
          help=("path to the binary installation directory (where to "+
                "install Roc command-line tools), '<prefix>/bin' by default"))

AddOption('--libdir',
          dest='libdir',
          action='store',
          type='string',
          help=("path to the library installation directory (where to "+
                "install Roc library), auto-detect if empty"))

AddOption('--incdir',
          dest='incdir',
          action='store',
          type='string',
          default=os.path.join(GetOption('prefix'), 'include'),
          help=("path to the headers installation directory (where to "+
                "install Roc headers), '<prefix>/include' by default"))

AddOption('--mandir',
          dest='mandir',
          action='store',
          type='string',
          default=os.path.join(GetOption('prefix'), 'share/man/man1'),
          help=("path to the manuals installation directory (where to "+
                "install Roc manual pages), '<prefix>/share/man/man1' by default"))

AddOption('--build',
          dest='build',
          action='store',
          type='string',
          help=("system name where Roc is being compiled, "+
                "e.g. 'x86_64-pc-linux-gnu', "+
                "auto-detect if empty"))

AddOption('--host',
          dest='host',
          action='store',
          type='string',
          help=("system name where Roc will run, "+
                "e.g. 'arm-linux-gnueabihf', "+
                "auto-detect if empty"))

AddOption('--platform',
          dest='platform',
          action='store',
          choices=([''] + supported_platforms),
          help=("platform name where Roc will run, "+
            "supported values: empty (detect from host), %s" % (
              ', '.join(["'%s'" % s for s in supported_platforms]))))

AddOption('--compiler',
          dest='compiler',
          action='store',
          type='string',
          help=("compiler name and optional version, e.g. 'gcc-4.9', "+
            "supported names: empty (detect what available), %s" % (
              ', '.join(["'%s'" % s for s in supported_compilers]))))

AddOption('--sanitizers',
          dest='sanitizers',
          action='store',
          type='string',
          help="list of gcc/clang sanitizers, "+
          "supported names: empty (no sanitizers), 'all', "+
          ', '.join(["'%s'" % s for s in supported_sanitizers]))

AddOption('--enable-debug',
          dest='enable_debug',
          action='store_true',
          help='enable debug build for Roc')

AddOption('--enable-debug-3rdparty',
          dest='enable_debug_3rdparty',
          action='store_true',
          help='enable debug build for 3rdparty libraries')

AddOption('--enable-werror',
          dest='enable_werror',
          action='store_true',
          help='treat warnings as errors')

AddOption('--enable-static',
          dest='enable_static',
          action='store_true',
          help='enable building static library')

AddOption('--disable-shared',
          dest='disable_shared',
          action='store_true',
          help='disable building shared library')

AddOption('--disable-tools',
          dest='disable_tools',
          action='store_true',
          help='disable tools building')

AddOption('--enable-tests',
          dest='enable_tests',
          action='store_true',
          help='enable tests building and running (requires CppUTest)')

AddOption('--enable-benchmarks',
          dest='enable_benchmarks',
          action='store_true',
          help='enable bechmarks building and running (requires Google Benchmark)')

AddOption('--enable-examples',
          dest='enable_examples',
          action='store_true',
          help='enable examples building')

AddOption('--enable-doxygen',
          dest='enable_doxygen',
          action='store_true',
          help='enable Doxygen documentation generation')

AddOption('--enable-sphinx',
          dest='enable_sphinx',
          action='store_true',
          help='enable Sphinx documentation generation')

AddOption('--disable-c11',
          dest='disable_c11',
          action='store_true',
          help='disable C11 support')

AddOption('--disable-soversion',
          dest='disable_soversion',
          action='store_true',
          help="don't write version into the shared library"+
              " and don't create version symlinks")

AddOption('--disable-openfec',
          dest='disable_openfec',
          action='store_true',
          help='disable OpenFEC support required for FEC codes')

AddOption('--disable-speexdsp',
          dest='disable_speexdsp',
          action='store_true',
          help='disable SpeexDSP support for resampling')

AddOption('--disable-sox',
          dest='disable_sox',
          action='store_true',
          help='disable SoX support in tools')

AddOption('--disable-libunwind',
          dest='disable_libunwind',
          action='store_true',
          help='disable libunwind support required for printing backtrace')

AddOption('--disable-pulseaudio',
          dest='disable_pulseaudio',
          action='store_true',
          help='disable PulseAudio support in tools')

AddOption('--with-openfec-includes',
          dest='with_openfec_includes',
          action='store',
          type='string',
          help=("path to the directory with OpenFEC headers (it should contain "+
                "lib_common and lib_stable subdirectories)"))

AddOption('--with-includes',
          dest='with_includes',
          action='append',
          type='string',
          help=("additional include search path, may be used multiple times"))

AddOption('--with-libraries',
          dest='with_libraries',
          action='append',
          type='string',
          help=("additional library search path, may be used multiple times"))

AddOption('--build-3rdparty',
          dest='build_3rdparty',
          action='store',
          type='string',
          help=("download and build specified 3rdparty libraries, "+
                "pass a comma-separated list of library names and optional versions, "+
                "e.g. 'libuv:1.4.2,openfec'"))

AddOption('--override-targets',
          dest='override_targets',
          action='store',
          type='string',
          help=("override targets to use, "+
                "pass a comma-separated list of target names, "+
                "e.g. 'glibc,stdio,posix,libuv,openfec,...'"))

# configure even in dry run mode
SCons.SConf.dryrun = 0

# when we cross-compile on macOS to Android using clang, we should use
# GNU-like clang options, but SCons incorrectly sets up Apple-like
# clang options; here we prevent this behavior by forcing 'posix' platform
scons_platform = Environment(ENV=os.environ)['PLATFORM']
for opt in ['host', 'platform']:
    if 'android' in (GetOption(opt) or ''):
        scons_platform = 'posix'

env = Environment(
    ENV=os.environ,
    platform=scons_platform,
    toolpath=[os.path.join(Dir('#').abspath, 'scripts')],
    tools=[
        'default',
        'scons_plugin', # our plugin in scripts/
        ])

# performance tuning
env.Decider('MD5-timestamp')
env.SetOption('implicit_cache', 1)

# provide absolute path to force single sconsign file
# per-directory sconsign files seems to be buggy with generated sources
# create separate sconsign file for each python version, since different
# python versions can use different pickle protocols and switching from
# a higher version to a lower one would cause exception
env.SConsignFile(os.path.join(
    env.Dir('#').abspath, '.sconsign%s%s.dblite' % sys.version_info[0:2]))

# we always use -fPIC, so object files built for static and shared
# libraries are no different
env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

for var in ['CXX', 'CC', 'LD', 'AR', 'RANLIB', 'INSTALL_NAME_TOOL',
            'RAGEL', 'GENGETOPT',
            'PKG_CONFIG', 'PKG_CONFIG_PATH', 'CONFIG_GUESS',
            'CLANG_FORMAT']:
    env.OverrideFromArgument(var)

env.OverrideFromArgument('CXXLD', names=['CXXLD', 'CXX'])
env.OverrideFromArgument('CCLD', names=['CCLD', 'LD', 'CC'])

env.OverrideFromArgument('STRIP', default='strip')
env.OverrideFromArgument('OBJCOPY', default='objcopy')

env.OverrideFromArgument('DOXYGEN', default='doxygen')
env.OverrideFromArgument('SPHINX_BUILD', default='sphinx-build')
env.OverrideFromArgument('BREATHE_APIDOC', default='breathe-apidoc')

env.PrependFromArgument('CPPFLAGS')
env.PrependFromArgument('CXXFLAGS')
env.PrependFromArgument('CFLAGS')
env.PrependFromArgument('LINKFLAGS', names=['LINKFLAGS', 'LDFLAGS'])
env.PrependFromArgument('STRIPFLAGS')

env.Append(CXXFLAGS=[])
env.Append(CPPDEFINES=[])
env.Append(CPPPATH=[])
env.Append(LIBPATH=[])
env.Append(LIBS=[])
env.Append(RPATH_LINK_DIRS=[])
env.Append(STRIPFLAGS=[])

if GetOption('with_includes'):
    env.Append(CPPPATH=GetOption('with_includes'))

if GetOption('with_libraries'):
    env.Append(LIBPATH=GetOption('with_libraries'))

if GetOption('help'):
    Return()

cleanfiles = [
    env.DeleteFile('#compile_commands.json'),
    env.DeleteFile('#config.log'),
    env.DeleteDir('#.sconf_temp'),
]

for f in env.Glob('.sconsign*.dblite'):
    cleanfiles += [env.DeleteFile(f)]

cleanbuild = [
    env.DeleteDir('#bin'),
    env.DeleteDir('#build/src'),
] + cleanfiles

cleandocs = [
    env.DeleteDir('#build/docs'),
    env.DeleteDir('#docs/html'),
]

cleanall = [
    env.DeleteDir('#bin'),
    env.DeleteDir('#build'),
    env.DeleteDir('#docs/html'),
] + cleanfiles

env.AlwaysBuild(env.Alias('clean', [], cleanall))
env.AlwaysBuild(env.Alias('cleanbuild', [], cleanbuild))
env.AlwaysBuild(env.Alias('cleandocs', [], cleandocs))

if set(COMMAND_LINE_TARGETS).intersection(['clean', 'cleanbuild', 'cleandocs']) or \
  env.GetOption('clean'):
    if set(COMMAND_LINE_TARGETS) - set(['clean', 'cleanbuild', 'cleandocs']):
        env.Die("combining 'clean*' targets with other targets is not allowed")
    if env.GetOption('clean'):
        env.Execute(cleanall)
    Return()

if 'fmt' in COMMAND_LINE_TARGETS:
    conf = Configure(env, custom_tests=env.CustomTests)
    conf.FindClangFormat()
    env = conf.Finish()

    fmt_actions = []

    fmt_actions.append(env.ClangFormat('#src'))

    fmt_actions.append(env.HeaderFormat('#src/internal_modules'))
    fmt_actions.append(env.HeaderFormat('#src/public_api/src'))
    fmt_actions.append(env.HeaderFormat('#src/tests'))
    fmt_actions.append(env.HeaderFormat('#src/tools'))

    env.AlwaysBuild(
        env.Alias('fmt', [], fmt_actions))

# build documentation
doc_env = env.Clone()
doc_env.SConscript('docs/SConscript',
                       duplicate=0, exports='doc_env')

non_build_targets = ['fmt', 'docs', 'shpinx', 'doxygen']
if set(COMMAND_LINE_TARGETS) \
  and set(COMMAND_LINE_TARGETS).intersection(non_build_targets) == set(COMMAND_LINE_TARGETS):
    Return()

# meta-information about the build, used to generate env parameters
meta = type('meta', (), {
    field: '' for field in ('build host toolchain platform variant thirdparty_variant '+
                            'compiler compiler_ver fpic_supporte').split()})

# toolchain triple of the local system (where we're building), e.g. x86_64-pc-linux-gnu
meta.build = GetOption('build')

# toolchain triple of the target system (where we will run), e.g. aarch64-linux-gnu
meta.host = GetOption('host') or ''

# toolchain prefix for compiler, linker, and other tools, e.g. aarch64-linux-gnu
meta.toolchain = GetOption('host') or ''

# name of the target platform, e.g. 'linux'; see supported_platforms
meta.platform = GetOption('platform') or ''

# build variant, i.e. 'debug' or 'release'
meta.variant = 'debug' if GetOption('enable_debug') else 'release'

# build variant for third-parties
meta.thirdparty_variant = 'debug' if GetOption('enable_debug_3rdparty') else 'release'

# compiler name, e.g. 'gcc', and version tuple, e.g. (4, 9)
if GetOption('compiler'):
    meta.compiler = GetOption('compiler')
    if '-' in meta.compiler:
        meta.compiler, meta.compiler_ver = meta.compiler.split('-')
        meta.compiler_ver = tuple(map(int, meta.compiler_ver.split('.')))
else:
    if env.HasArgument('CXX'):
        if 'clang' in env['CXX']:
            meta.compiler = 'clang'
        elif 'gcc' in env['CXX'] or 'g++' in env['CXX']:
            meta.compiler = 'gcc'
        elif os.path.basename(env['CXX']) in ['cc', 'c++']:
            meta.compiler = 'cc'
    elif meta.toolchain:
        if env.Which('%s-clang++' % meta.toolchain):
            meta.compiler = 'clang'
        elif env.Which('%s-g++' % meta.toolchain):
            meta.compiler = 'gcc'
        elif env.Which('%s-c++' % meta.toolchain):
            meta.compiler = 'cc'
    else:
        if env.Which('clang++'):
            meta.compiler = 'clang'
        elif env.Which('g++'):
            meta.compiler = 'gcc'
        elif env.Which('c++'):
            meta.compiler = 'cc'

if not meta.compiler:
    env.Die("can't detect compiler name, please specify '--compiler={name}' manually,"+
            " should be one of: %s'" % ', '.join(supported_compilers))

if not meta.compiler in supported_compilers:
    env.Die("unknown --compiler '%s', expected one of: %s",
            meta.compiler, ', '.join(supported_compilers))

if not meta.compiler_ver:
    if meta.toolchain:
        meta.compiler_ver = env.ParseCompilerVersion('%s-%s' % (meta.toolchain, meta.compiler))
    else:
        meta.compiler_ver = env.ParseCompilerVersion(meta.compiler)

if not meta.compiler_ver:
    if meta.compiler not in ['cc']:
        env.Die("can't detect compiler version for compiler '%s'",
                '-'.join([s for s in [meta.toolchain, meta.compiler] if s]))

conf = Configure(env, custom_tests=env.CustomTests)

if meta.compiler == 'clang':
    conf.FindLLVMDir(meta.compiler_ver)

if meta.compiler == 'clang':
    conf.FindTool('CXX', [meta.toolchain], [('clang++', meta.compiler_ver)])
elif meta.compiler == 'gcc':
    conf.FindTool('CXX', [meta.toolchain], [('g++', meta.compiler_ver)])
elif meta.compiler == 'cc':
    conf.FindTool('CXX', [meta.toolchain], [('c++', meta.compiler_ver)])

full_compiler_ver = env.ParseCompilerVersion(conf.env['CXX'])
if full_compiler_ver:
    meta.compiler_ver = full_compiler_ver

if not meta.build:
    for local_compiler in ['/usr/bin/gcc', '/usr/bin/clang']:
        meta.build = env.ParseCompilerTarget(local_compiler)
        if meta.build:
            break

if not meta.build and not meta.host:
    if conf.CheckCanRunProgs():
        meta.build = env.ParseCompilerTarget(conf.env['CXX'])

if not meta.build:
    if conf.FindConfigGuess():
        meta.build = env.ParseConfigGuess(conf.env['CONFIG_GUESS'])

if not meta.build:
    env.Die(("can't detect system type, please specify '--build={type}' manually, "+
             "e.g. '--build=x86_64-pc-linux-gnu'"))

if not meta.host:
    meta.host = env.ParseCompilerTarget(conf.env['CXX'])

if not meta.host:
    meta.host = meta.build

if not meta.toolchain and meta.build != meta.host:
    meta.toolchain = meta.host

if not meta.platform:
    if 'android' in meta.host:
        meta.platform = 'android'
    elif 'linux' in meta.host:
        meta.platform = 'linux'
    elif 'darwin' in meta.host:
        meta.platform = 'darwin'

if not meta.platform and meta.host == meta.build:
    if os.name == 'posix':
        meta.platform = 'unix'

if not meta.platform:
    env.Die("can't detect platform name, please specify '--platform={name}' manually,"+
            " should be one of: %s'" % ', '.join(supported_platforms))

if meta.platform not in supported_platforms:
    env.Die(("unknown --platform '%s', expected on of: %s"),
                meta.platform, ', '.join(supported_platforms))

allowed_toolchains = [meta.toolchain]
if meta.toolchain != '' and meta.build == meta.host:
    allowed_toolchains += ['']

if meta.compiler == 'clang':
    conf.FindTool('CXX', allowed_toolchains, [('clang++', meta.compiler_ver)])
    conf.FindTool('CC', allowed_toolchains, [('clang', meta.compiler_ver)])
    conf.FindTool('CXXLD', allowed_toolchains, [('clang++', meta.compiler_ver)])
    conf.FindTool('CCLD', allowed_toolchains, [('clang', meta.compiler_ver)])
    conf.FindTool('LD', allowed_toolchains, [('ld', None)], required=False)

    compiler_dir = env.ParseCompilerDirectory(conf.env['CXX'])
    if compiler_dir:
        prepend_path = [compiler_dir]
    else:
        prepend_path = []

    conf.FindTool('AR', allowed_toolchains,
                  [('llvm-ar', meta.compiler_ver), ('llvm-ar', None), ('ar', None)],
                  prepend_path=prepend_path)

    conf.FindTool('RANLIB', allowed_toolchains,
                  [('llvm-ranlib', meta.compiler_ver), ('llvm-ranlib', None), ('ranlib', None)],
                  prepend_path=prepend_path)

    conf.FindTool('STRIP', allowed_toolchains,
                  [('llvm-strip', meta.compiler_ver), ('llvm-strip', None), ('strip', None)],
                  prepend_path=prepend_path)

    conf.FindTool('OBJCOPY', allowed_toolchains,
                  [('llvm-objcopy', meta.compiler_ver),
                   ('llvm-objcopy', None),
                   ('objcopy', None)],
                  prepend_path=prepend_path,
                  required=False)

elif meta.compiler == 'gcc':
    conf.FindTool('CXX', allowed_toolchains, [('g++', meta.compiler_ver)])
    conf.FindTool('CC', allowed_toolchains, [('gcc', meta.compiler_ver)])
    conf.FindTool('CXXLD', allowed_toolchains, [('g++', meta.compiler_ver)])
    conf.FindTool('CCLD', allowed_toolchains, [('gcc', meta.compiler_ver)])
    conf.FindTool('LD', allowed_toolchains, [('ld', None)], required=False)
    conf.FindTool('AR', allowed_toolchains, [('ar', None)])
    conf.FindTool('RANLIB', allowed_toolchains, [('ranlib', None)])
    conf.FindTool('STRIP', allowed_toolchains, [('strip', None)])
    conf.FindTool('OBJCOPY', allowed_toolchains, [('objcopy', None)], required=False)

elif meta.compiler == 'cc':
    conf.FindTool('CXX', allowed_toolchains, [('c++', meta.compiler_ver)])
    conf.FindTool('CC', allowed_toolchains, [('cc', meta.compiler_ver)])
    conf.FindTool('CXXLD', allowed_toolchains, [('c++', meta.compiler_ver)])
    conf.FindTool('CCLD', allowed_toolchains, [('cc', meta.compiler_ver)])
    conf.FindTool('AR', allowed_toolchains, [('ar', None)])
    conf.FindTool('RANLIB', allowed_toolchains, [('ranlib', None)])
    conf.FindTool('STRIP', allowed_toolchains, [('strip', None)])

conf.env['LINK'] = env['CXXLD']
conf.env['SHLINK'] = env['CXXLD']

if meta.platform == 'darwin':
    conf.FindTool('INSTALL_NAME_TOOL', [''], [('install_name_tool', None)], required=False)

if meta.compiler in ['gcc', 'clang']:
    meta.fpic_supported = True
else:
    meta.fpic_supported = conf.CheckCompilerOptionSupported('-fPIC', 'cxx')

conf.env['ROC_SYSTEM_BINDIR'] = GetOption('bindir')
conf.env['ROC_SYSTEM_INCDIR'] = GetOption('incdir')

if GetOption('libdir'):
    conf.env['ROC_SYSTEM_LIBDIR'] = GetOption('libdir')
else:
    conf.FindLibDir(GetOption('prefix'), meta.host)

conf.FindPkgConfig(meta.toolchain)
conf.FindPkgConfigPath(GetOption('prefix'))

env = conf.Finish()

env['ROC_BINDIR'] = '#bin/%s' % meta.host

env['ROC_BUILDDIR'] = '#build/src/%s/%s' % (
    meta.host,
    '-'.join(
        [s for s in [
            meta.compiler,
            '.'.join(map(str, meta.compiler_ver)) if meta.compiler_ver else '',
            meta.variant
        ] if s])
    )

env['ROC_THIRDPARTY_BUILDDIR'] = '#build/3rdparty/%s/%s' % (
    meta.host,
    '-'.join(
        [s for s in [
            meta.compiler,
            '.'.join(map(str, meta.compiler_ver)) if meta.compiler_ver else '',
            meta.thirdparty_variant
        ] if s])
    )

env['ROC_VERSION'] = env.ParseProjectVersion('src/public_api/include/roc/version.h')
env['ROC_COMMIT'] = env.ParseGitHead()

env['ROC_SOVER'] = '.'.join(env['ROC_VERSION'].split('.')[:2])

env['ROC_MODULES'] = [
    'roc_core',
    'roc_error',
    'roc_address',
    'roc_packet',
    'roc_audio',
    'roc_rtp',
    'roc_fec',
    'roc_netio',
    'roc_sndio',
    'roc_pipeline',
    'roc_sdp',
    'roc_ctl',
    'roc_peer',
]

env['ROC_TARGETS'] = []

if GetOption('override_targets'):
    for t in GetOption('override_targets').split(','):
        env['ROC_TARGETS'] += ['target_%s' % t]
else:
    has_c11 = False
    if not GetOption('disable_c11'):
        if meta.compiler == 'gcc':
            has_c11 = meta.compiler_ver[:2] >= (4, 9)
        elif meta.compiler == 'clang':
            if meta.platform == 'darwin':
                has_c11 = meta.compiler_ver[:2] >= (7, 0)
            else:
                has_c11 = meta.compiler_ver[:2] >= (3, 6)

    if has_c11:
        env.Append(ROC_TARGETS=[
            'target_c11',
        ])
    else:
        env.Append(ROC_TARGETS=[
            'target_libatomic_ops',
        ])

    env.Append(ROC_TARGETS=[
        'target_stdio',
    ])

    if meta.platform in ['linux', 'unix', 'android', 'darwin']:
        env.Append(ROC_TARGETS=[
            'target_posix',
        ])

    if meta.platform in ['linux', 'unix', 'android']:
        env.Append(ROC_TARGETS=[
            'target_posix_ext',
        ])

    if meta.platform in ['android']:
        env.Append(ROC_TARGETS=[
            'target_bionic',
        ])

    if meta.platform in ['darwin']:
        env.Append(ROC_TARGETS=[
            'target_darwin',
        ])

    if meta.platform in ['linux', 'unix', 'darwin'] and not GetOption('disable_libunwind'):
        env.Append(ROC_TARGETS=[
            'target_libunwind',
        ])
    elif meta.platform in ['android']:
        pass
    else:
        env.Append(ROC_TARGETS=[
            'target_nobacktrace',
        ])

    is_gnulike_libc = False
    if meta.platform in ['linux', 'unix']:
        is_gnulike_libc = 'gnu' in meta.host
    elif meta.platform in ['android', 'darwin']:
        is_gnulike_libc = True

    if is_gnulike_libc and not GetOption('disable_libunwind'):
        env.Append(ROC_TARGETS=[
            'target_cxxabi',
        ])
    else:
        env.Append(ROC_TARGETS=[
            'target_nodemangle',
        ])

    env.Append(ROC_TARGETS=[
        'target_libuv',
    ])

    if not GetOption('disable_openfec'):
        env.Append(ROC_TARGETS=[
            'target_openfec',
        ])

    if not GetOption('disable_speexdsp'):
        env.Append(ROC_TARGETS=[
            'target_speexdsp',
        ])

    if not GetOption('disable_tools'):
        if not GetOption('disable_sox'):
            env.Append(ROC_TARGETS=[
                'target_sox',
            ])
        if not GetOption('disable_pulseaudio') and meta.platform in ['linux']:
            env.Append(ROC_TARGETS=[
                'target_pulseaudio',
            ])

# env will hold settings common to all code
# subenvs will hold settings specific to particular parts of code
subenv_names = 'internal_modules public_libs examples tools tests generated_code'.split()

subenv_attrs = {field: env.Clone() for field in subenv_names}
subenv_attrs['all'] = list(subenv_attrs.values())

subenvs = type('subenvs', (), subenv_attrs)

# find or build third-party dependencies
env, subenvs = env.SConscript('3rdparty/SConscript',
                       duplicate=0, exports='env subenvs meta')

if 'target_posix' in env['ROC_TARGETS'] and meta.platform not in ['darwin', 'unix']:
    env.Append(CPPDEFINES=[('_POSIX_C_SOURCE', '200809')])

if meta.platform in ['linux', 'unix']:
    env.AddPkgConfigLibs(['rt', 'dl', 'm'])

if meta.compiler in ['gcc', 'clang']:
    if not meta.platform in ['android']:
        env.Append(CXXFLAGS=[
            '-std=c++98',
        ])

    env.Append(CXXFLAGS=[
        '-fno-exceptions',
    ])

    for var in ['CXXFLAGS', 'CFLAGS']:
        env.Append(**{var: [
            '-pthread',
            '-fPIC',
        ]})

    if meta.platform in ['linux', 'darwin']:
        env.AddPkgConfigLibs(['pthread'])

    if meta.platform in ['linux', 'android']:
        if not GetOption('disable_soversion'):
            subenvs.public_libs['SHLIBSUFFIX'] = '%s.%s' % (
                subenvs.public_libs['SHLIBSUFFIX'], env['ROC_SOVER'])

        subenvs.public_libs.Append(LINKFLAGS=[
            '-Wl,-soname,libroc%s' % subenvs.public_libs['SHLIBSUFFIX'],
        ])

        if meta.variant == 'release':
            subenvs.public_libs.Append(LINKFLAGS=[
                '-Wl,--version-script=%s' % env.File('#src/public_api/roc.version').path
            ])

    if meta.platform in ['darwin']:
        if not GetOption('disable_soversion'):
            subenvs.public_libs['SHLIBSUFFIX'] = '.%s%s' % (
                env['ROC_SOVER'], subenvs.public_libs['SHLIBSUFFIX'])

            subenvs.public_libs.Append(LINKFLAGS=[
                '-Wl,-compatibility_version,%s' % env['ROC_SOVER'],
                '-Wl,-current_version,%s' % env['ROC_VERSION'],
            ])

        subenvs.public_libs.Append(LINKFLAGS=[
            '-Wl,-install_name,%s/libroc%s' % (
                env.Dir(env['ROC_BINDIR']).abspath, subenvs.public_libs['SHLIBSUFFIX']),
        ])

    if not(meta.compiler == 'clang' and meta.variant == 'debug'):
        env.Append(CXXFLAGS=[
            '-fno-rtti',
        ])

    if meta.variant == 'debug':
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-ggdb',
                '-funwind-tables',
                '-fno-omit-frame-pointer',
            ]})
        env.Append(LINKFLAGS=[
            '-rdynamic'
        ])
    else:
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-fvisibility=hidden',
                '-O3',
            ]})

    if meta.compiler == 'gcc' and meta.compiler_ver[:2] < (4, 6):
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-fno-strict-aliasing',
            ]})

if meta.compiler in ['cc']:
    env.AddPkgConfigLibs(['pthread'])

    if meta.variant == 'debug':
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-g',
            ]})
    else:
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-O3',
            ]})

    if meta.fpic_supported:
        for var in ['CXXFLAGS', 'CFLAGS']:
            conf.env.Append(**{var: [
                '-fPIC',
            ]})

if meta.compiler in ['gcc', 'clang']:
    if GetOption('enable_werror'):
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-Werror',
            ]})

if meta.compiler == 'gcc':
    for var in ['CXXFLAGS', 'CFLAGS']:
        env.Append(**{var: [
            '-Wall',
            '-Wextra',
            '-Wcast-qual',
            '-Wfloat-equal',
            '-Wpointer-arith',
            '-Wformat=2',
            '-Wformat-security',
            '-Wno-system-headers',
            '-Wno-psabi',
        ]})

    env.Append(CXXFLAGS=[
        '-Wctor-dtor-privacy',
        '-Wnon-virtual-dtor',
        '-Wstrict-null-sentinel',
        '-Wno-invalid-offsetof',
    ])

    if meta.compiler_ver[:2] >= (4, 4):
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-Wlogical-op',
                '-Woverlength-strings',
            ]})
        env.Append(CXXFLAGS=[
            '-Wmissing-declarations',
        ])

    if meta.compiler_ver[:2] >= (4, 8):
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-Wdouble-promotion',
            ]})

    if meta.compiler_ver[:2] >= (8, 0):
        for var in ['CXXFLAGS', 'CFLAGS']:
            env.Append(**{var: [
                '-Wno-parentheses',
                '-Wno-cast-function-type',
            ]})

if meta.compiler == 'clang':
    for var in ['CXXFLAGS', 'CFLAGS']:
        env.Append(**{var: [
            '-Weverything',
            '-Wno-system-headers',
            '-Wno-old-style-cast',
            '-Wno-padded',
            '-Wno-packed',
            '-Wno-cast-align',
            '-Wno-global-constructors',
            '-Wno-exit-time-destructors',
            '-Wno-invalid-offsetof',
            '-Wno-shift-sign-overflow',
            '-Wno-used-but-marked-unused',
            '-Wno-unused-macros',
            '-Wno-format-nonliteral',
            '-Wno-variadic-macros',
            '-Wno-disabled-macro-expansion',
            '-Wno-c++11-long-long',
        ]})

    env.Append(CFLAGS=[
        '-Wno-missing-prototypes',
    ])

    if meta.platform in ['linux', 'android']:
        if meta.compiler_ver[:2] >= (3, 4) and meta.compiler_ver[:2] < (3, 6):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-unreachable-code',
                ]})
        if meta.compiler_ver[:2] >= (3, 6):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-reserved-id-macro',
                    '-Wno-unreachable-code-break',
                ]})
        if meta.compiler_ver[:2] >= (6, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-redundant-parens',
                    '-Wno-zero-as-null-pointer-constant',
                ]})
        if meta.compiler_ver[:2] >= (8, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-atomic-implicit-seq-cst',
                    '-Wno-extra-semi-stmt',
                ]})
        if meta.compiler_ver[:2] >= (10, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-anon-enum-enum-conversion',
                    '-Wno-implicit-int-float-conversion',
                    '-Wno-enum-float-conversion',
                ]})
        if meta.compiler_ver[:2] >= (11, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-suggest-override',
                    '-Wno-suggest-destructor-override',
                ]})

    if meta.platform == 'darwin':
        if meta.compiler_ver[:2] >= (10, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-redundant-parens',
                ]})
        if meta.compiler_ver[:2] >= (11, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-atomic-implicit-seq-cst',
                ]})
        if meta.compiler_ver[:2] >= (12, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-poison-system-directories',
                    '-Wno-anon-enum-enum-conversion',
                ]})
        if meta.compiler_ver[:3] >= (12, 0, 5):
            for var in ['CXXFLAGS', 'CFLAGS']:
                env.Append(**{var: [
                    '-Wno-suggest-override',
                    '-Wno-suggest-destructor-override',
                ]})

    if meta.platform == 'android':
        env.Append(CXXFLAGS=[
            '-Wno-unknown-warning-option',
            '-Wno-c++98-compat-pedantic',
            '-Wno-deprecated-dynamic-exception-spec',
        ])

if meta.compiler == 'clang':
    subenvs.tests.AppendUnique(CXXFLAGS=[
        '-Wno-weak-vtables',
        '-Wno-unused-member-function',
    ])

    if meta.platform in ['linux', 'android']:
        if meta.compiler_ver[:2] >= (5, 0):
            for var in ['CXXFLAGS', 'CFLAGS']:
                subenvs.tests.AppendUnique(**{var: [
                    '-Wno-unused-template',
                ]})

    if meta.platform == 'darwin':
        if meta.compiler_ver[:2] >= (9, 1):
            for var in ['CXXFLAGS', 'CFLAGS']:
                subenvs.tests.AppendUnique(**{var: [
                    '-Wno-unused-template',
                ]})

if meta.compiler in ['gcc', 'clang']:
    for var in ['CXXFLAGS', 'CFLAGS']:
        subenvs.generated_code.AppendUnique(**{var: [
            '-w',
        ]})

sanitizers = env.ParseList(GetOption('sanitizers'), supported_sanitizers)
if sanitizers:
    if not meta.compiler in ['gcc', 'clang']:
        env.Die("sanitizers are not supported for compiler '%s'" % meta.compiler)

    for name in sanitizers:
        flags = ['-fsanitize=%s' % name, '-fno-sanitize-recover=%s' % name]
        env.AppendUnique(CFLAGS=flags)
        env.AppendUnique(CXXFLAGS=flags)
        env.AppendUnique(LINKFLAGS=flags)
else:
    if meta.platform in ['linux', 'android']:
        env.Append(LINKFLAGS=[
            '-Wl,--no-undefined',
        ])

if meta.platform in ['linux']:
    for path in env['RPATH_LINK_DIRS']:
        env.Append(LINKFLAGS=[
            '-Wl,-rpath-link,%s' % env.Dir(path).path,
        ])

subenvs.tests.Append(
    CPPDEFINES=('CPPUTEST_USE_MEM_LEAK_DETECTION', '0')
    )

if meta.platform in ['darwin']:
    if not env['STRIPFLAGS']:
        env.Append(STRIPFLAGS=['-x'])

env.Append(CPPPATH=['%s/tools' % env['ROC_BUILDDIR']])
env.Append(LIBPATH=['%s' % env['ROC_BUILDDIR']])

# both env and subenvs have been modified after subenvs were cloned from env
# here we propagate modifications from env to all subenvs
for senv in subenvs.all:
    senv.AppendEnvUnique(env)

# enable generation of compile_commands.json (a.k.a. clangdb)
if meta.compiler in ['gcc', 'clang']:
    for senv in subenvs.all:
        for var in ['CC', 'CXX']:
            senv[var] = env.GetClangDbWriter(senv[var], env['ROC_BUILDDIR'])

    compile_commands = '%s/compile_commands.json' % env['ROC_BUILDDIR']

    env.Artifact(compile_commands, '#src')
    env.Install('#', compile_commands)

# post-process paths after merging environments
if meta.compiler in ['gcc', 'clang']:
    for senv in subenvs.all:
        for var in ['CXXFLAGS', 'CFLAGS']:
            dirs = [('-isystem', senv.Dir(path).path) for path in senv['CPPPATH']]

            # workaround to force our 3rdparty directories to be placed
            # before /usr/local/include on macos: explicitly place it
            # after previous -isystem options
            if meta.compiler == 'clang' and meta.platform == 'darwin':
                dirs += [('-isystem', '/usr/local/include')]

            senv.Prepend(**{var: dirs})

        # workaround for "skipping incompatible" linker warning
        if '/usr/lib64' in senv.ParseLinkDirs(senv['CXXLD']):
            senv.Prepend(LINKFLAGS=['-L/usr/lib64'])

# finally build the project
env.SConscript('src/SConscript',
            variant_dir=env['ROC_BUILDDIR'], duplicate=0, exports='env subenvs')
