#!/usr/bin/env python
## Copyright (C) 2008 Ben Smith <benjamin.coder.smith@gmail.com>

##    This file is part of pyctags.

##    pyctags is free software: you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.

##    pyctags is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    and the GNU Lesser General Public Licens along with pyctags.  If not, 
##    see <http://www.gnu.org/licenses/>.


import unittest, os, sys
sys.path.append("../pyctags")
from exuberant import exuberant_ctags
from tag_lists import tag_lists
from make_tagfiles import file_lists, extended_tests


class test_exuberant_ctags(unittest.TestCase):
    
    def test_init(self):
        ec = exuberant_ctags(tag_program='ctags', files=file_lists['relpath'])
        ec = exuberant_ctags(files=file_lists['relpath'])
        ec = exuberant_ctags(tag_program='ctags')
        ec = exuberant_ctags()
    
    def test_executable_set(self):
        ec = exuberant_ctags(tag_program='ctags')

        ec = exuberant_ctags()
        ec.ctags_executable('/bin/ctags')
        
        ec = exuberant_ctags()
        ec.generate_tagfile("generated_tags", tag_program='ctags', files=file_lists['relpath'])
        self.failIf(not os.path.exists("generated_tags"))
    
    def test_empty_list(self):
        ec = exuberant_ctags(tag_program='ctags', files=[])
        tags = ec.generate_tags()
        self.failUnlessEqual(len(tags), 0)
    
    def test_no_ctags_set(self):
        # TODO this test fails if ctags isn't found on the path
        ec = exuberant_ctags(files=file_lists['relpath'])
        tags = ec.generate_tags()
        self.failUnlessEqual(tags[0], tag_lists['relpath']['body'][0])
        
    def test_generate_tags(self):
        ec = exuberant_ctags()
        tags = ec.generate_tags(tag_program='ctags', files=file_lists['relpath'])
        self.failUnlessEqual(tags[0], tag_lists['relpath']['body'][0])
        self.failUnlessEqual(tags[-1], tag_lists['relpath']['body'][-1])

    def test_generate_from_unc_files(self):
        if extended_tests and sys.platform == "win32":
            ec = exuberant_ctags(tag_program='ctags', files=file_lists['unc'])
            tags = ec.generate_tags()
            self.failUnlessEqual(tags[0], tag_lists['unc']['body'][0])
    
    def test_generate_from_drive_letter_path(self):
        if extended_tests and sys.platform == "win32":
            ec = exuberant_ctags(tag_program='ctags', files=file_lists['drive_letter'])
            tags = ec.generate_tags()
            self.failUnlessEqual(tags[0], tag_lists['drive_letter']['body'][0])
        
    def test_generate_to_unc_filename(self):
        if extended_tests and sys.platform == "win32":
            ec = exuberant_ctags(tag_program='ctags', files=file_lists['relpath'])
            self.failUnless(ec.generate_tagfile('\\\\lazarus\\network write\\tagfile'))
        
    def test_generate_to_drive_letter_path(self):
        if extended_tests and sys.platform == "win32":
            ec = exuberant_ctags(tag_program='ctags', files=file_lists['relpath'])
            self.failUnless(ec.generate_tagfile('C:\\tagfile'))
        
    def test_generate_tagfile(self):
        # use tempfile instead
        ec = exuberant_ctags(tag_program='ctags', files=file_lists['relpath'])
        ec.generate_tagfile("generated_tags")
        self.failIf(not os.path.exists("generated_tags"))
        os.remove("generated_tags")
        
        ec = exuberant_ctags(tag_program='ctags')
        ec.generate_tagfile("generated_tags", files=file_lists['relpath'])
        self.failIf(not os.path.exists("generated_tags"))
        os.remove("generated_tags")

        ec = exuberant_ctags()
        ec.generate_tagfile("generated_tags", tag_program='ctags', files=file_lists['relpath'])
        self.failIf(not os.path.exists("generated_tags"))
        os.remove("generated_tags")

    def test_custom_params(self):
        ec = exuberant_ctags(tag_program='ctags', files=file_lists['relpath'])
        tags = ec.generate_tags(generator_options={'-e' : None})
        self.failUnless(ec.command_line.find(' -e ') > 0)
        
        # could use a few more tests here

    def test_custom_input_files(self):
        ec = exuberant_ctags(tag_program='ctags')
        ec.generate_tagfile("customtags", generator_options={'-L' : "relpath.txt"})
        self.failIf(not os.path.exists("customtags"))
        os.remove("customtags")


if __name__ == '__main__':
    unittest.main()
