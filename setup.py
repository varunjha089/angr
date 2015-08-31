import os
import shutil
import subprocess
from distutils.errors import LibError
from distutils.core import setup
from distutils.command.build import build as _build

QEMU_REPO_PATH_CGC = "tracer-qemu-cgc"
QEMU_PATH_CGC = os.path.join("bin", "tracer-qemu-cgc")

QEMU_REPO_PATH_LINUX = "tracer-qemu-linux"
QEMU_PATH_LINUX_I386 = os.path.join("bin", "tracer-qemu-linux-i386")
QEMU_PATH_LINUX_X86_64 = os.path.join("bin", "tracer-qemu-linux-x86_64")
QEMU_LINUX_TRACER_PATCH = os.path.join("..", "patches", "tracer-qemu.patch")

BIN_PATH = "bin"

# grab the CGC repo
if not os.path.exists(QEMU_REPO_PATH_CGC):
    TRACER_QEMU_REPO_CGC = "git@git.seclab.cs.ucsb.edu:cgc/qemu.git"
    if subprocess.call(['git', 'clone', TRACER_QEMU_REPO_CGC, QEMU_REPO_PATH_CGC]) != 0:
        raise LibError("Unable to retrieve tracer qemu")
    if subprocess.call(['git', 'checkout', 'base_tracer'], cwd=QEMU_REPO_PATH_CGC) != 0:
        raise LibError("Unable to checkout tracer branch")

# grab the linux tarball
if not os.path.exists(QEMU_REPO_PATH_LINUX):
    TRACER_QEMU_REPO_LINUX = "git://git.qemu.org/qemu.git"
    if subprocess.call(['git', 'clone', TRACER_QEMU_REPO_LINUX, QEMU_REPO_PATH_LINUX]) != 0:
        raise LibError("Unable to retrieve qemu repository \"%s\"" % TRACER_QEMU_REPO_LINUX)
    if subprocess.call(['git', '-C', QEMU_REPO_PATH_LINUX, 'checkout', 'tags/v2.3.0']) != 0:
        raise LibError("Unable to checkout version 2.3.0 of qemu")
    if subprocess.call(['git', '-C', QEMU_REPO_PATH_LINUX, 'apply', QEMU_LINUX_TRACER_PATCH]) != 0:
        raise LibError("Unable to apply tracer patch to qemu")

# update tracer qemu for cgc
if subprocess.call(['git', 'pull'], cwd=QEMU_REPO_PATH_CGC) != 0:
    raise LibError("Unable to retrieve tracer qemu")

if not os.path.exists(BIN_PATH):
    try:
        os.makedirs(BIN_PATH)
    except OSError:
        raise LibError("Unable to create bin directory")

def _build_qemus():
    if subprocess.call(['./tracer-config'], cwd=QEMU_REPO_PATH_CGC) != 0:
        raise LibError("Unable to configure tracer-qemu-cgc")

    if subprocess.call(['./tracer-config'], cwd=QEMU_REPO_PATH_LINUX) != 0:
        raise LibError("Unable to configure tracer-qemu-linux")

    if subprocess.call(['make'], cwd=QEMU_REPO_PATH_CGC) != 0:
        raise LibError("Unable to build tracer-qemu-cgc")

    if subprocess.call(['make'], cwd=QEMU_REPO_PATH_LINUX) != 0:
        raise LibError("Unable to build tracer-qemu-linux")

    shutil.copyfile(os.path.join(QEMU_REPO_PATH_CGC, "i386-linux-user", "qemu-i386"), QEMU_PATH_CGC)
    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "i386-linux-user", "qemu-i386"), QEMU_PATH_LINUX_I386)
    shutil.copyfile(os.path.join(QEMU_REPO_PATH_LINUX, "x86_64-linux-user", "qemu-x86_64"), QEMU_PATH_LINUX_X86_64)

    os.chmod(QEMU_PATH_CGC, 0755)
    os.chmod(QEMU_PATH_LINUX_I386, 0755)
    os.chmod(QEMU_PATH_LINUX_X86_64, 0755)

class build(_build):
    def run(self):
            self.execute(_build_qemus, (), msg="Building Tracer QEMU")
            _build.run(self)
cmdclass = {'build': build}


setup(
    name='tracer', version='0.1', description="Symbolically trace concrete inputs.",
    packages=['tracer'],
    data_files=[
        ('bin', ('bin/tracer-qemu-cgc',),),
        ('bin', ('bin/tracer-qemu-linux-i386',),),
        ('bin', ('bin/tracer-qemu-linux-x86_64',),),
    ],
    cmdclass=cmdclass,
)
