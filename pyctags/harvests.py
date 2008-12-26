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

from kwargs_validator import the_validator as validator
from copy import copy

class abstract_harvest:
    def __init__(self, *args, **kwargs):
        self._tag_file = None
    
    def __len__(self, *args, **kwargs):
        pass
    
    def feed(self, entry):
        pass
    
    def do_before(self):
        pass
    
    def do_after(self):
        pass
    
    def retrieve_data(self):
        pass

    def set_tagfile(self, tag_file):
        self._tag_file = tag_file
        

class kind_harvest(abstract_harvest):
    def __init__(self, *args, **kwargs):
        self.kinds = {}
    
    def __len__(self):
        return len(self.kinds)
    
    def feed(self, entry):
        if 'kind' in entry.extensions:
            # note: case sensitive output from exuberant ctags
            entkey = entry.extensions['kind']
            if entkey not in self.kinds:
                self.kinds[entkey] = list()
            self.kinds[entkey].append(entry)
    
    def retrieve_data(self):
        return self.kinds


class name_lookup_harvest(abstract_harvest):
    def __init__(self, *args, **kwargs):
        self.__unique_names = dict()
        self.__sorted_names = list()
        self.__name_index = dict()
    
    def __len__(self):
        return len(self.__sorted_names)
    
    def feed(self, entry):
        self.__unique_names[entry.name] = None
    
    def do_after(self):
        self.__sorted_names = list(self.__unique_names.keys())
        self.__sorted_names.sort()

        # don't need this any more
        self.__unique_names = dict()
        
        i = 0
        prev_char = self.__sorted_names[0][0]
        self.__name_index[prev_char] = {'first' : 0}
        for f in self.__sorted_names:
            if f[0] not in self.__name_index:
                self.__name_index[prev_char]['last'] = i - 1
                self.__name_index[f[0]] = {'first' : i}
                prev_char = f[0]
            i += 1
        self.__name_index[prev_char]['last'] = i

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
                return self.__sorted_names[0:num_results]
            return self.__sorted_names[:]

        if 'case_sensitive' in kwargs:
            if kwargs['case_sensitive']:
                case_sensitive = True

        tag_names_that_start_with_char = []
        
        if case_sensitive:
            if matchstr[0] not in self.__name_index:
                return []
        else:
            if matchstr[0].lower() not in self.__name_index and matchstr[0].upper() not in self.__name_index:
                return []
        
        if case_sensitive:
            idxs = self.__name_index[matchstr[0]]
            
            if idxs['first'] == idxs['last'] + 1:
                tag_names_that_start_with_char = self.__sorted_names[idxs['first']]
            else:
                tag_names_that_start_with_char = self.__sorted_names[idxs['first']:idxs['last'] + 1]
            
        else:
            if matchstr[0].lower() in self.__name_index:
                idxs = self.__name_index[matchstr[0].lower()]
                
                if idxs['first'] == idxs['last'] + 1:
                    tag_names_that_start_with_char = self.__sorted_names[idxs['first']]
                else:
                    tag_names_that_start_with_char = self.__sorted_names[idxs['first']:idxs['last'] + 1]

            if matchstr[0].upper() in self.__name_index:
                idxs = self.__name_index[matchstr[0].upper()]
                
                if idxs['first'] == idxs['last'] + 1:
                    tag_names_that_start_with_char += [self.__sorted_names[idxs['first']]]
                else:
                    tag_names_that_start_with_char += self.__sorted_names[idxs['first']:idxs['last'] + 1]
        
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
