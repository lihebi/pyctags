#!/usr/bin/env python
import sys

try:
    import pyctags
except ImportError:
    # so you can run the sample without installing pyctags
    sys.path.append("../")

from pyctags import exuberant_ctags, ctags_file
import os

source_files = list()

for (dirpath, dirs, files) in os.walk("../"):
    for f in files:
        if f[-3:] == '.py':
            source_files.append(os.path.join(dirpath, f))

generator = exuberant_ctags(files=source_files)
list_o_tags = generator.generate_tags(generator_options={'--fields' : '+n'})

tags = ctags_file(list_o_tags)

print "Found %d tags in %d source files." % (len(tags), len(source_files))

# this fetches unique names
letter_tags = tags.starts_with('c')
print "%d of them start with the letter c." % (len(letter_tags))

for t in letter_tags:
    # there can be more than one occurance of a particular name
    for t2 in tags[t]:
        print "\t%s is in %s on line %s." % (t2.name, t2.file, t2.line_number)
