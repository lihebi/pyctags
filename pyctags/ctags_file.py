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

from copy import copy
import os
from kwargs_validator import the_validator as validator
from ctags_entry import ctags_entry

_UNKNOWN_LANGUAGE_KEY_ = 'unspecified'


class ctags_file:
    """
    Heavyweight class that parses ctags generated files and provides multiple query interfaces.
    """
    
    def __init__(self, tags=None):
        """
        Heavyweight class that parses ctags generated files and provides 
        multiple query interfaces.
        @param tags: If I{tags} is a sequence, it will automatically be parsed.  If it is a filename or path, it will be opened and parsed.
        @type tags: sequence or str
        """
        
        self._clear_variables()

        if tags:
            if type(tags) == str:
                tags = open(tags).readlines()
            self.parse(tags)

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
        
        self.language_kinds = {}
        """ 
        dict of dicts of ctags_entry, primary key is language name, subkeys are exuberant ctags kinds.
        If language tags are not found in the tag file, the primary key is set to 'unspecified'.
        This is an empty dict when kind information is not harvested from the ctags file.
        """
        
        self.__tags_by_name = {}
        self.__tags_by_repr = {}
        self.__tags_by_str = {}
        self.__sorted_unique_tag_names = []
        self.__sorted_tags = []
        self.__tag_index = {}
        
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
    
    def parse(self, tags):
        """
        Parses ctags file and constructs data members.
        @param tags: Filename or sequence of tag strings to parse.
        @type tags: sequence or str
        @raises ValueError: parsing error
        """

        extended_format = False
        if type(tags) == str:
            tags = open(tags).readlines()

        self._clear_variables()

        line_number = 1
        for rawline in tags:
            line = rawline.strip()
            if line[0] == '!':
                # this is part of the file information header
                elements = line.split('\t')
                try:
                    self.__HEADER_ITEMS[elements[0]](self, elements[1:])
                except KeyError:
                    print ("Unknown header comment element " + elements[0] + " at line " + line_number + ".")
            else:

                entry = ctags_entry(line)
                if not extended_format and (len(entry.extensions) > 0 or self.format == 2):
                    extended_format = True
                self.__sorted_tags.append(entry)
                
                if entry.name not in self.__tags_by_name:
                    self.__tags_by_name[entry.name] = []
                self.__tags_by_name[entry.name].append(entry)

                tmp = str(entry)
                if tmp not in self.__tags_by_str:
                    self.__tags_by_str[tmp] = []
                self.__tags_by_str[tmp].append(entry)

                self.__tags_by_repr[repr(entry)] = entry
                
                if 'kind' in entry.extensions:
                    langkey = _UNKNOWN_LANGUAGE_KEY_
                    if 'language' in entry.extensions:
                        langkey = entry.extensions['language'].lower()
                        
                    if langkey not in self.language_kinds:
                        self.language_kinds[langkey] = dict()
                        
                    # note: case sensitive output from exuberant ctags
                    entkey = entry.extensions['kind']
                    if entkey not in self.language_kinds[langkey]:
                        self.language_kinds[langkey][entkey] = list()
                    self.language_kinds[langkey][entkey].append(entry)

        self.__sorted_tags.sort(key=repr)
        self.__sorted_unique_tag_names = list(self.__tags_by_name.keys())
        self.__sorted_unique_tag_names.sort()
        
        i = 0
        prev_char = self.__sorted_unique_tag_names[0][0]
        self.__tag_index[prev_char] = {'first' : 0}
        for f in self.__sorted_unique_tag_names:
            if f[0] not in self.__tag_index:
                self.__tag_index[prev_char]['last'] = i - 1
                self.__tag_index[f[0]] = {'first' : i}
                prev_char = f[0]
            i += 1
        self.__tag_index[prev_char]['last'] = i


    def starts_with(self, matchstr, **kwargs):
        """
        Returns an alphabetical list of unique tag names that begin with matchstr.
            - B{Parameters:}
                - B{matchstr:} (str) string to search for in tags db
            - B{Keyword Arguments:}
                - B{num_results:} (int) maximum number of results to return, 0 for all, default
                - B{case_sensitive:} (bool) whether to match case, default False
            - B{Returns:}
                - (list of str) matching tag names
        """
        
        valid_kwargs = ['num_results', 'case_sensitive']
        validator.validate(kwargs.keys(), valid_kwargs)

        final_list = []
        case_sensitive = False
        num_results = 0
        
        if 'num_results' in kwargs:
            num_results = int(kwargs['num_results'])
            
        if len(matchstr) == 0:
            if num_results:
                return self.__sorted_unique_tag_names[0:num_results]
            return self.__sorted_unique_tag_names[:]

        if 'case_sensitive' in kwargs:
            if kwargs['case_sensitive']:
                case_sensitive = True

        tag_names_that_start_with_char = []
        
        if case_sensitive:
            if matchstr[0] not in self.__tag_index:
                return []
        else:
            if matchstr[0].lower() not in self.__tag_index and matchstr[0].upper() not in self.__tag_index:
                return []
        
        if case_sensitive:
            idxs = self.__tag_index[matchstr[0]]
            
            if idxs['first'] == idxs['last'] + 1:
                tag_names_that_start_with_char = self.__sorted_unique_tag_names[idxs['first']]
            else:
                tag_names_that_start_with_char = self.__sorted_unique_tag_names[idxs['first']:idxs['last'] + 1]
            
        else:
            if matchstr[0].lower() in self.__tag_index:
                idxs = self.__tag_index[matchstr[0].lower()]
                
                if idxs['first'] == idxs['last'] + 1:
                    tag_names_that_start_with_char = self.__sorted_unique_tag_names[idxs['first']]
                else:
                    tag_names_that_start_with_char = self.__sorted_unique_tag_names[idxs['first']:idxs['last'] + 1]

            if matchstr[0].upper() in self.__tag_index:
                idxs = self.__tag_index[matchstr[0].upper()]
                
                if idxs['first'] == idxs['last'] + 1:
                    tag_names_that_start_with_char += [self.__sorted_unique_tag_names[idxs['first']]]
                else:
                    tag_names_that_start_with_char += self.__sorted_unique_tag_names[idxs['first']:idxs['last'] + 1]
        
        if len(matchstr) == 1:
            if num_results == 0:
                return tag_names_that_start_with_char[:]
            else:
                return tag_names_that_start_with_char[0:num_results]
        
        if case_sensitive:
            for t in tag_names_that_start_with_char:
                if (t.find(matchstr) == 0):
                    final_list.append(copy(t))
                if num_results > 0 and len(final_list) == num_results:
                    return final_list
        else:
            for t in tag_names_that_start_with_char:
                if (t.lower().find(matchstr.lower()) == 0):
                    final_list.append(copy(t))
                if num_results > 0 and len(final_list) == num_results:
                    return final_list

        return final_list
 
    def __getitem__(self, i):
        if isinstance(i, int) or isinstance(i, slice):
            return self.__sorted_tags[i]
        else:
            try:
                return self.__tags_by_name[i]
            except KeyError:
                try:
                    return self.__tags_by_repr[i]
                except KeyError:
                    return self.__tags_by_str[i]
                
    def __setitem__(self, i, v):
        raise AttributeError("can't set item")
    
    def __delitem__(self, i):
        raise AttributeError("can't delete item")
    
    def __len__(self):
        return len(self.__sorted_tags)
    
    def __iter__(self):
        return self.__sorted_tags.__iter__()
    
    def __contains__(self, i):
        if isinstance(i, ctags_entry):
            i = repr(i)
        
        if i in self.__tags_by_repr:
            return True
        else:
            return False
        