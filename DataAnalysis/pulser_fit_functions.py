import numpy as np
import pylab as py
from lmfit import Parameters
from DataAnalysis.basic_functions import gauss
from DataAnalysis.basic_functions import get_hist_data_uncert
from DataAnalysis.basic_functions import get_fit

def pulser_model(params,x):

    num_peaks = params['num_peaks'].value

    peak_func = 0
    for i in range(num_peaks):
        i+=1
        amp = params['amp%d'%i].value
        cen = params['cen%d'%i].value
        sig = params['sig%d'%i].value

        z = (x-cen)/sig

        peak = gauss(z,amp)
        peak_func += peak
    return peak_func

def pulser_residual(params, x, y, alpha):
    model = pulser_model(params, x)
    return (model - y) / alpha

def add_pulser_params(params,initial_peak_props):

    for i in range(params['num_peaks'].value):
        i+=1
        params.add('amp%d'%i,value=initial_peak_props['amp%d'%i],min=0)
        params.add('cen%d'%i,value=initial_peak_props['cen%d'%i])
        params.add('sig%d'%i,value=initial_peak_props['sig%d'%i],min=0)

def get_initial_peak_props_pulser(xdat,ydat,num_peaks,initial_peak_sigmas):
    initial_peak_props = {}
    initial_peak_props['amp%d'%num_peaks] = max(ydat)
    initial_peak_props['cen%d'%num_peaks] = xdat[np.argmax(ydat)]
    initial_peak_props['sig%d'%num_peaks] = initial_peak_sigmas['sig%d'%num_peaks]

    return initial_peak_props

def get_pulser_fit(run_number,data,bin_edges,pixel,low_region,up_region,num_peaks,initial_peak_sigmas,plot=False):
    cnt = 0
    nrows,ncols=8,4
    fig = py.figure(figsize=(8*ncols,6*nrows))
    if not any(value==pixel for value in data.keys()):
        py.close(fig)
        return
    else:
        df = {}
        df['time'] = {}

        xdat = np.array(bin_edges[low_region:up_region])
        ydat = np.array(data[pixel][low_region:up_region])
        alpha = get_hist_data_uncert(ydat)
        initial_peak_props = get_initial_peak_props_pulser(xdat,ydat,num_peaks,initial_peak_sigmas)
        params = Parameters()
        params.add('num_peaks', value=num_peaks,vary=False)
        add_pulser_params(params,initial_peak_props)
        model=pulser_model
        residual_model = pulser_residual
        try:
            bestfit, result = get_fit(model,residual_model, params, xdat, ydat,alpha)
            if result.errorbars:
                df['chi2'] = result.chisqr
                df['red chi2'] = result.redchi
                if plot:
                    cnt+=1
                    ax=py.subplot(nrows,ncols,cnt)
                    ax.step(xdat, ydat, alpha=0.5)
                    ax.plot(xdat, bestfit,label='red chi: %.2f'%result.redchi)
                    ax.set_ylabel('Counts')
                    ax.set_xlabel('Energy (ADC)')
                    ax.legend()
                    py.show()
                else:
                    py.close(fig)
                for key in result.params.keys():
                    df['%s'%key] = {}
                    df['%s'%key] = {}
                    df['%s'%key]['value'] = result.params['%s'%key].value
                    df['%s'%key]['error'] = result.params['%s'%key].stderr
            else:
                print("no errors found for run: %d, pixel: %s"%(run_number,pixel))
                py.close(fig)
                return {}
        except Exception as e:
            print("failed pulser fit for run: %d, pixel: %s"%(run_number,pixel))
            py.close(fig)
            return {}

    return df

def get_pulser_results(energy, bin_edges, pixel, run_numbers,low=0,high=9999,plot=True,detector_type = None):
    if detector_type=='LDET':
        sigs0_df = {'sig1':5}
    else:
        sigs0_df = {'sig1':5}
    results = {}
    for i in run_numbers:
        r = get_pulser_fit(i, energy[i], bin_edges, pixel,low,high,1,sigs0_df,plot=plot)
        if r==None:
            pass
        else:
            results[i] = {}
            results[i][0] = r
    return results