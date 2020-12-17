import os
import pandas as pd
import pingouin as pg
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rcParams
from matplotlib.patches import Patch
from scipy.stats import iqr

'''settings'''
sns.set_context('notebook',font_scale=1.4)
sns.set_style('ticks', {'axes.spines.right':False, 'axes.spines.top':False})
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['savefig.dpi'] = 300
cpal = ['darkorange','grey']
legend_elements = [Patch(facecolor=cpal[0],edgecolor=None,label='CS+'),
                   Patch(facecolor=cpal[1],edgecolor=None,label='CS-')]

def p_convert(pval):  #converts pval to asterisks
    if pval < .05:
        return "*" * sum([ pval < cutoff for cutoff in [.05,.01,.001] ])
    elif pval < .1:
        return '~'
    else:
        return ''

def paired_barplot_annotate_brackets(txt, x_tick, height, y_lim, dh=.05, barh=.05, fs=10, maxasterix=None, ax=None):
    """ 
    Annotate barplot with p-values.

    :param txt: string to write or number for generating asterixes
    :param x_tick: center of pair of bars
    :param height: heights of the errors in question
    :param yerr: yerrs of all bars (like plt.bar() input)
    :param dh: height offset over bar / bar + yerr in axes coordinates (0 to 1)
    :param barh: bar height in axes coordinates (0 to 1)
    :param fs: font size
    :param maxasterix: maximum number of asterixes to write (for very small p-values)
    """

    if type(txt) is str:
        text = txt
    else:
        # * is p < 0.05
        # ** is p < 0.005
        # *** is p < 0.0005
        # etc.
        text = ''
        p = .05

        while txt < p:
            text += '*'
            p /= 10.

            if maxasterix and len(text) == maxasterix:
                break

        if len(text) == 0:
            text = 'n. s.'

    lx, ly = x_tick-.2, height[0]
    rx, ry = x_tick+.2, height[1]

    ax_y0, ax_y1 = y_lim
    dh *= (ax_y1 - ax_y0)
    barh *= (ax_y1 - ax_y0)

    y = max(ly, ry) + dh

    barx = [lx, lx, rx, rx]
    bary = [y, y+barh, y+barh, y]
    mid = ((lx+rx)/2, y+barh)

    ax.plot(barx, bary, c='black')

    kwargs = dict(ha='center', va='bottom')
    if fs is not None:
        kwargs['fontsize'] = fs

    ax.text(*mid, text, **kwargs)

def identify_outliers(x):
    """Takes in array x, and identifies outliers.
    Assumes that the index is the subject number.
    Outliers are defined by data that are beyond
    1.5*Inter Quartile Range in either direction. 
    """
    outliers = np.array([])

    IQR = iqr(x)
    low_cut = np.percentile(x,25) - 1.5*IQR
    high_cut = np.percentile(x,75) + 1.5*IQR

    for sub in x.index:
        if x.loc[sub] < low_cut or x.loc[sub] > high_cut:
            # outliers = np.append(outliers,np.asarray(x == i).nonzero()[0])
            outliers = np.append(outliers,sub)

    return outliers