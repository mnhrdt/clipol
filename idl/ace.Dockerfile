NAME    ace
TITLE   Automatic Color Enhancement
AUTHOR  Pascal Getreuer
SRC     http://www.ipol.im/pub/art/2012/g-ace/ace_20121029.tar.gz

BUILD   sed 's/uint32 /uint32_t /g' -i imageio.c  # fix warning in tiff reader
BUILD   sed 's/uint16 /uint16_t /g' -i imageio.c  # fix warning in tiff reader
BUILD   make -f makefile.gcc CFLAGS='-O3 -march=native'
BUILD   cp ace $BIN

INPUT   in image 
INPUT   alpha number 5
INPUT   omega string 1/r
INPUT   method string interp:5

OUTPUT  out image

RUN     ace -a $alpha -w $omega -m $method $in $out
