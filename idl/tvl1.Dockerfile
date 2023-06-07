NAME tvl1
TITLE TVL1 Optical Flow
SRC http://www.ipol.im/pub/art/2013/26/tvl1flow_3.tar.gz

BUILD sed 's/uint16 /uint16_t /g' -i iio.c   # fix warning on tiff reader
BUILD make
BUILD cp tvl1flow $BIN

BUILD:OpenBSD make CC="cc -std=c99" OMPFLAGS="-DDISABLE_OMP"
BUILD:OpenBSD cp tvl1flow $BIN

INPUT a image png
INPUT b image png
OUTPUT out image flo

RUN tvl1flow $a $b $out
