import pylab as pl
import sys

def plot():
    f = open("plot_data.log", "r")
    # create a list of the different data headings
    plot_headings = f.readline().split(',')
    # create dictionary of empty lists for each item
    plot_dict = {item:[] for item in plot_headings}
    lines = f.readlines()

    for line in lines:
        line = line.split(',')
        for i, data in enumerate(line):
            plot_dict[plot_headings[i]].append(float(line[i]))
            
    for i, heading in enumerate(plot_headings):
        pl.subplot(711 + i)
        pl.plot(plot_dict[heading])
        pl.ylabel(heading)
        pl.ylim( [ min(plot_dict[heading]) , max(plot_dict[heading]) ])
    pl.show()

if __name__== "__main__":
    plot()
