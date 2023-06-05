import setuptools

setuptools.setup(
	name = "ipol",
	version = "1",
	author = "Enric Meinhardt-Llopis",
	author_email = "enric.meinhardt@ens-paris-saclay.fr",
	description = "python interface to some IPOL journal algorithms",
	url = "https://git.sr.ht/~coco/clipol",
	classifiers = [
		"Operating System :: OS Independent",
		"License :: OSI Approved :: GNU Affero General Public License v3",
		"Topic :: Scientific/Engineering :: Image Processing",
		"Topic :: Scientific/Engineering :: Mathematics"
		],
	py_modules = ["ipol"]
)

