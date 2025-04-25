import setuptools

def data_files():
	import glob
	return glob.glob("idl/*.Dockerfile")

setuptools.setup(
	name = "ipol",
	version = "9",
	author = "Enric Meinhardt-Llopis",
	author_email = "enric.meinhardt@ens-paris-saclay.fr",
	description = "python interface to some IPOL journal algorithms",
	url = "https://git.sr.ht/~coco/clipol",
	license = "AGPL-3.0",
	classifiers = [
		"Operating System :: OS Independent",
		"Topic :: Scientific/Engineering :: Image Processing",
		"Topic :: Scientific/Engineering :: Mathematics"
		],
	py_modules = ["ipol"],
	data_files = [("idl", data_files())]
)
