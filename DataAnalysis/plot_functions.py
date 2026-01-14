import pylab as py
import numpy as np

def plot_calibration_results(pixel,results,metadata,gain=False,offset=False,quad=False,column='date'):
    nrows,ncols=1,1
    py.figure(figsize=((6)*ncols,(4)*nrows))
    ax=py.subplot(nrows,ncols,1)
    runs = list(results[pixel].keys())
    for run in runs:
        x = metadata.loc[metadata['run_number']==run,column].iloc[0]
        if gain==True:
            ax.errorbar(x,results[pixel][run].params['m'].value,results[pixel][run].params['m'].stderr,fmt='o')
        if offset==True:
            ax.errorbar(x,results[pixel][run].params['b'].value,results[pixel][run].params['b'].stderr,fmt='o')
        if quad==True:
            ax.errorbar(x,results[pixel][run].params['q'].value,results[pixel][run].params['q'].stderr,fmt='o')
    ax.tick_params(axis='x', labelrotation=90)

def plot_goodness_of_fit(results,chi2=False,reduced_chi2=False,bottom_ylim=None,top_ylim=None):
    nrows,ncols=1,1
    py.figure(figsize=((6)*ncols,(4)*nrows))
    ax=py.subplot(nrows,ncols,1)
    pixels = list(results.keys())
    for pixel in pixels:
        runs = list(results[pixel].keys())
        for run in runs:
            x = int(pixel)
            if chi2==True:
                ax.scatter(x,results[pixel][run].chisqr)
            if reduced_chi2==True:
                ax.scatter(x,results[pixel][run].redchi)
    ax.set_xticks(range(int(pixels[0]),int(pixels[-1]),10))
    ax.set_ylim(bottom=bottom_ylim,top=top_ylim)

def plot_calibration_param_props(param_prop_df,yscale='linear'):
    nrows,ncols=1,1
    py.figure(figsize=((6)*ncols,(4)*nrows))
    ax=py.subplot(nrows,ncols,1)
    pixels = list(param_prop_df.keys())
    values = list(param_prop_df.values())
    ax.set_xticks(range(int(pixels[0]),int(pixels[-1]),10))
    ax.scatter(list(param_prop_df.keys()),values)
    mean = np.average(values)
    ax.axhline(mean,linestyle='dashed',label = 'Average: %.2e'%mean)
    ax.set_yscale(yscale)
    ax.legend()

def plot_peak_fit_params(parameters,peak='peak1',bottom_ylim=None,top_ylim=None):
    nrows,ncols=1,1
    py.figure(figsize=((6)*ncols,(4)*nrows))
    ax=py.subplot(nrows,ncols,1)
    pixels = list(parameters.keys())
    ax.set_xticks(range(int(pixels[0]),int(pixels[-1]),10))
    for pixel in pixels:
        runs = list(parameters[pixel].keys())
        for run in runs:
            try:
                error = parameters[pixel][run][peak]['error']
                value = parameters[pixel][run][peak]['value']
                ax.errorbar(pixel,value,yerr=error,fmt='o')
            except Exception as e:
                pass
    ax.set_ylim(bottom=bottom_ylim,top=top_ylim)