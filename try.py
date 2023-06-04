#!/usr/bin/env python

import iio                      # functions for image input/output
import ipol                     # interface to ipol algorithms

x = iio.read("test/lenac.png")  # read input image
y = ipol.scb(x)                 # apply IPOL's Simplest Color Balance algorithm
iio.write("lena_scb.png", y)    # write output image

