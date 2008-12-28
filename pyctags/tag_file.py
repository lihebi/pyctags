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
Python representation of ctags format file.
"""

import os
try:
    # do relative imports for tests
    # try this first in case pyctags is already installed, since we want to be testing the source bundled in the distribution
    from kwargs_validator import the_validator as validator
    from tag_entry import ctags_entry, _PYTHON_3000_
except ImportError:
    from pyctags.kwargs_validator import the_validator as validator
    from pyctags.tag_entry import ctags_entry


class ctags_file:
    """
    Class that parses ctags generated files contains resulting ctags_entry objects.
    """
    
    def __init__(self, tags=None, **kwargs):
        """
        @param tags: If I{tags} is a sequence, it will automatically be parsed.  If it is a filename or path, it will be opened and parsed.
        @type tags: sequence or str
            - B{Keyword Arguments:}
                - B{harvests:} (list) list of harvesting classes
        """
        
        valid_kwargs = ['harvests']
        validator.validate(kwargs.keys(), valid_kwargs)
        
        self._clear_variables()

        if tags:
            if type(tags) == str:
                tags = open(tags).readlines()
            self.parse(tags, **kwargs)

    def _clear_variables(self):
        """
        Sets internal maps to initial values.
        """
        self.format = None
        """ Format from the header."""
        self.format_comment = None
        """ Format header comment."""
        self.sorted = None
        """ Sorting type."""
        self.sorted_comment = None
        """ Sorting type comment."""
        self.author = None
        """ Ctags author."""
        self.author_comment = None
        """ Ctags author comment."""
        self.name = None
        """ Tag program name."""
        self.name_comment = None
        """ Tag program comment."""
        self.url = None
        """ Tag program url."""
        self.url_comment = None
        """ Tag program url comment."""
        self.version = None
        """ Tag program version."""
        self.version_comment = None
        """ Tag program version comment."""
        
        self.tags = list()
        """ List of ctags_entry elements."""
        
    def __header_format(self, line):
        """ Processes !_ctags_file_FORMAT ctags header."""
        if not self.format:
            self.format = int(line[0])
            self.format_comment = line[1].strip('/')

    def __header_sorted(self, line):
        """ Processes !_ctags_file_SORTED ctags header."""
        self.sorted = int(line[0])
        self.sorted_comment = line[1].strip('/')

    def __header_author(self, line):
        """ Processes !_TAG_PROGRAM_AUTHOR ctags header."""
        self.author = line[0]
        self.author_comment = line[1].strip('/')

    def __header_name(self, line):
        """ Processes !_TAG_PROGRAM_NAME ctags header."""
        self.name = line[0]
        self.name_comment = line[1].strip('/')

    def __header_url(self, line):
        """ Processes !_TAG_PROGRAM_URL ctags header."""
        self.url = line[0]
        self.url_comment = line[1].strip('/')
        
    def __header_version(self, line):
        """ Processes !_TAG_PROGRAM_VERSION ctags header."""
        self.version = line[0]
        self.version_comment = line[1].strip('/')
        
    __HEADER_ITEMS = {
        '!_TAG_FILE_FORMAT' : __header_format,
        '!_TAG_FILE_SORTED' : __header_sorted,
        '!_TAG_PROGRAM_AUTHOR' : __header_author,
        '!_TAG_PROGRAM_NAME' : __header_name,
        '!_TAG_PROGRAM_URL' : __header_url,
        '!_TAG_PROGRAM_VERSION' : __header_version
    }
    
    def parse(self, tags, **kwargs):
        """
        Parses ctags file and constructs data members.
        @param tags: Filename or sequence of tag strings to parse.
        @type tags: sequence or str
            - B{Keyword Arguments:}
                - B{harvests:} (list) list of harvesting classes
        @raises ValueError: parsing error
        """

        valid_kwargs = ['harvests']
        validator.validate(kwargs.keys(), valid_kwargs)

        if type(tags) == str:
            tags = open(tags)

        self._clear_variables()
        
        harvests = list()
        if 'harvests' in kwargs:
            harvests = kwargs['harvests']
            
        for harvest in harvests:
            harvest.set_tagfile(self)
            harvest.do_before()
            
        line_number = 1

        for rawline in tags:
            line = rawline.strip()
            if not _PYTHON_3000_ and type(line) is not unicode:
                line = unicode(line, "utf-8")
            if line[0] == '!':
                # this is part of the file information header
                elements = line.split('\t')
                try:
                    self.__HEADER_ITEMS[elements[0]](self, elements[1:])
                except KeyError:
                    print ("Unknown header comment element " + elements[0] + " at line " + line_number + ".")
            else:
                entry = ctags_entry(line)

                self.tags.append(entry)
                for harvest in harvests:
                    harvest.feed(entry)

            line_number += 1

        for harvest in harvests:
            harvest.do_after()

    def harvest(self, harvests):
        """
        Used to perform new data harvests with already processed tags.
        @param harvests: list of harvest classes to apply to existing tags.
        @type harvests: list of instances supporting abstract_harvest interface.
        @raises ValueError: if no tag data is available to process.
        """
        
        if not len(self.tags):
            raise ValueError("No tag data to harvest from.")
        
        for h in harvests:
            h.set_tagfile(self)
            h.do_before()
        
        for tag in self.tags:
            h.feed(tag)
            
        for h in harvests:
            h.do_after()
            
