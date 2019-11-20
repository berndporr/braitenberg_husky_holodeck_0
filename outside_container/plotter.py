import pylab as pl
import sys

def plot():
    visual_direction_Green = []
    visual_direction_Blue = []
    placefieldGreen = []
    placefieldBlue = []
    mPFC_Green = []
    DRN = []
    core_weight_lg2lg = []
    VTA = []
    CoreGreenOut = []

    f = open("plot_data.log", "r")
    lines = f.readlines()
    for line in lines:
        line.split(',')
        visual_direction_Green.append(line[0])
        visual_direction_Blue.append(line[1])
        placefieldGreen.append(line[2])
        placefieldBlue.append(line[3])
        mPFC_Green.append(line[4])
        DRN.append(line[5])
        core_weight_lg2lg.append(line[6])
        VTA.append(line[7])
        CoreGreenOut.append(line[8])

    pl.subplot(711)
    pl.plot(visual_direction_Green)
    pl.plot(placefieldGreen)
    pl.ylabel('vis1/green lm')
    pl.ylim([0,1.2])
    pl.yticks([0,0.5,1])
    #
    pl.subplot(712)
    pl.plot(visual_direction_Blue)
    pl.plot(placefieldBlue)
    pl.ylabel('vis2/blue r')
    pl.ylim([0,1.2])
    pl.yticks([0,0.5,1])
    #
    pl.subplot(713);
    pl.plot(mPFC_Green);
    pl.ylabel('mPFC: green lm');
    pl.ylim([0,2.5])
    pl.yticks([0,1,2])
    #
    pl.subplot(714);
    pl.plot(DRN);
    pl.ylabel('DRN');
    pl.ylim([0,2.5])
    pl.yticks([0,1,2])
    #
    pl.subplot(715);
    pl.plot(core_weight_lg2lg);
    pl.ylabel('core w green');
    pl.ylim([0,1.2])
    pl.yticks([0,0.5,1])
    #
    pl.subplot(716);
    pl.plot(VTA);
    pl.ylabel('VTA');
    pl.ylim([0,0.6])
    pl.yticks([0,0.25,0.5])
    #
    pl.subplot(717);
    pl.plot(CoreGreenOut);
    pl.ylabel('core out green');
    pl.ylim([0,3])
    pl.yticks([0,1,2])
    #
    pl.show();

if __name__== "__main__":
    plot()