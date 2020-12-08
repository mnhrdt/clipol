#!/usr/bin/env python3

# imports
import os   # TODO: remove this global import

# global configuration options
IPOL_CACHE = "%s/.cache/ipol" % os.path.expanduser("~")
#IPOL_CONFIG = "%s/.config/ipol" % os.path.expanduser("~")
IPOL_CONFIG = "/home/coco/src/clipol"

# arbitrary names for temporary files
BUILD_SCRIPT_NAME = "_ipol_build_script.sh"
CALL_SCRIPT_NAME = "_ipol_call_script.sh"


# print an error message and exit
def fail(msg):
	import sys
	print("ERROR: %s" % msg)
	sys.exit(42)

# idl spec:
#	NAME <id>
#	TITLE <unquoted-string-max-68-chars>
#	SRC <url>                             # where to get the source code
#	BUILD <command-line>                  # build instructions
#	INPUT <id> <type>                     # obligatory input argument
#	INPUT <id> <type> <default-value>     # optional input argument
#	OUTPUT <id> <type>                    # obligatory output argument
#	OUTPUT <id> <type> optional           # optional output argument
#	RUN <command-line>                    # run instructions
#
#	<id> := string without spaces
#	<type> := <type-name>
#	<type> := <type-name>:<type-modifier>
#	<type-name> := {image|number|string}
#	<type-modifier> := {pgm|ppm|png|...}


# parse the named ipol file and return a dictionary with the acquired data
def ipol_parse_idl(f):
	"""
	Read an IPOL interface description from file "f"
	(newer version, with Dockerfile-like syntax)
	"""

	# the variable "p" is a dictionary containing the parsed IDL file
	p = {}

	# There are three types of values in this dictionary.
	# 1. the "singular_entries" are strings (NAME, SRC, etc)
	# 2. the "linewise_entries" are lists of strings (RUN, BUILD)
	# 3. the keyed sections are dictionaries of k,v pairs (INPUT, OUTPUT)
	singular_entries = ("NAME", "TITLE", "SRC", "AUTHORS")
	linewise_entries = ("RUN", "BUILD")
	keyed_sections = ("INPUT", "OUTPUT")

	# parse the input file into the tree "p"
	for l in open(f"{f}.Dockerfile", "r").read().split("\n"):
		l = l.partition("#")[0].strip()    # remove comments
		if len(l) < 4: continue
		k = l.partition(" ")[0]
		v = l.partition(" ")[2]
		if k in singular_entries:
			p[k] = v
		else:
			p.setdefault(k,[]).append(v)

	# turn the keyed sections intro key,value pairs
	# the "key" is the ID of the parameter
	# the "value" is a 2-tuple (type, defaultvalue/type)
	# "type" is one of "image,number,string"
	for i in keyed_sections:
		w = {}
		for l in p[i]:
			# todo: directly split into 2 or 3 substrings
			k = l.partition(" ")[0]
			v = l.partition(" ")[2]
			v1 = v.partition(" ")[0]
			v2 = v.partition(" ")[2]
			w[k] = (v1, v2)
		p[i] = w
	return p


# parse the named ipol file and return a dictionary with the acquired data
def ipol_parse_idl_old(f):
	"""
	Read an IPOL interface description from file "f"
	(old version, with .ini-like file format)
	"""

	# tree with the parsed information
	p = {}

	# current config section
	c = None
	textual_sections = ("build", "run")

	# parse the input file into the tree "p"
	for k in open(f, "r").read().split("\n"):
		k = k.partition("#")[0].strip()
		if len(k) < 2: continue
		if len(k) > 3 and k[0] == "[" and k[-1] == "]":
			c = k[1:-1]
			if c in textual_sections:
				p[c] = []
			else:
				p[c] = {} #collections.OrderedDict()
		else:
			if c in textual_sections:
				p[c].append(k)
			else:
				key = k.partition("=")[0].strip()
				val = k.partition("=")[2].strip()
				p[c][key] = val
	return p

