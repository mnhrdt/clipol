#!/usr/bin/env python3

# global configuration options
DEBUG_LEVEL = 0
IPOL_CACHE = "/tmp/ipol/cache"
IPOL_CONFIG = "/tmp/ipol/config"
#IPOL_CACHE = "%s/.cache/ipol" % os.path.expanduser("~")
#IPOL_CONFIG = "%s/.config/ipol" % os.path.expanduser("~")
#IPOL_CONFIG = "/home/coco/src/clipol"
def setup_global_variables():
	global IPOL_CACHE
	global IPOL_CONFIG

	# cache is easy
	import os
	IPOL_CACHE = "%s/.cache/ipol" % os.path.expanduser("~")

	# config is harder...
	# if ~/.config/ipol/idl/lsd.Dockerfile exists, use that folder
	# if there's an idl folder besides this ipol.py, use that
	# otherwise, use site.USER_BASE

	import site
	IPOL_CONFIG = site.USER_BASE
	x = os.path.dirname(os.path.realpath(__file__))
	if os.path.exists(f"{x}/idl/lsd.Dockerfile"):
		IPOL_CONFIG = x
	x = "%s/.config/ipol" % os.path.expanduser("~")
	if os.path.exists(f"{x}/idl/lsd.Dockerfile"):
		IPOL_CONFIG = x

	# hack: google colab does not respect USER_BASE and the path is fixed
	import sys
	if "google.colab" in sys.modules:
		IPOL_CONFIG = "/usr/local"


setup_global_variables()


# arbitrary names for temporary files
BUILD_SCRIPT_NAME = "_ipol_build_script.sh"
CALL_SCRIPT_NAME = "_ipol_call_script.sh"


# print to stderr
def dprint(*args, **kwargs):
	if DEBUG_LEVEL > 0:
		import sys
		print(*args, file=sys.stderr, **kwargs)

# print an error message and exit
def fail(msg):
	import sys
	dprint("ERROR: %s" % msg)
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

	dprint(f"IPOL: ipol_parse_idl f={f}")

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
	f = f if f.endswith(".Dockerfile") else f"{f}.Dockerfile"
	for l in open(f, "r").read().split("\n"):
		l = l.partition(" #")[0].strip()    # remove comments
		if len(l) < 4: continue
		if l[0] == "#": continue
		k = l.partition(" ")[0]
		v = l.partition(" ")[2].lstrip(" ")
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


# check whether an article is already unzipped and built
def ipol_is_built(p):
	import os
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


# auxiliary function to get the SRCDIR of an article (with some heuristics)
def get_srcdir(p):
	import os
	name = p['NAME']
	mysrc = "%s/%s/src" % (IPOL_CACHE, name)
	l = os.listdir(mysrc)
	if len(l) == 1:
		return f"{mysrc}/{l[0]}"
	else:
		return mysrc

def print_stderr_and_stdout_in_cwd(s, d):
	import pathlib
	p = pathlib.Path(f"{d}/stderr.txt")
	if p.exists() and p.stat().st_size > 0:
		dprint(f"{s} stderr:")
		for l in open(f"{d}/stderr.txt", "r").read().split("\n"):
			dprint(f"{l}")
	p = pathlib.Path(f"{d}/stdout.txt")
	if p.exists() and p.stat().st_size > 0:
		dprint(f"{s} stdout:")
		for l in open(f"{d}/stdout.txt", "r").read().split("\n"):
			dprint(f"{l}")



