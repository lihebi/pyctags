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


import unittest, sys
sys.path.append("../pyctags")
from readtags import ctags_entry, ctags_file
from make_tagfiles import file_lists
from tag_lists import tag_lists

entry_kwargs_pattern = {"name" : "testName", "file" : "../testFile", "pattern" : "testPattern", "extensions" : {"aa" : "aav", "bb" : "bbv"}}
entry_kwargs_min_line = {"name" : "testName", "file" : "../testFile", "line_number" : 555}
entry_kwargs_min_pattern = {"name" : "testName", "file" : "../testFile", "pattern" : "testPattern"}
entry_kwargs_line = {"name" : "testName", "file" : "../testFile", "line_number" : 555, "extensions" : {"aa" : "aav", "bb" : "bbv"}}
entry_kwargs_both = {"name" : "testName", "file" : "../testFile", "pattern" : "testPattern", "line_number" : 555, "extensions" : {"aa" : "aav", "bb" : "bbv"}}
entry_kwargs_neither = {"name" : "testName", "file" : "../testFile", "extensions" : {"aa" : "aav", "bb" : "bbv"}}
entry_kwargs_windows_path = {"name" : "testName", "file" : "C:\\foo\\bar\\testFile", "pattern" : "testPattern", "line_number" : 555, "extensions" : {"aa" : "aav", "bb" : "bbv"}}
class test_ctags_entry(unittest.TestCase):
    
    def test_short_filename(self):
        d = entry_kwargs_windows_path
        fn = d['file']
        te = ctags_entry(**d)
        self.failUnless(te.name == d['name'])
        self.failUnless(te.file == fn)
        self.failUnless(te.pattern == d['pattern'])
        self.failUnless(te.line_number == d['line_number'])
        self.failUnless(te.extensions == d['extensions'])
        self.failUnless(te.short_filename == fn[fn.rfind("\\") + 1:])
    
    def test_pattern_init(self):
        d = entry_kwargs_pattern
        fn = d['file']
        te = ctags_entry(**d)
        self.failUnless(te.name == d['name'])
        self.failUnless(te.file == fn)
        self.failUnless(te.pattern == d['pattern'])
        self.failUnless(te.line_number == None)
        self.failUnless(te.extensions == d['extensions'])
        self.failUnless(te.short_filename == fn[fn.rfind("/") + 1:])
        
    def test_linenum_init(self):
        d = entry_kwargs_line
        fn = d['file']
        te = ctags_entry(**d)
        self.failUnless(te.name == d['name'])
        self.failUnless(te.file == d['file'])
        self.failUnless(te.pattern == None)
        self.failUnless(te.line_number == d['line_number'])
        self.failUnless(te.extensions == d['extensions'])
        self.failUnless(te.short_filename == fn[fn.rfind("/") + 1:])

    def test_both_init(self):
        d = entry_kwargs_both
        fn = d['file']
        te = ctags_entry(**d)
        self.failUnless(te.name == d['name'])
        self.failUnless(te.file == d['file'])
        self.failUnless(te.pattern == d['pattern'])
        self.failUnless(te.line_number == d['line_number'])
        self.failUnless(te.extensions == d['extensions'])
        self.failUnless(te.short_filename == fn[fn.rfind("/") + 1:])

    def test_neither_init(self):
        te = None
        try:
            te = ctags_entry(**entry_kwargs_neither)
        except ValueError:
            pass
        self.failUnlessEqual(te, None)
    
    def test_str(self):
        te = ctags_entry(**entry_kwargs_both)
        should_be = "%s:%s:%s" % (te.name, te.short_filename, te.line_number)
        self.failUnless(str(te) == should_be)

    def test_empty_tag(self):
        te = None
        try:
            te = ctags_entry(**{})
        except ValueError:
            pass
        self.failUnlessEqual(te, None)
        
        try:
            te = ctags_entry({})
        except ValueError:
            pass
        self.failUnlessEqual(te, None)
        
    def test_min_line(self):
        d = entry_kwargs_min_line
        fn = d['file']
        te = ctags_entry(**d)
        self.failUnless(te.name == d['name'])
        self.failUnless(te.file == d['file'])
        self.failUnless(te.pattern == None)
        self.failUnless(te.line_number == d['line_number'])
        self.failUnless(te.extensions == None)
        self.failUnless(te.short_filename == fn[fn.rfind("/") + 1:])
        
    def test_min_pattern(self):
        d = entry_kwargs_min_pattern
        fn = d['file']
        te = ctags_entry(**d)
        self.failUnless(te.name == d['name'])
        self.failUnless(te.file == d['file'])
        self.failUnless(te.pattern == d['pattern'])
        self.failUnless(te.line_number == None)
        self.failUnless(te.extensions == None)
        self.failUnless(te.short_filename == fn[fn.rfind("/") + 1:])
        
    def test_missing_min(self):
        te = None
        try:
            te = ctags_entry({"name" : "testName", "file" : "testFile"})
        except ValueError:
            pass
        self.failIf(te != None)
        
        te = None
        try:
            te = ctags_entry({"name" : "testName", "line_number" : 555})
        except ValueError:
            pass
        self.failIf(te != None)

        te = None
        try:
            te = ctags_entry({"file" : "testFile", "line_number" : 555})
        except ValueError:
            pass
        self.failIf(te != None)

    def test_kwarg_init(self):
        self.failIf(False)
        
    def test_arg0_init(self):
        self.failIf(False)
        
    def test_eq_ne(self):
        te = ctags_entry(entry_kwargs_both)
        self.failUnlessEqual(te, te)
        
        ent = ctags_entry(entry_kwargs_both)
        self.failUnlessEqual(te, ent)
        
        ent = ctags_entry(**entry_kwargs_both)
        self.failUnlessEqual(te, ent)
        
        self.failUnlessEqual(ent, ent)
    
    def test_repr(self):
        te = ctags_entry(**entry_kwargs_both)
        
        ent = ctags_entry(repr(te))
        self.failUnlessEqual(te, ent)
        
        ent = ctags_entry(entry_kwargs_both)
        self.failUnlessEqual(te, ent)
        
        fail = True
        try:
            ent = ctags_entry(repr(te), **entry_kwargs_both)
        except:
            fail = False
            
        self.failIf(fail)
        
        
        

class test_ctags_file(unittest.TestCase):
    
    def test_init_noparams(self):
        tf = ctags_file()
        self.failIf(tf == None)
    
    def test_init_list(self):
        tf = ctags_file(tag_lists['unextended']['body'])
        self.failUnlessEqual(tf[0], ctags_entry(tag_lists['unextended']['body'][0]))
        self.failUnlessEqual(tf[-1], ctags_entry(tag_lists['unextended']['body'][-1]))
        
        tf = ctags_file(tag_lists['relpath']['body'])
        self.failUnlessEqual(tf[0], ctags_entry(tag_lists['relpath']['body'][0]))
        self.failUnlessEqual(tf[-1], ctags_entry(tag_lists['relpath']['body'][-1]))
        
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
        self.failUnlessEqual(tf[0].extensions['kind'], 'c')
    
    def test_getitem(self):
        tf = ctags_file()
        tf.parse(tag_lists['relpath']['body'])
        te = tf[0]
        ent = ctags_entry(tag_lists['relpath']['body'][0])
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
