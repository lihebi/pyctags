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
Exuberant Ctags (U{http://ctags.sourceforge.net}) wrapper.

This module uses the subprocess.Popen function.  Users of this module could pass arbitrary commands to the system.
"""
import subprocess, os
from copy import copy
from pyctags.ctags_base import ctags_base, VersionException
from pyctags.kwargs_validator import the_validator as validator


class exuberant_ctags(ctags_base):
    """
    Wraps the Exuberant Ctags program.  U{http://ctags.sourceforge.net}
    
    The B{generate_tags} and B{generate_tagfile} methods will accept custom command line parameters for exuberant ctags via the generator_options keyword dict.
    The Exuberant Ctags output flags (-f and -o) are reserved for internal use and will trigger an exception.
    """
    __extra_file_extensions = {}
    __version_opt = "--version"
    __list_kinds_opt = "--list-kinds"
    __argless_args = ["--version", "--help", "--license", "--list-languages", 
        "-a", "-B", "-e", "-F", "-n", "-N", "-R", "-u", "-V", "-w", "-x"]
    __default_opts = {"-L" : "-", "-f" : "-"}
    __exuberant_id = "exuberant ctags"
    __supported_versions = ["5.7", "5.6b1"]
    __warning_str = "ctags: Warning:"
    
    def __init__(self, *args, **kwargs):
        """
        Wraps the Exuberant Ctags program.
            - B{Keyword Arguments:}
                - B{tag_program:} (str) path to ctags executable, or name of a ctags program in path
                - B{files:} (sequence) files to process with ctags
        """
        valid_kwargs = ['tag_program', 'files']
        validator.validate(kwargs.keys(), valid_kwargs)

        self.__version = None
        self.language_info = None

        ctags_base.__init__(self, *args, **kwargs)

    def __process_kinds_list(self, kinds_list):
        d = dict()
        key = ""
        for k in kinds_list:
            if len(k):
                if k[0].isspace():
                    if len(key):
                        kind_info = k.strip().split('  ')
                        if len(kind_info) > 2:
                            raise ValueError("Kind information is in an unexpected format.")
                        d[key][kind_info[0]] = kind_info[1]
                else:
                    key = k.strip().lower()
                    if key not in d:
                        d[key] = dict()
    
        return d


    def _query_tag_generator(self, path):
        """
        Gets Exuberant Ctags program information.
        @raise ValueError: No valid ctags executable set.
        @raise TypeError: Executable is not Exuberant Ctags.
        """
        
        shell_str = path + ' ' + self.__version_opt

        p = subprocess.Popen(shell_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        outstr = out.decode()
        if outstr.lower().find(self.__exuberant_id) < 0:
            raise TypeError("Executable file " + self._executable_path + " is not Exuberant Ctags")
        
        comma = outstr.find(',')
        self.__version = outstr[len(self.__exuberant_id):comma].strip()
        if self.__version not in self.__supported_versions:
            raise VersionException("Version " + self.__version + " isn't known to work, but might.")

        # find out what this version of ctags supports in terms of language and kinds of tags
        p = subprocess.Popen(path + ' ' + self.__list_kinds_opt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        
        self.language_info = self.__process_kinds_list(out.decode().splitlines())
        
    def _dict_to_args(self, gen_opts):
        """
        Converts from a dict with command line arguments to a string to feed exuberant ctags on the comand line.
        @param gen_opts: command line arguments, key=argument, value=setting
        @type gen_opts: dict
        @rtype: str
        """
        
        if '--langmap' not in gen_opts and len(self.__extra_file_extensions):
            lang_opts = ""
            for lang, exts in self.__extra_file_extensions.iteritems():
                lang_opts += lang.lower() + ":+"
                for ext in exts:
                    lang_opts += ext
            gen_opts['--langmap'] = lang_opts
            
        # because yargs sounds like a pirate
        yargs = ""
        for k, v in gen_opts.items():
            if k in self.__argless_args:
                yargs += k + ' '
                continue
            if k[0:2] == '--':
                # long opt
                yargs += k + '=' + v
            elif k[0] == '-':
                # short opt
                yargs += k + ' ' + v + ' '
                
        return yargs
    
    def _prepare_to_generate(self, kw):
        """
        Prepares parameters to be passed to exuberant ctags.
        """
        input_file_override = False
        
        if 'generator_options' in kw:
            if '-f' in kw['generator_options'] or '-o' in kw['generator_options']:
                raise ValueError("The options -f and -o are used internally.")
            if '-L' in kw['generator_options']:
                input_file_override = True
        
        if 'tag_program' in kw:
            if self.ctags_executable(kw['tag_program']):
                self._executable_path = kw['tag_program']
        
        if 'files' in kw:
            self._file_list = list(kw['files'])
        
        if not self._executable_path:
            if self.ctags_executable('ctags'):
                self._executable_path = 'ctags'
            else:
                raise ValueError("No ctags executable set.")

        gen_opts = copy(self.__default_opts)
        if 'generator_options' in kw:
            gen_opts.update(kw['generator_options'])
            
        file_list = ''
        if not input_file_override:
            for f in self._file_list:
                file_list += f + "\n"
                
        return (gen_opts, file_list)
        
    
    def generate_tags(self, **kwargs):
        """ 
        Parses source files into list of tags.
            - B{Keyword Arguments:}
                - B{tag_program:} (str) path to ctags executable, or name of a ctags program in path
                - B{files:} (sequence) files to process with ctags
                - B{generator_options:} (dict) command-line options to pass to ctags program
            - B{Returns:}
                - len 2 tuple; (list of ctags str, ctags format)
            @raise ValueError: ctags executable path not set, fails execution
            
        """
        valid_kwargs = ['tag_program', 'files', 'generator_options']
        validator.validate(kwargs.keys(), valid_kwargs)
        
        (gen_opts, file_list) = self._prepare_to_generate(kwargs)
        tag_args = self._dict_to_args(gen_opts)
        
        self.command_line = self._executable_path + ' ' + tag_args
        p = subprocess.Popen(self.command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate(input=file_list.encode())
        
        if p.returncode != 0:
            raise ValueError("Ctags execution did not complete, return value: " + p.returncode + ".\nCommand line: " + self.command_line)
        
        results = out.decode().splitlines()
        
        # clean out anything that isn't formatted like a tag
        idxs = []
        i = 0
        for r in results:
            if r[:len(self.__warning_str)] == self.__warning_str:
                idxs.append(i)
            i += 1

        # reverse the list so we don't mess up index numbers as we're deleting
        idxs.sort(reverse=True)
        for i in idxs:
            del results[i]

        return results

    def generate_tagfile(self, output_file, **kwargs):
        """ 
        Generates tag file from list of files.
        @param output_file: File name and location to write tagfile.
        @type output_file: str
            - B{Keyword Arguments:}
                - B{tag_program:} (str) path to ctags executable, or name of a ctags program in path
                - B{files:} (sequence) files to process with ctags
                - B{generator_options:} (dict) options to pass to ctags program
            - B{Returns:}
                - (boolean) file written
        @raise ValueError: ctags executable path not set or output file isn't valid
            
        """
        valid_kwargs = ['tag_program', 'files', 'generator_options']
        validator.validate(kwargs.keys(), valid_kwargs)

        # exuberant ctags 5.7 chops 'def' off the beginning of variables, if it starts with def
        _default_output_file = 'tags'

        if 'generator_options' in kwargs:
            if '-e' in kwargs['generator_options']:
                _default_output_file.upper()

        if output_file:
            if output_file != "-":
                if os.path.isdir(output_file):
                    output_file = os.path.join(output_file, _default_output_file)
                else:
                    (head, tail) = os.path.split(output_file)
                    if len(head) == 0 and len(tail) == 0:
                        raise ValueError("No output file set")
                    if len(head) != 0:
                        if not os.path.isdir(head):
                            raise ValueError("Output directory " + head + " does not exist.")
        else:
            raise ValueError("No output file set")
        
        (gen_opts, file_list) = self._prepare_to_generate(kwargs)
        gen_opts['-f'] = '"' + output_file + '"'
        tag_args = self._dict_to_args(gen_opts)

        self.command_line = self._executable_path + ' ' + tag_args
        p = subprocess.Popen(self.command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate(input=file_list.encode())
        if (p.returncode == 0):
            return True
        return False
