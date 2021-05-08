#!/usr/bin/env python3

import ipol, iio

x = iio.read("good_lena.png")
y = ipol.lsd(x)
iio.write("lenseg.asc", y)