# download, build and cache an ipol code
def ipol_build_interface(p):
	import os
	import shutil
	import subprocess
	dprint(f"IPOL: ipol_build_interface")
	dprint("building interface \"%s\"" % p)
	name = p['NAME']
	srcurl = p['SRC']
	dprint("get \"%s\" code from \"%s\"" % (name,srcurl))
	mycache = "%s/%s" % (IPOL_CACHE, name)
	dprint("cache = \"%s\"" % mycache)
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

	srcdir = get_srcdir(p)
	bindir = "%s/bin" % mycache
	dprint(f"srcdir = {srcdir}")
	dprint(f"bindir = {bindir}")

	popd = os.getcwd()
	os.chdir(srcdir)
	script = "%s/%s" % (srcdir, BUILD_SCRIPT_NAME)
	with open(script, "w") as f:
		f.write("export BIN=%s\n" % bindir)
		f.writelines(["%s\n" % i  for i in p['BUILD']])
	subprocess.call(f". {script} >_build_stdout.txt 2>_build_stderr.txt", shell=True)
	print_stderr_and_stdout_in_cwd(f"{script}", srcdir)
	os.chdir(popd)

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
def ipol_matchpars(p, pos_args, named_args):
	dprint(f"matchpars pos_args={pos_args}")
	dprint(f"matchpars named_args={named_args}")
	args_dict = {}
	for x in named_args:
		a,_,b = x.partition("=")
		args_dict[a] = b
	r = {}
	cx = 0
	for k,v in p['INPUT'].items():
		a,b = v
		dprint(f"k,v,a,b={k},{v},{a},{b}")
		if len(b) == 0 or a == "image":
			r[k] = pos_args[cx]
			cx += 1
		else:
			r[k] = args_dict[k] if k in args_dict else b
	for k,v in p['OUTPUT'].items():
		a,b = v
		if len(b) == 0 or a == "image":
			r[k] = pos_args[cx]
			cx += 1
		else:
			r[k] = args_dict[k] if k in args_dict else b
	return r

# produce a unique MD5 string
def get_random_key():
	import uuid
	return uuid.uuid4().hex.upper()

# perform the actual subprocess call to the IPOL code (pure shell)
def ipol_call_matched(p, m):
	import os

	dprint(f"IPOL: ipol_call_matched")

	# 1. create a sanitized run environment
	if not ipol_is_built(p):
		ipol_build_interface(p)
	name = p['NAME']
	mycache = "%s/%s" % (IPOL_CACHE, name)
	bindir = "%s/bin" % mycache

	key = get_random_key()
	dprint("key = %s" % key)
	dprint("m = %s" % m)
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
			f = f"in_{cx}.{ext}"
			in_pairs.append((m[k], f"{tmpdir}/{f}"))
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
			f = f"out_{cx}.{ext}"
			out_pairs.append((f"{tmpdir}/{f}", m[k]))
			m[k] = f
			cx = cx + 1
	dprint(f"in_pairs={in_pairs}")
	dprint(f"out_pairs={out_pairs}")
	dprint(f"m={m}")
	import iio
	for i in in_pairs:
		dprint(f"iion {i[0]} {i[1]}")
		x = iio.read(i[0])
		iio.write(i[1], x)


	# 3. write the call script into the sanitized run environement
	callscript = "%s/%s" % (tmpdir, CALL_SCRIPT_NAME)
	with open(callscript, "w") as f:
		from string import Template
		f.write("export PATH=%s:$PATH\n" % bindir)
		f.write("export SRCDIR=%s\n" % get_srcdir(p))
		f.writelines(["%s\n" % Template(i).safe_substitute(m)
		              for i in p['RUN']])

	# 4. run the call script
	from subprocess import call
	call(f". {callscript} >stdout.txt 2>stderr.txt", shell=True, cwd=tmpdir)
	print_stderr_and_stdout_in_cwd(f"{callscript}", tmpdir)

	# 5. recover the output data
	for i in out_pairs:
		dprint(f"iion {i[0]} {i[1]}")
		x = iio.read(i[0])
		iio.write(i[1], x)