# download, build and cache an ipol code
def ipol_build_interface(p):
	import shutil
	import subprocess
	print("building interface \"%s\"" % p)
	name = p['NAME']
	srcurl = p['SRC']
	print("get \"%s\" code from \"%s\"" % (name,srcurl))
	mycache = "%s/%s" % (IPOL_CACHE, name)
	print("cache = \"%s\"" % mycache)
	if os.path.exists(mycache):
		shutil.rmtree(mycache)
	os.makedirs(mycache)
	os.makedirs("%s/dl" % mycache)
	os.makedirs("%s/src" % mycache)
	os.makedirs("%s/bin" % mycache)
	os.makedirs("%s/tmp" % mycache)

	os.system("wget -P %s/dl %s" % (mycache, srcurl))
	mysrc = os.listdir("%s/dl" % mycache)[0]
	shutil.unpack_archive("%s/dl/%s" % (mycache,mysrc), "%s/src" % mycache)

	l = os.listdir("%s/src" % mycache)
	if len(l) != 1:
		fail("more than one file! %s" % l)
	srcdir = "%s/src/%s" % (mycache, l[0])
	bindir = "%s/bin" % mycache
	os.chdir(srcdir)
	buildscript = "%s/%s" % (srcdir, BUILD_SCRIPT_NAME)
	with open(buildscript, "w") as f:
		f.write("export BIN=%s\n" % bindir)
		f.writelines(["%s\n" % i  for i in p['BUILD']])
	subprocess.call(". %s" % buildscript, shell=True)

def ipol_is_built(p):
	name = p['NAME']
	mycache = "%s/%s" % (IPOL_CACHE, name)
	if not os.path.exists(mycache):
		return False
	bindir = "%s/bin" % mycache
	if not os.path.exists(bindir):
		return False
	if len(os.listdir(bindir)) < 1:
		return False
	return True

def ipol_signature(p):
	nb_in = 0
	nb_out = 0
	for k,v in p['INPUT'].items():
		#a,_,b = tuple(x.strip() for x in v.partition(":"))
		#print("\tinpupa k(%s) a(%s) b(%s)" % (k,v[0],v[1]))
		if len(v[1]) == 0:
			nb_in += 1
	for k,v in p['OUTPUT'].items():
		#a,_,b = tuple(x.strip() for x in v.partition(":"))
		#print("\toutpupa k(%s) a(%s) b(%s)" % (k,v[0],v[1]))
		if len(v[1]) == 0:
			nb_out += 1
	return nb_in,nb_out

# split list of strings according to whether they contain "=" or not
def ipol_partition_args(l):
	equal_yes = [x for x in l if "="     in x]
	equal_nop = [x for x in l if "=" not in x]
	return (equal_nop, equal_yes)

# returns a dictionary of replacements
def ipol_matchpars(p,pos_args,named_args):
	args_dict = {}
	for x in named_args:
		a,_,b = x.partition("=")
		args_dict[a] = b
	r = {}
	cx = 0
	for k,v in p['INPUT'].items():
		a,b = v
		if len(b) == 0:
			r[k] = pos_args[cx]
			cx += 1
		else:
			r[k] = args_dict[k] if k in args_dict else b
	for k,v in p['OUTPUT'].items():
		a,b = v
		if len(b) == 0:
			r[k] = pos_args[cx]
			cx += 1
		else:
			r[k] = args_dict[k] if k in args_dict else b
	return r

# produce a unique MD5 string
def get_random_key():
	import uuid
	return uuid.uuid4().hex.upper()

