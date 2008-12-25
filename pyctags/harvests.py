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

class harvest_kinds:
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

    