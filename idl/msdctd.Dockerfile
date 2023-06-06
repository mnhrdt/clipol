NAME msdctd
TITLE Multi-Scale DCT Denoising
AUTHORS Nicola Pierazzo, Jean-Michel Morel, Gabriele Facciolo
SRC http://www.ipol.im/pub/art/2017/201/DCTdenoising-master.zip

# create an ad-hoc makefile
BUILD cat << 'EOF' > Makefile
BUILD CFLAGS=-march=native -O3 -Wno-format-truncation
BUILD CXXFLAGS=$(CFLAGS)
BUILD LDLIBS=-lfftw3f -lpng -ltiff -ljpeg
BUILD OBJ = iio.o main.o utils.o demoutils.o
BUILD BIN = DCTdenoising
BUILD $(BIN) : $(OBJ)
BUILD clean: ; $(RM) $(BIN) $(OBJ)
BUILD EOF

# fix warning in tiff reader
BUILD sed 's/uint16 /uint16_t /g' -i iio.c

# fix a bug so that the program works for images of arbitrary size
# (non necessarily multiple of 8)
BUILD sed '76i   if (col >= columns_) col = columns_ - 1;' -i Image.hpp
BUILD sed '76i   if (row >= rows_) row = rows_ - 1;'       -i Image.hpp

# compile, and copy the resulting binary
BUILD make
BUILD cp DCTdenoising $BIN/msdctd

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

RUN msdctd $sigma $in $out
