TITLE Pyramidal Horn Schunck
SRC http://www.ipol.im/pub/art/2013/20/phs_3.tar.gz

BUILD make
BUILD cp horn_schunck_pyramidal $BIN/phs

INPUT image a
INPUT image b
OUTPUT image out

RUN phs $a $b $out
