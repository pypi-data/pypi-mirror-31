#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Copyright (c) 2006-2008 Andreas Kloeckner, Christoph Burgmer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def get_config_schema():
    from aksetup_helper import ConfigSchema, \
            IncludeDir, LibraryDir, Libraries, BoostLibraries, \
            Switch, StringListOption, make_boost_base_options

    return ConfigSchema(make_boost_base_options() + [
        BoostLibraries("python"),

        IncludeDir("TAGLIB", []),
        LibraryDir("TAGLIB", []),
        Libraries("TAGLIB", ["tag"]),

        StringListOption("CXXFLAGS", [],
            help="Any extra C++ compiler options to include"),
        ])


def main():
    from aksetup_helper import hack_distutils, get_config, setup, Extension

    hack_distutils()
    conf = get_config(get_config_schema())

    INCLUDE_DIRS = conf["TAGLIB_INC_DIR"] + conf["BOOST_INC_DIR"]
    LIBRARY_DIRS = conf["TAGLIB_LIB_DIR"] + conf["BOOST_LIB_DIR"]
    LIBRARIES = conf["TAGLIB_LIBNAME"] + conf["BOOST_PYTHON_LIBNAME"]

    setup(name="tagpy",
          version="2018.1",
          description="Python Bindings for TagLib",
          long_description=open("README.rst", "rt").read(),
          author="Andreas Kloeckner",
          author_email="inform@tiker.net",
          classifiers=
          [
              "Development Status :: 5 - Production/Stable",
              "Intended Audience :: Developers",
              "License :: OSI Approved :: MIT License",
              "Natural Language :: English",
              "Operating System :: OS Independent",
              "Operating System :: POSIX",
              "Operating System :: Unix",
              "Programming Language :: Python",
              "Programming Language :: Python :: 3",
              "Topic :: Multimedia :: Sound/Audio",
              "Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Ripping",
              "Topic :: Multimedia :: Sound/Audio :: Editors",
              "Topic :: Software Development :: Libraries :: Python Modules",
              "Topic :: Utilities"],
          license="MIT",

          install_requires=["pytest"],

          url="http://mathema.tician.de/software/tagpy",
          packages=["tagpy", "tagpy.ogg"],
          ext_modules=[
              Extension("_tagpy",
                  ["src/wrapper/basics.cpp",
                      "src/wrapper/id3.cpp",
                      "src/wrapper/rest.cpp"],
                  include_dirs=INCLUDE_DIRS,
                  library_dirs=LIBRARY_DIRS,
                  libraries=LIBRARIES,
                  extra_compile_args=conf["CXXFLAGS"],
                  ),
                        ]
          )


if __name__ == '__main__':
    main()
