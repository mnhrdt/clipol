NAME bm3d
TITLE An Analysis and Implementation of the BM3D Image Denoising Method
AUTHORS Marc Lebrun
SRC http://www.ipol.im/pub/art/2012/l-bm3d/revisions/2021-02-20/bm3d_src.tar.gz

BUILD sed '/stdio/a#include <string.h>' -i io_png.c  # add missing header
BUILD make CXXFLAGS='-O3 -march=native -Wno-narrowing -Wno-misleading-indentation'
BUILD cp BM3Ddenoising $BIN/bm3d

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

# note: we call bm3d with default arguments and without any diagnostic output
# note2: the documentation line of the revised BM3Ddenoising executable is
# wrong (the add-noise selector and the value of sigma being reversed)
RUN bm3d $in $sigma 0 /dev/null /dev/null $out /dev/null /dev/null /dev/null 1 bior 0 dct 1 opp
