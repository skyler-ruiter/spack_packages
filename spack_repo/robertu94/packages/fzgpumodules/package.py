# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack.package import *


class Fzgpumodules(CMakePackage, CudaPackage):
    """Composable CUDA compression pipelines for scientific data."""

    homepage = "https://szcompressor.org/"
    git = "https://github.com/szcompressor/FZGPUModules.git"

    maintainers("skyler-ruiter")

    license("BSD-3-Clause", checked_by="skyler-ruiter")

    version(
        "2.0.0",
        url="https://github.com/szcompressor/FZGPUModules/releases/download/v2.0.0/FZGPUModules-2.0.0-source.tar.gz",
        sha256="fe54bec71b0b83033a3e9653f61898ce2c893ca9cefffc8d6c2d621faab70335",
        preferred=True,
    )
    # Stable-main API snapshot required by the independently decodable adapter.
    version("archive-support", commit="8f73a3988a2e1efd3192850c192f489e253a1a2e")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake@3.24:", type="build")
    depends_on("cuda@11.2:", type=("build", "link", "run"))

    conflicts("~cuda")
    conflicts("cuda_arch=none", when="+cuda")

    variant("shared", default=True, description="Build shared libraries")

    def cmake_args(self):
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define("BUILD_TESTING", False),
            self.define("BUILD_PROFILING", False),
            self.define("BUILD_CLI", False),
            self.define("BUILD_EXAMPLES", False),
            self.define("FZGMOD_BACKEND", "CUDA"),
            self.define(
                "CMAKE_CUDA_ARCHITECTURES",
                self.spec.variants["cuda_arch"].value,
            ),
        ]
        return args