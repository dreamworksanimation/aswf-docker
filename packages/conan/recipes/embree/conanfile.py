# Copyright (c) Contributors to the aswf-docker Project. All rights reserved.
# SPDX-License-Identifier: MIT

import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get

required_conan_version = ">=2.1"


class EmbreeConan(ConanFile):
    name = "embree"
    description = (
        "Intel® Embree is a collection of high-performance ray tracing kernels, "
        "developed at Intel. It targets 64-bit CPUs supporting SSE2 or higher."
    )
    license = "Apache-2.0"
    url = "https://www.embree.org/"
    homepage = "https://www.embree.org/"
    topics = ("raytracing", "rendering", "simd", "ispc")
    package_type = "shared-library"
    settings = "os", "arch"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.ref} prebuilt binary is only available for Linux")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(
                f"{self.ref} prebuilt binary is only available for x86_64")

    def source(self):
        pass  # download in build() — self.settings not available in source()

    def build(self):
        arch = str(self.settings.arch)
        get(self, **self.conan_data["sources"][self.version][arch],
            destination=self.build_folder)  # no strip_root — tarball is prefix layout

    def package(self):
        copy(self, "LICENSE.txt",
             src=os.path.join(self.build_folder, "doc"),
             dst=os.path.join(self.package_folder, "licenses", self.name))
        # Headers
        copy(self, "*",
             src=os.path.join(self.build_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        # Shared libs: embree4 + bundled TBB/Intel runtime (exact ABI match for this build)
        for pattern in ("libembree4*", "libtbb.so*", "libtbbmalloc.so*",
                        "libimf.so*", "libirng.so*", "libsvml.so*", "libintlc.so*"):
            copy(self, pattern,
                 src=os.path.join(self.build_folder, "lib"),
                 dst=os.path.join(self.package_folder, "lib"))
        # ASWF: keep cmake config files for non-Conan consumers
        copy(self, "*",
             src=os.path.join(self.build_folder, "lib", "cmake"),
             dst=os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        # Binary-only: OS + arch only
        pass

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "embree4")
        self.cpp_info.set_property("cmake_target_name", "embree4")
        self.cpp_info.libs = ["embree4", "tbb", "tbbmalloc"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
