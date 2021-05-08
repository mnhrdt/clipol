NAME lsd
TITLE Line Segment Detector
SRC http://www.ipol.im/pub/art/2012/gjmr-lsd/lsd_1.6.zip

INPUT in image png
OUTPUT out image asc

BUILD make
BUILD cp lsd $BIN

RUN convert $in x.pgm
RUN lsd x.pgm segments.txt
RUN (echo 7 `wc -l <segments.txt` 1 1 ; cat segments.txt) > $out
