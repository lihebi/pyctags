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
Python representation of ctags data elements.

This module uses the eval function, which will let package users execute arbitrary python code, if they want.
"""

from copy import copy
import os
from pyctags.kwargs_validator import the_validator as validator

_PYTHON_3000_ = True

import sys
if sys.version_info[0] < 3:
    _PYTHON_3000_ = False
    
_COMMENT_BEGIN_ = ';"'

class ctags_entry:
    """
    An entry in the tag file.
    """
    def __init__(self, *args, **kwargs):
        """
        A tag entry from ctags file. Initializes from keyword args.
        
            - B{Keyword Arguments:}
                - B{name}: (str) tag name
                - B{file}: (str) source file name
                - B{pattern}: (str) locator pattern for tag
                - B{line_number}: (int) locator line number
                - B{extensions}: (dict) extension fields
            - B{Raises:}
                - B{ValueError}: line_number or pattern isn't set, or a parameter type can't be transformed.
        """
        valid_kwargs = ['name', 'file', 'pattern', 'line_number', 'extensions']
        validator.validate(kwargs.keys(), valid_kwargs)

        self.name = None
        """ Tag name."""
        self.file = None
        """ Source file of tag."""
        self.pattern = None
        """ If not None, regular expression to locate this tag in self.file."""
        self.line_number = None
        """ If not None, line number to locate this tag in self.file."""
        self.extensions = None
        """ If not none, dict of extension fields embedded in comments in the tag entry, from exuberant ctags."""
        self.short_filename = None
        """ Short version of filename, used in str representation."""
        self.__rep = None
        
        entry = dict()
        if len(args) == 1:
            if len(kwargs):
                raise ValueError("multiple tag data found in init")

            if type(args[0]) == dict:
                entry = args[0]

            elif type(args[0]) == str or type(args[0]) == unicode:
                
                if args[0][0] == '{' and args[0][-1] == '}':

                    # security anyone?
                    entry = eval(args[0])

                else:
                    # bah!  uglies.
                    if _PYTHON_3000_:
                        argstr = args[0]
                    else:
                        argstr = unicode(args[0])

                    # this should be a tag line, could use some safety checking here though
                    (entry['name'], entry['file'], the_rest) = argstr.split('\t', 2)
    
                    extension_fields = None
    
                    if the_rest.find(_COMMENT_BEGIN_) > 0:
                        (locator, junk, extension_fields) = the_rest.rpartition(_COMMENT_BEGIN_)
                    else:
                        locator = the_rest
    
                    if locator.isdigit():
                        try:
                            entry['line_number'] = int(locator)
                        except ValueError:
                            raise ValueError("Line number locator found for tag, but can't be converted to integer")
                    else:
                        # should be a regex pattern
                        entry['pattern'] = locator
    
                    entry['extensions'] = {}
                    kind_arg_found = False
                    if extension_fields:
                        if extension_fields[0] == '\t':
    
                            # probably exuberant ctags format
                            extension_list = extension_fields[1:].split('\t')
                            for ext in extension_list:
                                if ':' in ext:
                                    (k, v) = ext.split(':', 1)
                                    entry['extensions'][k] = v
                                    if k == 'line' and 'line_number' not in entry:
                                        try:
                                            entry['line_number'] = int(v)
                                        except ValueError:
                                            raise ValueError("Extended tag 'line' found but can't be converted to integer.")
                                else:
                                    if kind_arg_found:
                                        raise ValueError("Unknown extended tag found.")
                                    else:
                                        entry['extensions']['kind'] = ext
                                        kind_arg_found = True
                
        elif len(kwargs):
            entry = kwargs
            
        if 'file' in entry:
            self.file = str(entry['file'])
        else:
            raise ValueError("'file' parameter is required")

        if 'name' in entry:
            self.name = str(entry['name'])
        else:
            raise ValueError("'name' parameter is required")

        if 'pattern' in entry:
            self.pattern = str(entry['pattern'])

        if 'line_number' in entry:
            self.line_number = int(entry['line_number'])

        if not self.line_number and not self.pattern:
            raise ValueError("No valid locator for this tag.")

        if 'extensions' in entry:
            self.extensions = entry['extensions']


        self.__rep = entry

    def __repr__(self):
        return str(self.__rep)
        
    def __str__(self):
        idx = self.file.rfind('/')
        
        if idx == -1:
            idx = self.file.rfind("\\")
        
        short_fn = self.file[idx + 1:]

        if self.name:
            return self.name + ':' + short_fn + ':' + str(self.line_number)
        else:
            return "Unnamed tag."
        
    def __eq__(self, other):
        return (repr(self) == repr(other))
    
    def __ne__(self, other):
        return (repr(self) != repr(other))
