#!/usr/bin/env python
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

import unittest, sys
sys.path.append("../pyctags")
from ctags_file import ctags_file, _UNKNOWN_LANGUAGE_KEY_
from ctags_entry import ctags_entry
from tag_lists import tag_lists

class test_ctags_file(unittest.TestCase):
    
    def test_init_noparams(self):
        tf = ctags_file()
        self.failIf(tf == None)
    
    def test_init_list(self):
        tf = ctags_file(tag_lists['unextended']['body'])
        for line in tag_lists['unextended']['body']:
            e = ctags_entry(line)
            self.failIf(e not in tf)
            
        tf = ctags_file(tag_lists['relpath']['body'])
        for line in tag_lists['relpath']['body']:
            e = ctags_entry(line)
            self.failIf(e not in tf)
        
    def test_parse_list(self):
        tf = ctags_file()
        tf.parse(tag_lists['unextended']['body'])
        
        tf = ctags_file()
        tf.parse(tag_lists['relpath']['body'])

    def test_init_with_filename(self):
        tf = ctags_file("relpath.tags")
        tf2 = ctags_file(tag_lists['relpath']['body'])
        self.failUnlessEqual(len(tf), len(tf2))

        i = 0
        for t in tf:
            self.failUnlessEqual(t, tf2[i])
            i += 1

    def test_parse_with_filename(self):
        tf = ctags_file()
        tf.parse("relpath.tags")
        tf2 = ctags_file(tag_lists['relpath']['body'])
        self.failUnlessEqual(len(tf), len(tf2))

        i = 0
        for t in tf:
            self.failUnlessEqual(t, tf2[i])
            i += 1


    def test_starts_with_case_sensitive(self):
        tf = ctags_file(tag_lists['extended']['head'] + tag_lists['extended']['body'])
        tags = tf.starts_with('c', case_sensitive=True)

        self.failUnlessEqual(len(tags), 4)
        tags = tf.starts_with('C', case_sensitive=True)
        self.failUnlessEqual(len(tags), 0)
    
    def test_starts_with_case_insensitive(self):
        tf = ctags_file(tag_lists['extended']['head'] + tag_lists['extended']['body'])

        self.failUnless(len(tf))
        
        atags = tf.starts_with('a')
        self.failUnlessEqual(len(atags), 0)

        tags = tf.starts_with('c')
        self.failUnlessEqual(len(tags), 4)
        
        tag_tags = tf.starts_with('ctags_')
        self.failUnlessEqual(len(tag_tags), 4)
        
    
    def test_starts_with_limit(self):
        tf = ctags_file(tag_lists['extended']['head'] + tag_lists['extended']['body'])

        tags = tf.starts_with('c', num_results=2)
        self.failUnlessEqual(len(tags), 2)

        tags = tf.starts_with('C', num_results=2)
        self.failUnlessEqual(len(tags), 2)
    
        tags = tf.starts_with('c', num_results=5)
        self.failUnless(len(tags) <= 5)
        
    def test_starts_with_case_sensitive_with_limit(self):
        tf = ctags_file(tag_lists['extended']['head'] + tag_lists['extended']['body'])

        tags = tf.starts_with('c', num_results=3, case_sensitive=True)
        self.failUnlessEqual(len(tags), 3)

        tags = tf.starts_with('C', num_results=2, case_sensitive=True)
        self.failUnlessEqual(len(tags), 0)
    
    def test_starts_with_case_insensitive_with_limit(self):
        tf = ctags_file(tag_lists['extended']['head'] + tag_lists['extended']['body'])

        tags = tf.starts_with('c', num_results=2, case_sensitive=False)
        self.failUnlessEqual(len(tags), 2)

        tags = tf.starts_with('C', num_results=2, case_sensitive=False)
        self.failUnlessEqual(len(tags), 2)
    
    def test_extended_kinds(self):
        tf = ctags_file(tag_lists['extended']['body'])
        tf2 = ctags_file(tag_lists['relpath']['body'])
        
        self.failUnlessEqual(tf[0].extensions['kind'], tf2[0].extensions['kind'])
    
    def test_getitem(self):
        tf = ctags_file()
        ent = ctags_entry(tag_lists['relpath']['body'][0])
        tf.parse(tag_lists['relpath']['body'])
        te = tf[repr(ent)]
        self.failUnlessEqual(te, ent)
 
    def test_setitem(self):
        tf = ctags_file()
        tf.parse(tag_lists['relpath']['body'])
        fail = True
        try:
            tf[0] = "abc"
        except AttributeError:
            fail = False
        self.failIf(fail)
    
    def test_delitem(self):
        tf = ctags_file(tag_lists['relpath']['body'])
        fail = True
        try:
            del tf[0]
        except AttributeError:
            fail = False
        self.failIf(fail)
    
    def test_len(self):
        tf = ctags_file(tag_lists['relpath']['body'])
        self.failUnlessEqual(len(tf), len(tag_lists['relpath']['body']))
    
    def test_iter(self):
        tf = ctags_file(tag_lists['relpath']['body'])
        l = len(tag_lists['relpath']['body'])
        i = 0
        for g in tf:
            i += 1
        self.failUnlessEqual(l, i)
        

if __name__ == '__main__':
    unittest.main()
