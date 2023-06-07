NAME phs
TITLE Pyramidal Horn Schunck
SRC http://www.ipol.im/pub/art/2013/20/phs_3.tar.gz

BUILD sed 's/uint16 /uint16_t /g' -i iio.c   # fix warning on tiff reader
BUILD make
BUILD cp horn_schunck_pyramidal $BIN/phs

INPUT a image
INPUT b image
OUTPUT out image

RUN phs $a $b $out
