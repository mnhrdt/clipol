NAME scb
TITLE Simplest Color Balance
SRC http://www.ipol.im/pub/art/2011/llmps-scb/simplest_color_balance.tar.gz

BUILD make
BUILD cp balance $BIN/scb

INPUT in image
INPUT Smin number 1      # percentage saturated to min
INPUT Smax number 1      # percentage saturated to max
INPUT mode string irgb   # rgb or irgb
OUTPUT out image

RUN scb $mode $Smin $Smax $in $out
