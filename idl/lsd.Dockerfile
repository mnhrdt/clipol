NAME lsd
TITLE Line Segment Detector
SRC http://www.ipol.im/pub/art/2012/gjmr-lsd/lsd_1.6.zip

INPUT in image pgm
OUTPUT out image npy

BUILD make
BUILD cp lsd $BIN

#RUN convert $in x.pgm
RUN lsd x.pgm $out
