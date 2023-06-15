NAME ffdnet
TITLE An Analysis and Implementation of the FFDNet Image Denoising Method
AUTHORS Matias Tassano, Julie Delon, Thomas Veit
SRC http://www.ipol.im/pub/art/2019/231/revisions/2019-07-23/ffdnet-pytorch.zip

# as per https://stackoverflow.com/questions/71182396/modulenotfounderror-no-module-named-skimage-measure-simple-metrics
BUILD sed 's/dynamic_range/data_range/' -i ffdnet-pytorch/utils.py
BUILD sed '/measure/c\from skimage.metrics import peak_signal_noise_ratio as compare_psnr' -i ffdnet-pytorch/utils.py
BUILD touch $BIN/dummy

INPUT in image
INPUT sigma number 10    # denoiser sigma
OUTPUT out image

RUN python $SRCDIR/ffdnet-pytorch/test_ffdnet_ipol.py --input $in --noise_sigma $sigma --no_gpu --add_noise False ; cp ffdnet.png $out
