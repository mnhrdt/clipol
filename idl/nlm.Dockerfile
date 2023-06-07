NAME nlm
TITLE Non-Local Means Denoising
AUTHORS Antoni Buades, Bartomeu Coll, Jean-Michel Morel
SRC http://www.ipol.im/pub/art/2011/bcm_nlm/revisions/2021-08-22/nlmeansC.tar.gz

BUILD sed '/stdio/a#include <string.h>' -i io_png.c  # add missing header
BUILD make clean                                     # del binaries in the zip
BUILD make
BUILD cp nlmeans_ipol $BIN/nlm

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

RUN nlm $in $sigma 0 $out dummy
