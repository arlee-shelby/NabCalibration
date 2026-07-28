import pylab as py
import numpy as np

def plot_calibration_results(pixel,results,metadata,gain=False,offset=False,quad=False,column='date',title=None,ylabel=None,bottom_ylim=None,top_ylim=None):
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
    ax.set_ylim(bottom=bottom_ylim,top=top_ylim)
    ax.set_xlabel(column)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

def plot_goodness_of_fit(results,chi2=False,reduced_chi2=False,bottom_ylim=None,top_ylim=None,title=None,ylabel=None):
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
    ax.set_xlabel('Pixel')
    ax.set_ylabel(ylabel)
    ax.set_title(title)

def plot_calibration_param_props(param_prop_df,yscale='linear',LDETparam_prop_df=None,title=None,ylabel=None,bottom_ylim=None,top_ylim=None):
    nrows,ncols=1,1
    py.figure(figsize=((6)*ncols,(4)*nrows))
    ax=py.subplot(nrows,ncols,1)

    pixels = list(param_prop_df.keys())
    int_pixels = list(map(int, pixels))
    values = list(param_prop_df.values())
    ax.scatter(int_pixels,values,color='C0')
    mean = np.average(values)
    ax.axhline(mean,linestyle='dashed',label = 'UDET average: %.2e'%mean,color='C0')
    if LDETparam_prop_df!=None:
        LDETpixels = list(LDETparam_prop_df.keys())
        LDETvalues = list(LDETparam_prop_df.values())
        LDETint_pixels = list(map(int, LDETpixels))
        ax.scatter(np.array(LDETint_pixels)-1000,LDETvalues,color='C1')
        mean = np.average(LDETvalues)
        ax.axhline(mean,linestyle='dashed',label = 'LDET average: %.2e'%mean,color='C1')
    ax.set_xticks(range(min(int_pixels),max(int_pixels),10))
    ax.set_yscale(yscale)
    ax.set_ylim(bottom=bottom_ylim,top=top_ylim)
    ax.set_xlabel('Pixel')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()

def plot_peak_fit_params(parameters,parameters2=None,peak='peak1',bottom_ylim=None,top_ylim=None,title=None,ylabel=None,detector_type='UDET'):
    nrows,ncols=1,1
    py.figure(figsize=((10)*ncols,(8)*nrows))
    ax=py.subplot(nrows,ncols,1)
    pixels = list(parameters.keys())
    int_pixels = list(map(int, pixels))
    for pixel in pixels:
        runs = list(parameters[pixel].keys())
        for run in runs:
            try:
                error = parameters[pixel][run][peak]['error']
                value = parameters[pixel][run][peak]['value']
                if detector_type=='UDET':
                    pixel_value = int(pixel)
                    c = 'C0'
                if detector_type=='LDET':
                    pixel_value = int(pixel)-1000
                    c = 'C0'
                if pixel=='11' and run==8655:
                    ax.errorbar(pixel_value,value,yerr=error,fmt='o',color=c,label = 'UDET 2025')
                else:
                    ax.errorbar(pixel_value,value,yerr=error,fmt='o',color=c)
            except Exception as e:
                pass
    if detector_type=='UDET':
        ax.set_xticks(range(min(int_pixels),max(int_pixels),12))
    if detector_type=='LDET':
        ax.set_xticks(range(min(int_pixels)-1000,max(int_pixels)-1000,12))
    if parameters2!=None:
        pixels2 = list(parameters2.keys())
        for pixel in pixels2:
            runs = list(parameters2[pixel].keys())
            for run in runs:
                try:
                    error = parameters2[pixel][run][peak]['error']
                    value = parameters2[pixel][run][peak]['value']
                    if detector_type=='UDET':
                        pixel_value = int(pixel)-1000
                        c = 'C1'
                    if detector_type=='LDET':
                        pixel_value = int(pixel)-1000
                        c = 'C1'
                    if pixel=='1012' and run==8644:
                        ax.errorbar(pixel_value,value,yerr=error,fmt='o',color=c,label = 'LDET 2025')
                    else:
                        ax.errorbar(pixel_value,value,yerr=error,fmt='o',color=c)
                except Exception as e:
                    pass
    # if detector_type=='UDET':
    #     ax.set_xticks(range(min(int_pixels),max(int_pixels),12))
    # if detector_type=='LDET':
    #     ax.set_xticks(range(min(int_pixels)-1000,max(int_pixels)-1000,12))

    ax.legend(fontsize=25)
    ax.set_ylim(bottom=bottom_ylim,top=top_ylim)
    ax.set_xlabel('Pixel',fontsize=30)
    ax.set_ylabel(ylabel,fontsize=30)
    ax.set_title(title,fontsize=30)
    ax.tick_params(axis='both', which='major', labelsize=30)