# perform the actual subprocess call to the IPOL code
def ipol_call_matched(p, m):

	# 1. create a sanitized run environment
	if not ipol_is_built(p):
		ipol_build_interface(p)
	name = p['NAME']
	mycache = "%s/%s" % (IPOL_CACHE, name)
	bindir = "%s/bin" % mycache

	key = get_random_key()
	print("key = %s" % key)
	print("m = %s" % m)
	tmpdir = "%s/tmp/%s" % (mycache, key)
	os.makedirs(tmpdir)

	# 2. copy the input data into the run environement
	# (note: in most cases this is an unnecessary overhead, but it allows
	# for a cleaner implementation)
	in_pairs = []  # correspondence between cli filenames and assigned names
	cx = 0
	for k,v in p['INPUT'].items():
		a,b = v     # (type,type-complement) for example (image,png)
		if a == "image":
			ext = "png" # default file extension
			if len(b) > 0:
				ext = b
			f = f"{tmpdir}/in_{cx}.{ext}"
			in_pairs.append((m[k], f))
			m[k] = f
			cx = cx + 1

	out_pairs = [] # correspondence between cli filenames and assigned names
	cx = 0
	for k,v in p['OUTPUT'].items():
		a,b = v     # (type,type-complement) for example (image,png)
		if a == "image":
			ext = "png" # default file extension
			if len(b) > 0:
				ext = b
			f = f"{tmpdir}/out_{cx}.{ext}"
			out_pairs.append((f, m[k]))
			m[k] = f
			cx = cx + 1
	print(f"in_pairs={in_pairs}")
	print(f"out_pairs={out_pairs}")
	print(f"m={m}")
	import iio
	for i in in_pairs:
		print(f"iion {i[0]} {i[1]}")
		x = iio.read(i[0])
		iio.write(i[1], x)


	# 3. write the call script into the sanitized run environement
	callscript = "%s/%s" % (tmpdir, CALL_SCRIPT_NAME)
	with open(callscript, "w") as f:
		from string import Template
		f.write("export PATH=%s:$PATH\n" % bindir)
		f.writelines(["%s\n" % Template(i).safe_substitute(m)
		              for i in p['RUN']])

	# 4. run the call script
	import subprocess
	subprocess.call("pwd;cat %s" % callscript, shell=True, cwd=tmpdir)
	subprocess.call(". %s" % callscript, shell=True, cwd=tmpdir)

	# 5. recover the output data
	for i in out_pairs:
		print(f"iion {i[0]} {i[1]}")
		x = iio.read(i[0])
		iio.write(i[1], x)


# run an IPOL article with the provided input and parameters
#
# Note: this function is mostly parameter juggling, the actuall call is
# deferred to the function "ipol_call_matched"
def main_article(argv):
	x = argv[0]
	#print("Article id = %s" % x)
	x_idl = "%s/idl/%s" % (IPOL_CONFIG, x)
	x_cache = "%s/%s" % (IPOL_CACHE, x)
	p = ipol_parse_idl(x_idl)
	#print("Is built = %s" % str(ipol_is_built(p)))
	if not ipol_is_built(p):
		ipol_build_interface(p)
	# compulsory, positional parameters
	nb_in, nb_out = ipol_signature(p)
	#print("signature = %d %d" % (nb_in, nb_out))
	args_nop,args_yes = ipol_partition_args(argv[1:])

	## TODO: hide these details under the "--raw" option
	#hypobin = "%s/bin/%s" % (x_cache, x)
	#if len(args_nop) == 0 and os.path.exists(hypobin):
	#	subprocess.run(hypobin, shell=True)
	#	return 0

	print("args_nop = %s" % args_nop)
	print("args_yes = %s" % args_yes)
	mp = ipol_matchpars(p,args_nop,args_yes)
	#print("matched args:\n%s" % mp)
	if len(args_nop) == nb_in + nb_out:
		ipol_call_matched(p, mp)
	else:
		fail("signatures mismatch")
	return 0

def main_status():
	config_dir = IPOL_CONFIG
	config_idl = "%s/idl" % config_dir
	idls = os.listdir(config_idl)
	print('Config dir "%s" /ontains %d programs' % (config_dir, len(idls)))
	cache_dir = IPOL_CACHE
	cacs = os.listdir(cache_dir)
	print('Cache dir "%s" contains %d programs' % (cache_dir, len(cacs)))
	return 0

