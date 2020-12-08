NAME tvl1
TITLE TVL1 Optical Flow
SRC http://www.ipol.im/pub/art/2013/26/tvl1flow_3.tar.gz


BUILD make
BUILD cp tvl1flow $BIN

BUILD:OpenBSD make CC="cc -std=c99" OMPFLAGS="-DDISABLE_OMP"
BUILD:OpenBSD cp tvl1flow $BIN


INPUT image a
INPUT image b
OUTPUT image out

RUN tvl1flow $a $b $out
