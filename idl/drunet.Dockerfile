NAME drunet
TITLE Valery's interface to drunet
SRC https://github.com/mnhrdt/drunet-ipolized/archive/refs/heads/master.zip

BUILD wget -P model_zoo https://huggingface.co/deepinv/drunet/resolve/main/drunet_gray.pth
BUILD wget -P model_zoo https://huggingface.co/deepinv/drunet/resolve/main/drunet_color.pth
BUILD touch $BIN/dummy

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

RUN python $SRCDIR/drunet.py -s $sigma -i $in -o $out