def main_list():
	config_dir = IPOL_CONFIG
	config_idl = "%s/idl" % config_dir
	idls = os.listdir(config_idl)
	for x in idls:
		p = ipol_parse_idl("%s/%s" % (config_idl, x))
		print("\t%s\t%s" % (p['NAME'], p['LONGNAME']))
	return 0

def main_dump(x):
	config_dir = IPOL_CONFIG
	config_x = "%s/idl/%s" % (config_dir, x)
	p = ipol_parse_idl(config_x)
	print(p)
	return 0

def main_json(x):
	config_dir = IPOL_CONFIG
	config_x = "%s/idl/%s" % (config_dir, x)
	p = ipol_parse_idl(config_x)
	import json
	print(json.dumps(p, indent=8))
	return 0

def main_gron(x):
	config_dir = IPOL_CONFIG
	config_x = "%s/idl/%s" % (config_dir, x)
	p = ipol_parse_idl(config_x)
	import json
	print(json.dumps(p, indent=8))
	return 0

def main_info(x):
	config_dir = IPOL_CONFIG
	config_x = "%s/idl/%s" % (config_dir, x)
	p = ipol_parse_idl(config_x)
	print("NAME:\t\"%s\" %s" % (p["NAME"], p["TITLE"]))
	print("INPUT:", end="")
	for k,v in p['INPUT'].items():
		print("\t%s = %s" % (k,v))
	print("OUTPUT:", end="")
	for k,v in p['OUTPUT'].items():
		print("\t%s = %s" % (k,v))
	print("RUN:", end="")
	for l in p['RUN']:
		print("\t%s" % l)
	print("USAGE:\t%s" % p["NAME"], end="")
	for k,v in p['INPUT'].items():
		if len(v[1]) == 0:
			print(f" {k}", end="")
		else:
			print(" [%s=%s]" % (k,v[1]), end="")
	for k,v in p['OUTPUT'].items():
		if len(v[1]) == 0 or v[0] == "image":
			print(f" {k}", end="")
		else:
			print(" [%s=%s]" % (k,v[1]), end="")
	print("")
	return 0

def main_build(x):
	config_dir = IPOL_CONFIG
	config_x = "%s/idl/%s" % (config_dir, x)
	p = ipol_parse_idl(config_x)
	if not ipol_is_built(p):
		ipol_build_interface(p)
	return 0

# sub-commands:
#	list       list all the sub-commands available (default action)
#	status     print various global status statistics
#	dump id    dump the dictionary associated to sub-command "id"
#	info id    pretty-print the data associated to sub-command "id"
#	id         run the sub-command "id"

def main():
	import sys
	if len(sys.argv) < 2 or sys.argv[1] == "list":
		return main_list()
	if sys.argv[1] == "status":
		return main_status()
	if sys.argv[1] == "dump":
		return main_dump(sys.argv[2]) if len(sys.argv) == 3 else 1
	if sys.argv[1] == "gron":
		return main_gron(sys.argv[2]) if len(sys.argv) == 3 else 1
	if sys.argv[1] == "json":
		return main_json(sys.argv[2]) if len(sys.argv) == 3 else 1
	if sys.argv[1] == "info":
		return main_info(sys.argv[2]) if len(sys.argv) == 3 else 1
	if sys.argv[1] == "build":
		return main_build(sys.argv[2]) if len(sys.argv) == 3 else 1
	if len(sys.argv) == 2:
		return main_info(sys.argv[1])
	return main_article(sys.argv[1:])

# ipol.sh: the shell interface
if __name__ == '__main__':
	import sys
	sys.dont_write_bytecode = True
	sys.exit(main())

# ipol.py: the import-able interface







# vim: sw=8 ts=8 sts=0 noexpandtab:
