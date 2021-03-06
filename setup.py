from multiprocessing import cpu_count
import os
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution
from shutil import copyfile
from subprocess import check_call
from sys import platform


class CMakeBuild(build_py):
    SHLIBEXT = "dylib" if platform == "darwin" else "so"

    def run(self):
        if not self.dry_run:
            self._build()
        super(CMakeBuild, self).run()

    def get_outputs(self, *args, **kwargs):
        outputs = super(CMakeBuild, self).get_outputs(*args, **kwargs)
        outputs.extend(self._shared_lib)
        return outputs

    def _build(self, builddir=None):
        check_call(("cmake", "-DCMAKE_BUILD_TYPE=Release",
                    "-DCUDA_TOOLKIT_ROOT_DIR=%s" % os.getenv(
                        "CUDA_TOOLKIT_ROOT_DIR",
                        "must_export_CUDA_TOOLKIT_ROOT_DIR"),
                    "."))
        check_call(("make", "-j%d" % cpu_count()))
        self.mkpath(self.build_lib)
        shlib = "libKMCUDA." + self.SHLIBEXT
        dest = os.path.join(self.build_lib, shlib)
        copyfile(shlib, dest)
        self._shared_lib = [dest]


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(self):
        return True

    def is_pure(self):
        return False

setup(
    name="libKMCUDA",
    description="Accelerated K-means and K-nn on GPU",
    version="5.0.0",
    license="MIT",
    author="Vadim Markovtsev",
    author_email="vadim@sourced.tech",
    url="https://github.com/src-d/kmcuda",
    download_url="https://github.com/src-d/kmcuda",
    py_modules=["libKMCUDA"],
    install_requires=["numpy"],
    distclass=BinaryDistribution,
    cmdclass={'build_py': CMakeBuild},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ]
)

# python3 setup.py bdist_wheel
# auditwheel repair -w dist dist/*
# twine upload dist/*manylinux*