# run an IPOL article with the provided input and parameters
# [this function is used for the command-line shell interface]
#
# Note: this function is mostly parameter juggling, the actuall call is
# deferred to the function "ipol_call_matched"
def main_article(argv):
	x = argv[0]
	dprint(f"IPOL: main_article")
	dprint("Article id = %s" % x)
	x_idl = "%s/idl/%s" % (IPOL_CONFIG, x)
	x_cache = "%s/%s" % (IPOL_CACHE, x)
	p = ipol_parse_idl(x_idl)
	dprint("Is built = %s" % str(ipol_is_built(p)))
	if not ipol_is_built(p):
		ipol_build_interface(p)
	# compulsory, positional parameters
	#nb_in, nb_out = ipol_signature(p)
	#dprint("signature = %d %d" % (nb_in, nb_out))
	args_nop,args_yes = ipol_partition_args(argv[1:])

	## TODO: hide these details under the "--raw" option
	#hypobin = "%s/bin/%s" % (x_cache, x)
	#if len(args_nop) == 0 and os.path.exists(hypobin):
	#	subprocess.run(hypobin, shell=True)
	#	return 0

	dprint(f"p = {p}")
	dprint("args_nop = %s" % args_nop)
	dprint("args_yes = %s" % args_yes)
	mp = ipol_matchpars(p,args_nop,args_yes)
	dprint("matched args:\n%s" % mp)
	#if len(args_nop) == nb_in + nb_out:
	ipol_call_matched(p, mp)
	#else:
	#	fail("signatures mismatch")
	return 0



# this function calls the article "x" with the given arguments
# [it is used from the import-able python interface]
# NOTE: it could be refactored with the functions "main_article" and
# "ipol_call_matched" above, because most of the logic is the same
#
# here the (non-optional) outputs are returned as a tuple
def run_article(x, *args):

	args, kwargs = (args[0], args[1]) # I don't understand why this works
	dprint(f"IPOL: run_article x={x}")
	dprint(f"len(args)={len(args)}")
	dprint(f"kwargs={kwargs.keys()}")
	dprint(f"going to run {x}(args, {kwargs})")
	p = ipol_parse_idl(f"{IPOL_CONFIG}/idl/{x}")
	if not ipol_is_built(p):
		ipol_build_interface(p)
	#args_nop,args_yes = ipol_partition_args(argv[1:])
	#dprint(f"p = {p}")
	#dprint("args_nop = %s" % args_nop)
	#dprint("args_yes = %s" % args_yes)
	#mp = ipol_matchpars(p,args_nop,args_yes)
	#print("matched args:\n%s" % mp)

	# 0.1. populate dictionary m with default input parameter values
	m = {}
	for k,v in p['INPUT'].items():
		a,b = v     # (type,type-complement) for example (image,png)
		if a == "number" or a == "string" and len(b) > 0:
			m[k] = b
	dprint(f"default m={m}")
	# 0.2. add given arguments from kwargs
	for k,v in kwargs.items():
		m[k] = v
	dprint(f"updated m={m}")



	# 1. create a sanitized run environment
	name = p['NAME']
	mycache = "%s/%s" % (IPOL_CACHE, name)
	bindir = "%s/bin" % mycache
	key = get_random_key()
	dprint("key = %s" % key)
	tmpdir = "%s/tmp/%s" % (mycache, key)
	import os
	os.makedirs(tmpdir)

	# 2. write the input ndarrays into the run environment
	in_pairs = [] # correspondence between ndarrays(indices) and filenames
	cx = 0
	for k,v in p['INPUT'].items():
		a,b = v     # (type,type-complement) for example (image,png)
		if a == "image":
			ext = "png" # default file extension
			if len(b) > 0:
				ext = b
			f = f"in_{cx}.{ext}"
			in_pairs.append((cx, f"{tmpdir}/{f}"))
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
			f = f"out_{cx}.{ext}"
			out_pairs.append((f"{tmpdir}/{f}", cx))
			m[k] = f
			cx = cx + 1
	out_nb = cx
	dprint(f"in_pairs={in_pairs}")
	dprint(f"out_pairs={out_pairs}")
	dprint(f"out_nb={out_nb}")
	import iio
	for i in in_pairs:
		idx = i[0]
		fname = i[1]
		dprint(f"going to write args[{idx}] into file {fname}")
		iio.write(fname, args[idx])

	# 3. write the call script into the sanitized run environement
	callscript = "%s/%s" % (tmpdir, CALL_SCRIPT_NAME)
	with open(callscript, "w") as f:
		from string import Template
		f.write("export PATH=%s:$PATH\n" % bindir)
		f.write("export SRCDIR=%s\n" % get_srcdir(p))
		f.writelines(["%s\n" % Template(i).safe_substitute(m)
		              for i in p['RUN']])

	# 4. run the call script
	from subprocess import call
	call(f". {callscript} >stdout.txt 2>stderr.txt", shell=True, cwd=tmpdir)
	print_stderr_and_stdout_in_cwd(f"{callscript}", tmpdir)

	# 5. recover the output data into out_nb ndarrays
	outs = [] # list of output ndarrays
	for i in out_pairs:
		x = iio.read(i[0])
		outs.append(x)

	if len(outs) > 1:
		return tuple(outs)
	else:
		return outs[0]

