## Copyright (C) 2008 Ben Smith <benjamin.coder.smith@gmail.com>

##    This file is part of pyctags.

##    pyctags is free software: you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published
##    by the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.

##    pyctags is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    and the GNU Lesser General Public Licens along with pyctags.  If not, 
##    see <http://www.gnu.org/licenses/>.



"""
A ctags file reader and a wrapper to the command line program ctags.

This package has been tested against exuberant ctags version 5.7 and SVN revision 686 on Windows XP with Python 2.5, 2.6, and 3.0, and on Linux with Python 2.5.

B{Security Notes:}
 - This package makes use of the subprocess.Popen() and eval() python constructs.  
 - This package B{does not} filter the parameters for security, instead relying on module users to implement relevant security for their applications.
 
Included in the source distribution is an example of usage and several tests that can illustrate usage.

Here's a very small sample to show it in action::

    from pyctags import exuberant_ctags, ctags_file

    # if you have a list of source files:
    ctags = exuberant_ctags()

    # the module will default to running whichever ctags is on the path, if it can
    taglist = ctags.generate_tags(files=['path/to/source.h'])
    
    # or you can specify a path
    taglist = ctags.generate(tag_program='/opt/bin/ctags', files=['/path/to/source.h', '/path/to/different/source.py', '../also/here.c'])
    
    # pass additional flags to exuberant ctags (file list stored from previous run or constructor)
    taglist = ctags.generate_tags(generator_options={'--fields' : '+iKmn', '-F' : None}

    # you can generate a tag file instead
    ctags.generate_tagfile(output_file_path, generator_options={'--fields' : '+iKmn'}, file_list=['../some_dir/src.s'])
    
    # a few ways to parse into a ctags_file object
    tagfile = ctags_file(taglist)
    
    # or, if you already have a tags file:
    tagfile = ctags_file("/path/to/tagfile")
    
    # or from a list
    file_lines = open("/path/to/tagfile").readlines()
    tagfile = ctags_file(file_lines)

    # you can also do it this way
    tagfile = ctags_file()
    tagfile.parse(file_lines)
    
    # clears data from file_lines
    tagfile.parse("/path/to/tagfile")
    
    print len(tagfile.tags) # number of tags

    from pyctags.harvests import lookup_name_harvest, kind_harvest, by_name_harvest
    
    lookup = lookup_name_harvest()
    k_harvest = kind_harvest()
    by_name_harvester = by_name_harvest()
    tagfile.harvest([lookup, k_harvest, by_name_harvester])
    
    by_name = by_name_harvester.retrieve_data()    
    f_tags = lookup.starts_with('f', case_sensitive=True) # print all tags that start with a lower case f
    
    # get the full tag info from the name
    for tagname in ftags:
        for tag in by_name[tagname]:
            print (tag.name, tag.file, tag.line)

    kinds = k_harvest.retrieve_data()
    print(kinds['class']) # print all classes (from +K flag to exuberant ctags)
    
I'm not certain if ctags generators other than Exuberant Ctags are in much use, but wrappers for them can be derived from ctags_base.py.
Feel free to contact me for or with details.

Pyctags is pretty heavy for large projects.  A 153 MB tag file generated from linux kernel sources takes a little while to 
process and consumes over 1.1GB of RAM.  I hope to learn more ways to trim this down.
"""

from pyctags.tag_file import ctags_file
from pyctags.tag_entry import ctags_entry
from pyctags.exuberant import exuberant_ctags
import pyctags.harvesters
