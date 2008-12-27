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

from unittest import TestCase, main as unittest_main
import sys
sys.path.append("../pyctags")
from ctags_file import ctags_file
from harvests import kind_harvest, name_lookup_harvest
from tag_lists import tag_lists

class TestHarvesting(TestCase):
    def do_kind_harvest(self, taglist):
        kh = kind_harvest()
        tf = ctags_file(taglist, harvests=[kh])
        return (tf, kh.retrieve_data())
    
    def check_kind_keys(self, kinds, keys):
        for k in keys:
            self.failUnless(k in kinds)
            self.failUnless(type(kinds[k]), list)
            self.failUnless(len(kinds[k]))


    def test_kind_harvest(self):

        (tf, kinds) = self.do_kind_harvest(tag_lists['unextended']['body'])
        self.failUnlessEqual(len(kinds), 0)
        
        (tf, kinds) = self.do_kind_harvest(tag_lists['no_kinds']['body'])
        self.failUnlessEqual(len(kinds), 0)

        (tf, kinds) = self.do_kind_harvest(tag_lists['relpath']['body'])
        self.failUnlessEqual(len(kinds), 3)
        self.check_kind_keys(kinds, ['c', 'm', 'v'])
        
        for tag in tf.tags:
            if 'kind' in tag.extensions:
                self.failUnless(tag in kinds[tag.extensions['kind']])

        (tf, kinds) = self.do_kind_harvest(tag_lists['hyper_extended']['body'])
        self.failUnlessEqual(len(kinds), 3)
        self.check_kind_keys(kinds, ['class', 'member', 'variable'])
        
        for tag in tf.tags:
            if 'kind' in tag.extensions:
                self.failUnless(tag in kinds[tag.extensions['kind']])

    def test_name_lookup_harvest(self):
        lookup_harvest = name_lookup_harvest()
        tf = ctags_file(tag_lists['extended']['body'], harvests=[lookup_harvest])
        
        tags = lookup_harvest.starts_with('c', case_sensitive=True)
        self.failUnlessEqual(len(tags), 4)

        tags = lookup_harvest.starts_with('C', case_sensitive=True)
        self.failUnlessEqual(len(tags), 0)
        
        atags = lookup_harvest.starts_with('a')
        self.failUnlessEqual(len(atags), 0)

        tags = lookup_harvest.starts_with('c')
        self.failUnlessEqual(len(tags), 4)
        
        tag_tags = lookup_harvest.starts_with('ctags_')
        self.failUnlessEqual(len(tag_tags), 4)

        tags = lookup_harvest.starts_with('c', num_results=2)
        self.failUnlessEqual(len(tags), 2)

        tags = lookup_harvest.starts_with('C', num_results=2)
        self.failUnlessEqual(len(tags), 2)
    
        tags = lookup_harvest.starts_with('c', num_results=5)
        self.failUnless(len(tags) <= 5)

        tags = lookup_harvest.starts_with('c', num_results=3, case_sensitive=True)
        self.failUnlessEqual(len(tags), 3)

        tags = lookup_harvest.starts_with('C', num_results=2, case_sensitive=True)
        self.failUnlessEqual(len(tags), 0)
    
        tags = lookup_harvest.starts_with('c', num_results=2, case_sensitive=False)
        self.failUnlessEqual(len(tags), 2)

        tags = lookup_harvest.starts_with('C', num_results=2, case_sensitive=False)
        self.failUnlessEqual(len(tags), 2)

        
if __name__ == '__main__':
    unittest_main()