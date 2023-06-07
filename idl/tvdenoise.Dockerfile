NAME tvdenoise
TITLE Rudin-Osher-Fatemi Total Variation Denoising using Split Bregman
AUTHORS Pascal Getreuer
SRC http://www.ipol.im/pub/art/2012/g-tvd/revisions/2012-05-19/tvdenoise_20120516.tar.gz

BUILD   sed 's/uint32 /uint32_t /g' -i imageio.c  # fix warning in tiff reader
BUILD   sed 's/uint16 /uint16_t /g' -i imageio.c  # fix warning in tiff reader
BUILD make -f makefile.gcc
BUILD cp tvdenoise $BIN/tvdenoise

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

RUN tvdenoise -n gaussian:$sigma $in $out
