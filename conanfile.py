#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools

class EnetConan(ConanFile):
    name = "enet"
    version = "1.3.14"
    license = "https://github.com/lsalzman/enet/blob/master/LICENSE"
    author = "https://github.com/lsalzman/enet/graphs/contributors"
    url = "https://github.com/lsalzman/enet.git"
    description = "ENet reliable UDP networking library"
    topics = ("udp", "C", "networking")
    settings = "os", "compiler", "build_type", "arch"
    exports = "*"
    options = {
        "shared": [ True, False ],
        "fPIC": [ True, False ],
    }
    default_options = {
        'shared': True,
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

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.fPIC
        #env_build.libs.append("pthread")
        if self.settings.os == "QNX":
            env_build.defines.append("__EXT_BSD=ON")
        if self.settings.os == "Windows" and self.options.shared:
            env_build.defines.append("ENET_DLL=ON")
        with tools.environment_append(env_build.vars):
            if self.settings.os == "Windows":
                self.run('cd %s && NMAKE /f "enet.mak" CFG="enet - Win32 Debug"' % (self.name))
            else:
                self.run("cd %s && autoreconf -vfi" % (self.name))
                self.run("cd %s && ./configure" % (self.name))
                self.run("cd %s && make" % (self.name))
                self.run("cd %s && ./libtool --mode=install /usr/bin/install -c libenet.la %s/%s" % (self.name, self.build_folder, self.name))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src="%s/%s" % (self.build_folder, self.name))
        self.copy("*.h", "include", "%s/%s/include" % (self.build_folder, self.name))
        if self.options.shared:
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(['psapi', 'ws2_32'])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(['pthread'])
        elif self.settings.os == "QNX":
            self.cpp_info.libs.extend(['socket'])
