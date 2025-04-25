NAME    gauss
TITLE   Computing an Exact Gaussian Scale-Space
AUTHOR  Ives Rey Otero, Mauricio Delbracio
SRC     https://www.ipol.im/pub/art/2016/117/gaussconv_20160131.zip

BUILD   make
BUILD   cp bin/gaussconv_dct $BIN
BUILD   cp bin/gaussconv_dft $BIN
BUILD   cp bin/gaussconv_lindeberg $BIN
BUILD   cp bin/gaussconv_sampled_kernel $BIN

INPUT   in image
INPUT   sigma number 3.0
INPUT   method string dft

OUTPUT  out image

RUN     gaussconv_$method $in $sigma $out
