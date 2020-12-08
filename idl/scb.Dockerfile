NAME scb
TITLE Simplest Color Balance
AUTHORS N.Limare, J.-L. Lisani, J.-M. Morel, A. Belén Petro, C. Sbert
SRC http://www.ipol.im/pub/art/2011/llmps-scb/simplest_color_balance.tar.gz

BUILD make
BUILD cp balance $BIN/scb

INPUT in image
INPUT Smin number 1      # percentage saturated to min
INPUT Smax number 1      # percentage saturated to max
INPUT mode string rgb    # rgb or irgb
OUTPUT out image

RUN scb $mode $Smin $Smax $in $out
