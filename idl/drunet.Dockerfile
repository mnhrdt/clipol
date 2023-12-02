NAME drunet
TITLE Valery's interface to drunet
SRC https://github.com/mnhrdt/drunet-ipolized/archive/refs/heads/master.zip

BUILD echo building drunet
BUILD (pwd ; cd model_zoo ; pwd ; ls ; sh download.sh)
BUILD touch $BIN/dummy

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

RUN python $SRCDIR/ffdnet-pytorch/test_ffdnet_ipol.py --input $in --noise_sigma $sigma --no_gpu --add_noise False ; cp ffdnet.png $out