# perform the necessary magic to define the article "x" programmatically note:
# the corresponding idl file is parsed, but the article code is not downloaded
# and compiled.  This happens upon the first call of the interface
def export_article_interface(x):
	p = ipol_parse_idl(f"{IPOL_CONFIG}/idl/{x}")
	__import__(__name__).__dict__[x] = lambda *a, **k : run_article(x, a, k)
	globals()[x].__doc__ = p["TITLE"]  # TODO: beautify docstring


def main_status():
	import os
	config_dir = IPOL_CONFIG
	config_idl = "%s/idl" % config_dir
	idls = os.listdir(config_idl)
	print('Config dir "%s" contains %d programs' % (config_idl, len(idls)))
	cache_dir = IPOL_CACHE
	cacs = os.listdir(cache_dir)
	print('Cache dir "%s" contains %d programs' % (cache_dir, len(cacs)))
	return 0

def main_list():
	import os
	config_dir = IPOL_CONFIG
	config_idl = "%s/idl" % config_dir
	idls = os.listdir(config_idl)
	for x in idls:
		p = ipol_parse_idl("%s/%s" % (config_idl, x))
		print("\t%s\t%s" % (p['NAME'], p['TITLE']))
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

# TODO: add option to dump the idl into ddl (copy-pasteable into the cp)

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

def main_buildall():
	import os
	idls = os.listdir(f"{IPOL_CONFIG}/idl")
	DEBUG_LEVEL = 1
	for x in idls:
		p = ipol_parse_idl(f"{IPOL_CONFIG}/idl/{x}")
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
	if sys.argv[1] == "buildall":
		return main_buildall() if len(sys.argv) == 2 else 1
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
if __name__ == "__main__":
	dprint(f"IPOL: entering shell interface")
	dprint(f"IPOL_CONFIG = {IPOL_CONFIG}")
	dprint(f"IPOL_CACHE = {IPOL_CACHE}")
	import sys
	sys.dont_write_bytecode = True
	sys.exit(main())

# ipol.py: the import-able interface
if __name__ == "ipol":
	dprint(f"IPOL: entering importable interface")
	dprint(f"IPOL_CONFIG = {IPOL_CONFIG}")
	dprint(f"IPOL_CACHE = {IPOL_CACHE}")
	#available_idls = ("scb", "lsd")  # TODO: traverse the idl folder
	import os
	idls = os.listdir(f"{IPOL_CONFIG}/idl")
	idls = [ x[:-11] if x.endswith(".Dockerfile") else x for x in idls ]
	for i in idls:
		export_article_interface(i)


# API
version = 9

# vim: sw=8 ts=8 sts=0 noexpandtab:
