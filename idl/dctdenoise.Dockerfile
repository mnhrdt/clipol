NAME dctdenoise
TITLE DCT Image Denoising: a Simple and Effective Image Denoising Algorithm
AUTHORS Guoshen Yu, Guillermo Sapiro
SRC http://www.ipol.im/pub/art/2011/ys-dct/revisions/2021-02-20/src_demoDCTdenoising.tar.gz

BUILD make
BUILD cp demo_DCTdenoising $BIN/dctdenoise

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

# note: in the documentation of the revised DCT denoising article the order of
# the arguments is wrong (options "add-noise" and "sigma" are swapped)
RUN dctdenoise $in $sigma 0 /dev/null $out
