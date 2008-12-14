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

"""
Exuberant Ctags (U{http://ctags.sourceforge.net}) wrapper.

This module uses the subprocess.Popen function.  Users of this module could pass arbitrary commands to the system.
"""
import subprocess, os
from copy import copy
from ctags_base import ctags_base, VersionException
from kwargs_validator import the_validator as validator


class exuberant_ctags(ctags_base):
    """
    Wraps the Exuberant Ctags program.  U{http://ctags.sourceforge.net}
    
    The B{generate_tags} and B{generate_tagfile} methods will accept custom command line parameters for exuberant ctags via the generator_options keyword dict.
    The Exuberant Ctags output flags (-f and -o) are reserved for internal use and will trigger an exception.
    """
    __extra_file_extensions = {}
    __version_opt = "--version"
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
        ctags_base.__init__(self, *args, **kwargs)
        self.__version = None

    def _query_tag_generator(self, path):
        """
        Gets Exuberant Ctags program information.
        @raise ValueError: No valid ctags executable set.
        @raise TypeError: Executable is not Exuberant Ctags.
        """
        

        shell_str = "%s %s" % (path, self.__version_opt)

        p = subprocess.Popen(shell_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        lines = p.stdout.readlines()

        if lines[0].lower().find(self.__exuberant_id) < 0:
            raise TypeError, "Executable file %s is not Exuberant Ctags" % (self._executable_path)

        comma = lines[0].find(',')
        self.__version = lines[0][len(self.__exuberant_id):comma].strip()
        if self.__version not in self.__supported_versions:
            raise VersionException, "Version %s isn't known to work, but might." % self.__version
        
    def _dict_to_args(self, gen_opts):
        """
        Converts from a dict with command line arguments to a string to feed exuberant ctags on the comand line.
        @param gen_opts: command line arguments, key=argument, value=setting
        @type gen_opts: dict
        @rtype: str
        """
        
        if '--langmap' not in gen_opts:
            lang_opts = ""
            if len(self.__extra_file_extensions):
                for lang, exts in self.__extra_file_extensions.iteritems():
                    lang_opts += "%s:+" % lang.lower()
                    for ext in exts:
                        lang_opts += "%s" % ext
            gen_opts['--langmap'] = lang_opts
            
        # because yargs sounds like a pirate
        yargs = ""
        for k, v in gen_opts.iteritems():
            if k in self.__argless_args:
                yargs += k + " "
                continue
            if k[0:2] == '--':
                # long opt
                yargs += k + "=%s " % v
            elif k[0] == '-':
                # short opt
                yargs += k + " %s " % v
                
        return yargs
    
    def _prepare_to_generate(self, kw):
        """
        Prepares parameters to be passed to exuberant ctags.
        """
        input_file_override = False
        
        if 'generator_options' in kw:
            if '-f' in kw['generator_options'] or '-o' in kw['generator_options']:
                raise ValueError, "The options -f and -o are used internally."
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
                raise ValueError, "No ctags executable set."

        gen_opts = copy(self.__default_opts)
        if 'generator_options' in kw:
            gen_opts.update(kw['generator_options'])
            
        file_list = ''
        if not input_file_override:
            for f in self._file_list:
                file_list += "%s\n" % f
                
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
        
        self.command_line = "%s %s" % (self._executable_path, tag_args)
        p = subprocess.Popen(self.command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate(input=file_list)
        
        if p.returncode != 0:
            raise ValueError, "Ctags execution did not complete, return value: %d.\nCommand line: %s" % (p.returncode, self.command_line)
        
        results = out.splitlines()
        
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

        default_output_file = 'tags'

        if 'generator_options' in kwargs:
            if '-e' in kwargs['generator_options']:
                default_output_file.upper()

        if output_file:
            if output_file != "-":
                if os.path.isdir(output_file):
                    output_file = os.path.join(output_file, default_output_file)
                else:
                    (head, tail) = os.path.split(output_file)
                    if len(head) == 0 and len(tail) == 0:
                        raise ValueError, "no output file set"
                    if len(head) != 0:
                        if not os.path.isdir(head):
                            raise ValueError, "output directory %s does not exist" % (head)
        else:
            raise ValueError, "no output file set"
        
        (gen_opts, file_list) = self._prepare_to_generate(kwargs)
        gen_opts['-f'] = '"%s"' % output_file
        tag_args = self._dict_to_args(gen_opts)

        self.command_line = "%s %s" % (self._executable_path, tag_args)
        p = subprocess.Popen(self.command_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate(input=file_list)
        if (p.returncode == 0):
            return True
        return False
