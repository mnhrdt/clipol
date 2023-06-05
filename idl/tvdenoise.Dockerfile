NAME tvdenoise
TITLE Rudin-Osher-Fatemi Total Variation Denoising using Split Bregman
AUTHORS Pascal Getreuer
SRC http://www.ipol.im/pub/art/2012/g-tvd/revisions/2012-05-19/tvdenoise_20120516.tar.gz

BUILD make -f makefile.gcc
BUILD cp tvdenoise $BIN/tvdenoise

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

RUN tvdenoise -n gaussian:$sigma $in $out
