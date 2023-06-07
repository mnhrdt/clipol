NAME nlbayes
TITLE Implementation of the "Non-Local Bayes" (NL-Bayes) Image Denoising Algorithm
AUTHORS Marc Lebrun, Antoni Buades, Jean-Michel Morel
SRC http://www.ipol.im/pub/art/2013/16/./revisions/2021-02-20/nl-bayes_20130617.tar.gz

BUILD sed '/stdio/a#include <string.h>' -i Utilities/io_png.c  # missing header
BUILD make
BUILD cp NL_Bayes $BIN/nlbayes

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

# note: the documentation line of the revised source code executable is
# wrong (the add-noise selector and the value of sigma being reversed)
RUN nlbayes $in $sigma 0 /dev/null $out /dev/null /dev/null /dev/null ImBiasBasic /dev/null 1 0 1
