import numpy as np
import matplotlib.pyplot as plt

def HepHist(data,nbins=20,xlims=[0,0],xtrim=False,xLog=False,yLog=False,color='C0',label='',norm=False,fill=True,alpha=0.1):
    if xlims[0] == 0 and xlims[1] == 0: xlims = [min(data),max(data)]
    ls = '-'
    lw = 2
    plt.rcParams['hatch.color'] = color
    if xLog:
        if xlims[0]==0 or xlims[1]==0: raise Exception("xlims must be >0!")
        hist, bin_edges = np.histogram(data,bins=np.logspace(np.log10(xlims[0]),np.log10(xlims[1]),nbins))
    else: hist, bin_edges = np.histogram(data,bins=nbins,range=xlims)
    bin_center = [(bin_edges[i] + bin_edges[i+1])/2. for i in range(len(bin_edges)-1)]
    xerr = (bin_center[1]-bin_center[0])/2.
    yerr = np.sqrt(hist)
    if norm:
        normFactor = float(np.sum(hist))
        hist = hist/normFactor
        yerr = yerr/normFactor
    plt.step(bin_edges[:-1],hist,where='post',color=color,linestyle=ls,lw=lw,label=label)
    plt.errorbar(bin_center,hist,xerr=xerr,fmt='.',color=color,lw=lw)
    plt.errorbar(bin_center,hist,yerr=yerr,fmt='.',color=color,lw=lw,capsize=3,elinewidth=1)
    if fill:      
        xfill = []
        yfill = []
        for x in bin_edges:
            xfill.append(x)
            xfill.append(x)
        for y in hist:
            yfill.append(y)
            yfill.append(y)    
        xfill = xfill[1:-1]
        plt.fill_between(xfill,0,yfill,facecolor=color,alpha=alpha,lw=0)
    plt.plot([bin_edges[0],bin_edges[0]],[0,hist[0]],color=color,ls=ls,lw=lw)
    plt.plot([bin_edges[-1],bin_edges[-1]],[0,hist[-1]],color=color,ls=ls,lw=lw)
    plt.gca().set_ylim(bottom=0)
    if xtrim: plt.xlim(xlims)
    if hist.max() > plt.gca().get_ylim()[1]*0.9: plt.gca().set_ylim(top=hist.max()*1.1)
    if xLog: plt.xscale('log')
    if yLog: plt.yscale('log'); plt.gca().set_ylim(bottom=0.1)
    plt.grid(ls='--')

def HepPlot(bin_lowEdge,yval,yerr=[0],color='C0',label='',fill=True,alpha=0.1):
    ls = '-'
    lw = 2
    yval = np.array(yval)
    if len(yerr) == 1: yerr = [0 for i in range(len(yval))]
    plt.rcParams['hatch.color'] = color
    halfStep = (bin_lowEdge[1] - bin_lowEdge[0])/2.
    bin_center = [x+halfStep for x in bin_lowEdge]
    bin_edges = [x for x in bin_lowEdge]
    bin_edges.append(bin_lowEdge[-1]+2*halfStep)
    plt.step(bin_lowEdge,yval,where='post',color=color,linestyle=ls,lw=lw,label=label)
    plt.errorbar(bin_center,yval,xerr=halfStep,fmt='.',color=color,lw=lw)
    plt.errorbar(bin_center,yval,yerr=yerr,fmt='.',color=color,lw=lw,capsize=3,elinewidth=1)
    if fill:      
        xfill = []
        yfill = []
        for x in bin_edges:
            xfill.append(x)
            xfill.append(x)
        for y in yval:
            yfill.append(y)
            yfill.append(y)    
        xfill = xfill[1:-1]
        plt.fill_between(xfill,0,yfill,facecolor=color,alpha=alpha,lw=0)
    plt.plot([bin_edges[0],bin_edges[0]],[0,yval[0]],color=color,ls=ls,lw=lw)
    plt.plot([bin_edges[-1],bin_edges[-1]],[0,yval[-1]],color=color,ls=ls,lw=lw)
    if yval.max() > plt.gca().get_ylim()[1]*0.9: plt.gca().set_ylim(top=yval.max()*1.1)
    plt.gca().set_ylim(bottom=0)
    plt.grid(ls='--')
