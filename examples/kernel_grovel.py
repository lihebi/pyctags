import pyctags, os, time, sys

## This program takes over six minutes on an AMD Athlon 64 3000+ and 
## consumes over 1GB of RAM.  It'd probably be significantly slower if less memory is
## is available.


srcdir = "../../temp extracts/linux-2.6.27"
if sys.platform.lower()[:len('linux')] == 'linux':
    srcdir = os.realpath("/usr/src/linux")

source_files = list()
extensions = ['.c', '.h', '.s']

cl = time.clock()
print ("Walking source tree %s..." % (srcdir))
for (dirpath, dirs, files) in os.walk(srcdir):
    for f in files:
        if f[-2:] in extensions:
            source_files.append(os.path.join(dirpath, f))
            
print ("%.2f seconds elapsed, found %d source files." % (time.clock() - cl, len(source_files)))
print ("This part will take a while.  I've seen it take five to eight minutes on my machine which isn't exactly tuff...")
cl = time.clock()
tf = pyctags.exuberant_ctags().generate_object(files=source_files, generator_options={"--fields" : "-sfk+Kn"})

print ("%d tags parsed in %.2f seconds." % (len(tf.tags), time.clock() - cl))
cl = time.clock()
names = pyctags.harvests.name_lookup_harvest()
names.process_tag_list(tf.tags)
print ("Name index took %.2f seconds to build." % (time.clock() - cl))

abs_names = names.starts_with('abs_')
print ("%d tags start with the letters abs.  They are:" % (len(abs_names)))

for name in abs_names:
    print ("\t%s" % (name))
print("\n")

print ("%d tags start with the letters abse.  They are:" % (len(names.starts_with("abse"))))

for name in names.starts_with("abse"):
    print ("\t%s" % (name))
print("\n")

print ("%d tags start with a case sensitive match to 'abse'" % (len(names.starts_with("abse", case_sensitive=True))))

for name in names.starts_with("abse", case_sensitive=True):
    print ("\t%s" % (name))
print("\n")
    
print ("Or there's %d tags that start with a case sensitive mach to 'absE':" % (len(names.starts_with("absE", case_sensitive=True))))
for name in names.starts_with("absE", case_sensitive=True):
    print ("\t%s" % (name))

print ("Wait a little more...")
kind_harvest = pyctags.harvests.kind_harvest()
kind_harvest.process_tag_list(tf.tags)
kind_dict = kind_harvest.retrieve_data()

kinds_by_name = pyctags.harvests.by_name_harvest()
kinds_by_name.process_tag_list(kind_dict['struct'])
struct_name_dict = kinds_by_name.retrieve_data()

print("\nIf you felt like it, you could find out that the first (and only) struct that's called 'frag' is in file %s on line %d." % (struct_name_dict['frag'][0].file, struct_name_dict['frag'][0].line_number))
