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

This package has been tested against exuberant ctags version 5.7 and SVN revision 686 on Windows XP and Linux with Python 2.5 and 2.6.

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
    taglist = ctags.generate_tags(generator_options={'--fields' : '+imn', '-F' : None}

    # you can generate a tag file instead
    ctags.generate_tagfile(output_file_path, generator_options={'--fields' : '+imn'}, file_list=['../some_dir/src.s'])
    
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
    
    print len(tagfile) # number of tags

    f_tags = tagfile.starts_with('f', case_sensitive=True) # print all tags that start with a lower case f

    first_tag = tagfile[0]

    for tag in tagfile:
        print tag

    taglist = tagfile['tagname'] # list of tags that match tagname

    for tag in taglist:
        print tag.name
        print tag.line_number
        print tag.pattern
        print tag.extensions
        
I'm not certain if ctags generators other than Exuberant Ctags are in much use, but wrappers for them can be derived from ctags_base.py.
Feel free to contact me for or with details.

Pyctags is currently unsuitable for extremely large projects.  I've used it to generate a custom kernel source tag file that came out to 153 MB,
generation worked fine but I had to kill the tag parser - it was soaking up an enormous amount of RAM.  The kernel source is a very large data 
set to represent all of in memory at once in python, though I'm hoping there are things I can do to address this.  Things will work fine on smaller
projects than the Linux kernel, depending on the amount of system memory available.
"""

from exuberant import exuberant_ctags
from ctags_file import ctags_file
from ctags_entry import ctags_entry
