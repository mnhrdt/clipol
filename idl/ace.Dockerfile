NAME    ace
TITLE   Automatic Color Enhancement
AUTHOR  Pascal Getreuer
SRC     http://www.ipol.im/pub/art/2012/g-ace/ace_20121029.tar.gz

BUILD   make -f makefile.gcc
BUILD   cp ace $BIN

INPUT   image in
INPUT   number alpha 5
INPUT   string omega 1/r
INPUT   string method interp:5

OUTPUT  image

RUN     ace -a $alpha -w $omega -m $method $in $out
