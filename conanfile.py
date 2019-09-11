#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools

class EnetConan(ConanFile):
    name = "enet"
    version = "1.3.14"
    license = "https://github.com/maingig/enet/blob/master/LICENSE"
    author = "https://github.com/maingig/enet/graphs/contributors"
    url = "https://github.com/maingig/enet.git"
    description = "ENet reliable UDP networking library"
    topics = ("udp", "C", "networking")
    settings = "os", "compiler", "build_type", "arch"
    exports = "*"
    options = {
        "shared": [ True, False ],
        "fPIC": [ True, False ],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
    }
    generators = "cmake"
    source_subfolder = "source_subfolder"

    # Custom variables
    source_url = url
    source_branch = "master"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        self.run("git clone %s %s" % (self.source_url, self.name))
        self.run("cd %s && git checkout" % (self.name))

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self.name, build_folder=self.name)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self.source_subfolder)
        self.copy("*.h", "include", "%s/%s/include" % (self.build_folder, self.name))
        if self.options.shared:
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(['winmm', 'ws2_32'])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(['pthread'])
        elif self.settings.os == "QNX":
            self.cpp_info.libs.extend(['socket'])
