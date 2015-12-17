from __future__ import print_function

import sys
import os
import os.path
import shutil
import fnmatch
import copy
import re
import subprocess

import SCons.Script

def Die(env, fmt, *args):
    print('error: ' + (fmt % args).strip() + '\n', file=sys.stderr)
    SCons.Script.Exit(1)

def RecursiveGlob(env, dirs, patterns, exclude=[]):
    if not isinstance(dirs, list):
        dirs = [dirs]

    if not isinstance(patterns, list):
        patterns = [patterns]

    if not isinstance(exclude, list):
        exclude = [exclude]

    matches = []

    for pattern in patterns:
        for root in dirs:
            for root, dirnames, filenames in os.walk(env.Dir(root).srcnode().abspath):
                for filename in fnmatch.filter(filenames, pattern):
                    cwd = env.Dir('.').srcnode().abspath

                    abspath = os.path.join(root, filename)
                    relpath = os.path.relpath(abspath, cwd)

                    for ex in exclude:
                        if fnmatch.fnmatch(relpath, ex):
                            break
                        if fnmatch.fnmatch(os.path.basename(relpath), ex):
                            break
                    else:
                        matches.append(env.File(relpath))

    return matches

def Which(env, prog):
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, prog)
        if os.access(p, os.X_OK):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, os.X_OK):
                result.append(pext)
    return result

def Python(env):
    base = os.path.basename(sys.executable)
    path = env.Which(base)
    if path and path[0] == sys.executable:
        return base
    else:
        return sys.executable

def CompilerVersion(env, compiler):
    proc = subprocess.Popen([compiler, '--version'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    line = proc.stdout.readline()
    m = re.search('([0-9]\.[0-9.]+)', line)
    if not m:
        return (0)
    return tuple(map(int, m.group(1).split('.')))

def ClangDB(env, build_dir, pattern, compiler):
    return '%s %s/wrappers/clangdb.py %s %s "%s" %s' % (
        env.Python(),
        env.Dir(os.path.dirname(__file__)).path,
        env.Dir('#').path,
        env.Dir(build_dir).path,
        pattern,
        compiler)

def Doxygen(env, output_dir, sources):
    target = os.path.join(env.Dir(output_dir).path, '.done')

    if 'DOXYGEN' in env.Dictionary():
        doxygen = env['DOXYGEN']
    else:
        doxygen = 'doxygen'

    if not env.Which(doxygen):
        env.Die("doxygen not found in PATH (looked for `%s')" % doxygen)

    env.Command(target, sources, SCons.Action.CommandAction(
        '%s %s/wrappers/doxygen.py %s %s %s %s' % (
            env.Python(),
            env.Dir(os.path.dirname(__file__)).path,
            env.Dir('#').path,
            output_dir,
            target,
            doxygen),
        cmdstr = env.Pretty('DOXYGEN', output_dir, 'purple')))

    return target

def GenGetOpt(env, source, ver):
    if 'GENGETOPT' in env.Dictionary():
        gengetopt = env['GENGETOPT']
    else:
        gengetopt = 'gengetopt'

    if not env.Which(gengetopt):
        env.Die("gengetopt not found in PATH (looked for `%s')" % gengetopt)

    source = env.File(source)
    source_name = os.path.splitext(os.path.basename(source.path))[0]
    target = [
        os.path.join(str(source.dir), source_name + '.c'),
        os.path.join(str(source.dir), source_name + '.h'),
    ]

    env.Command(target, source, SCons.Action.CommandAction(
        '%s -F %s --output-dir=%s --set-version=%s < %s' % (
            gengetopt,
            source_name,
            os.path.dirname(source.path),
            ver,
            source.srcnode().path),
        cmdstr = env.Pretty('GGO', '$SOURCE', 'purple')))

    return [env.Object(target[0])]

def ThridParty(env, toolchain, name, includes=[]):
    if not os.path.exists('3rdparty/%s.done' % name):
        if env.IsPretty():
            suffix = '>build.log 2>&1'
        else:
            suffix = ''
        if env.Execute(
            SCons.Action.CommandAction(
                '%s scripts/3rdparty.py 3rdparty "%s" %s%s' % (
                    env.Python(),
                    toolchain,
                    name,
                    suffix),
                cmdstr = env.Pretty('MAKE', name, 'yellow'))):
            env.Die("can't make `%s', see `build.log' for details", name)

    if not includes:
        includes = ['']

    for s in includes:
        env.Prepend(CPPPATH=[
            '3rdparty/%s/include/%s' % (name, s)
        ])

    for lib in env.RecursiveGlob('3rdparty/%s/lib' % name, 'lib*'):
        env.Append(LIBS=[env.File(lib)])

def DeleteDir(env, path):
    path = env.Dir(path).path
    def remove(*args, **kw):
        if os.path.exists(path):
            shutil.rmtree(path)
    return env.Action(remove, env.Pretty('RM', path, 'red'))

def TryParseConfig(env, cmd):
    if 'PKG_CONFIG' in env.Dictionary():
        pkg_config = env['PKG_CONFIG']
    elif env.Which('pkg-config'):
        pkg_config = 'pkg-config'
    else:
        return False

    try:
        env.ParseConfig('%s %s' % (pkg_config, cmd))
        return True
    except:
        return False

def CheckLibWithHeaderExpr(context, libs, headers, language, expr):
    if not isinstance(libs, list):
        libs = [libs]

    if not isinstance(headers, list):
        headers = [headers]

    suffix = '.%s' % language
    includes = '\n'.join(['#include <%s>' % h for h in ['stdio.h'] + headers])
    src = """
%s

int main() {
    printf("%%d\\n", (int)(%s));
    return 0;
}
""" % (includes, expr)

    context.Message("Checking for %s library %s... " % (
        language.upper(), libs[0]))

    err, out = context.RunProg(src, suffix)

    if not err and out.strip() != '0':
        context.Result('yes')
        return True
    else:
        context.Result('no')
        return False

def Init(env):
    env.AddMethod(Die, 'Die')
    env.AddMethod(RecursiveGlob, 'RecursiveGlob')
    env.AddMethod(Which, 'Which')
    env.AddMethod(Python, 'Python')
    env.AddMethod(CompilerVersion, 'CompilerVersion')
    env.AddMethod(ClangDB, 'ClangDB')
    env.AddMethod(Doxygen, 'Doxygen')
    env.AddMethod(GenGetOpt, 'GenGetOpt')
    env.AddMethod(ThridParty, 'ThridParty')
    env.AddMethod(DeleteDir, 'DeleteDir')
    env.AddMethod(TryParseConfig, 'TryParseConfig')
    env.CustomTests = {
        'CheckLibWithHeaderExpr': CheckLibWithHeaderExpr,
    }
