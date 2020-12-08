#!/usr/bin/env python3

import ipol, iio

x = iio.read("lenac.png")
y = ipol.scb(x)
#y = ipol.scb(x, Smin=20, Smax=20)
iio.write("good_lena2.png", y)

