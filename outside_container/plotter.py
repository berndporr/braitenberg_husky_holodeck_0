""" 
Reads in file named plot_data.log. The first line of which contains comma separated headings.
The following lines contain comma separated data corresponding to the heading.
Any heading containing a '/' will have its data plotted with the next set of data on the same graph.
"""
import pylab as pl
import numpy as np

def create_plot(data1, heading1, plot_no, data2=[], heading2='', last=False):
    pl.subplot(911 + plot_no)

    pl.plot(data1, 'k')
    pl.plot(data2, 'k',linestyle='--')



    label_string = '\n\n\n' + heading1 +'\n' +  heading2
    label_string = label_string.replace('/','')
    pl.ylabel(label_string, labelpad=40, rotation=0).set_position((1.0, -0.3))
    min_lim = min(data1 + data2) - max(data1 + data2) * 0.1
    max_lim = max(data1 + data2) + max(data1 + data2) * 0.1
    max_mark = np.ceil(  max(data1 + data2))
    pl.ylim([min_lim, max_lim])         
    pl.yticks( [0, max_mark/2, max_mark] )
    if last: 
        pl.xlabel("Time Steps", labelpad=10)
    if not last:
        pl.ylabel(label_string, labelpad=50, rotation=0).set_position((1.0, 0))
        pl.xticks([])

def plot():
    f = open("plot_data.log", "r")
    plot_headings = f.readline().split(',')
    plot_dict = {item:[] for item in plot_headings}
    lines = f.readlines()
    skip_next = False
    plot_no = 0
    last = False
    for line in lines:
        line = line.split(',')
        for i, data in enumerate(line):
            plot_dict[plot_headings[i]].append(float(data))
            
    for i, heading in enumerate(plot_headings):
        if ((i >= len(plot_headings)-1)  or ( ('/' in heading) and (i >= len(plot_headings)-2)) ) :
            last = True
        if skip_next:
            skip_next = False
            continue
        # multiple data on one plot
        if ('/' in heading):
            skip_next = True
            next_heading = plot_headings[i+1]
            create_plot(plot_dict[heading], heading, plot_no, plot_dict[next_heading], next_heading, last)
        else:
            create_plot(plot_dict[heading], heading, plot_no, last=last)
        plot_no += 1

    pl.show()

if __name__== "__main__":
    plot()