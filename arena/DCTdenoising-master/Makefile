CFLAGS=-march=native -O3 -Wno-format-truncation
CXXFLAGS=$(CFLAGS)
LDLIBS=-lfftw3f -lpng -ltiff -ljpeg
OBJ = iio.o main.o utils.o demoutils.o
BIN = DCTdenoising
$(BIN) : $(OBJ)
clean: ; $(RM) $(BIN) $(OBJ)
