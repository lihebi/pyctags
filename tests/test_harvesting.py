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
from harvester import harvester
from harvests import harvest_kinds as kinds
from tag_lists import tag_lists

class TestHarvesting(TestCase):
    def do_kind_harvest(self, taglist):
        kind_harvest = kinds()
        tf = ctags_file(taglist, harvests=[kind_harvest])
        return (tf, kind_harvest.retrieve_data())
    
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
        
        for tag in tf:
            if 'kind' in tag.extensions:
                self.failUnless(tag in kinds[tag.extensions['kind']])

        (tf, kinds) = self.do_kind_harvest(tag_lists['hyper_extended']['body'])
        self.failUnlessEqual(len(kinds), 3)
        self.check_kind_keys(kinds, ['class', 'member', 'variable'])
        
        for tag in tf:
            if 'kind' in tag.extensions:
                self.failUnless(tag in kinds[tag.extensions['kind']])

if __name__ == '__main__':
    unittest_main()
