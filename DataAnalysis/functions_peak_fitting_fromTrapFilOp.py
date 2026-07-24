import numpy as np
from lmfit import Minimizer, Parameters
import pylab as py
from scipy import special
from scipy.signal import find_peaks

def get_fit(model,residuals,params,xdat,ydat,alpha):
    mini = Minimizer(residuals, params, fcn_args=(xdat, ydat, alpha))
    result = mini.minimize()
    bestfit = model(result.params, xdat)
    return bestfit, result

def get_hist_data_uncert(data):
    alpha = np.sqrt(data)
    for k in range(len(alpha)):
        if alpha[k]<1:
            alpha[k]=1
    return alpha

def gauss(z,p1):
    return p1*np.exp(-0.5*(z)**2)

def background(x,p7,p8):
    return p7*x+p8

def lower_exp2(x,x0,beta,sig,amp):
    return (amp)*np.exp((sig**2/(2*beta**2))+((x-x0)/beta))*(1-special.erf((x-x0)/(np.sqrt(2)*sig) + sig/(np.sqrt(2)*beta)))

def step_function2(x,amp,x0,sig):
    return (amp)*(1-special.erf((x-x0)/(np.sqrt(2)*sig)))

def bi_model(params,x):

    num_peaks = params['num_peaks'].value
    intercept = params['intercept'].value
    slope = params['slope'].value
    beta = params['beta'].value
    
    peak_func = 0
    for i in range(int(num_peaks)):
        i+=1
        amp = params['amp%d'%i].value
        cen = params['cen%d'%i].value
        sig = params['sig%d'%i].value
        n= params['n%d'%i].value
        h = params['h%d'%i]

        z = (x-cen)/sig

        peak = gauss(z,amp*(1-n)) + lower_exp2(x,cen,beta,sig,amp*n) + step_function2(x,amp*h,cen,sig)
        peak_func += peak
    
    linear_background = background(x, slope, intercept)

    return peak_func + linear_background

def bi_residual(params, x, y, alpha):
    model = bi_model(params, x)
    return (model - y) / alpha

def add_bi_params(params,initial_peak_props,initial_parameter_values=None):

    if initial_parameter_values==None:
        params.add('slope',value=-1e-3) #original
        params.add('intercept',value=0)
        params.add('beta',value=10)
        for i in range(params['num_peaks'].value):
            i+=1
            params.add('amp%d'%i,value=initial_peak_props['amp%d'%i],min=0)
            params.add('cen%d'%i,value=initial_peak_props['cen%d'%i],min=0)
            params.add('sig%d'%i,value=initial_peak_props['sig%d'%i],min=0)
            params.add('n%d'%i,value=0.6,min=0,max=1)
            params.add('h%d'%i,0.1,min=0,max=1)

    else:
        params.add('slope',value=initial_parameter_values['slope']) #original
        params.add('intercept',value=initial_parameter_values['intercept'])
        for i in range(params['num_peaks'].value):
            i+=1
            params.add('amp%d'%i,value=initial_peak_props['amp%d'%i],min=0)
            params.add('cen%d'%i,value=initial_peak_props['cen%d'%i],min=0)
            params.add('sig%d'%i,value=initial_peak_props['sig%d'%i],min=0)
            params.add('beta%d'%i,value=initial_parameter_values['beta%d'%i],min=0)
            params.add('n%d'%i,value=initial_parameter_values['n%d'%i],min=0,max=1)
            params.add('h%d'%i,value=initial_parameter_values['h%d'%i],min=0,max=1)

def get_UDETinitial_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas):
    initial_peak_props = {}
    find_peaks.__defaults__ = peak_finder_props
    peaks, props = find_peaks(ydat)
    while len(peaks)>num_peaks:
        prop_list = list(peak_finder_props)
        prop_list[3] += 10

        peak_finder_props = tuple(prop_list)
        find_peaks.__defaults__ = peak_finder_props

        peaks, props = find_peaks(ydat)
    for i in range(num_peaks):
        i += 1
        if len(peaks)==num_peaks:
            initial_peak_props['amp%d'%i] = props['peak_heights'][i-1]
            initial_peak_props['cen%d'%i] = xdat[peaks[i-1]]
            initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
        
        # elif len(peaks)==num_peaks-1:
        #     if i!=num_peaks:
        #         initial_peak_props['amp%d'%i] = props['peak_heights'][i-1]
        #         initial_peak_props['cen%d'%i] = xdat[peaks[i-1]]
        #         initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
        #     else:
        #         initial_peak_props['amp%d'%i] = props['peak_heights'][-1]*0.5
        #         initial_peak_props['cen%d'%i] = xdat[peaks[-1]]+36
        #         initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
        # else:
        #     if num_peaks==2:
        #         if i<num_peaks:
        #             initial_peak_props['amp%d'%i] = max(ydat)
        #             initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0])
        #             initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
        #         else:
        #             initial_peak_props['amp%d'%i] = max(ydat)*0.5
        #             initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0])+36
        #             initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
        #     if num_peaks==3:
        #         if i==1:
        #             amp_scale = 1
        #             cen_shift = 0
        #         if i==2:
        #             amp_scale = 1/3
        #             cen_shift = 216
        #         if i==3:
        #             amp_scale = 1/6
        #             cen_shift = 252
        #         initial_peak_props['amp%d'%i] = max(ydat)*amp_scale
        #         initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0]) + cen_shift
        #         initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
    return initial_peak_props
    
def get_UDETbi_fit_long(run_number,data,bin_edges,pixel,low_region,up_region,num_peaks,peak_finder_props,initial_peak_sigmas,plot=False,initial_parameter_values=None):
    cnt = 0
    nrows,ncols=8,4
    fig = py.figure(figsize=(8*ncols,6*nrows))
    if not any(value==pixel for value in data.keys()):
        py.close(fig)
        print('pixel %s not found for run %d'%(pixel,run_number))
        return
    else:
        df = {}
        df['time'] = {}

        xdat = np.array(bin_edges[low_region:up_region])
        ydat = np.array(data[pixel][low_region:up_region])

        alpha = get_hist_data_uncert(ydat)

        try:
            initial_peak_props = get_UDETinitial_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas)
        except Exception as e:
            print('could not get initial peak props for run: %d, pixel: %s'%(run_number,pixel))
            return
        
        params = Parameters()
        params.add('num_peaks', value=num_peaks,vary=False)
        try:
            if initial_parameter_values==None:
                add_bi_params(params,initial_peak_props)
            else:
                add_bi_params(params,initial_peak_props,initial_parameter_values)
        except Exception as e:
            print('could not add params, run: %d, pixel: %s, low reg: %d'%(run_number,pixel,low_region),e)
            return
        
        model=bi_model
        residual_model = bi_residual

        try:
            bestfit, result = get_fit(model,residual_model, params, xdat, ydat,alpha)

            if result.errorbars:
                df['chi2'] = result.chisqr
                df['red chi2'] = result.redchi

                if plot:
                    cnt+=1
                    ax=py.subplot(nrows,ncols,cnt)
                    ax.step(xdat, ydat, alpha=0.5)
                    ax.plot(xdat, bestfit,label='Run %d, Pixel %s red chi: %.2f'%(run_number,pixel,result.redchi))
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
                print("no errors found for run: %d, pixel: %s, region "%(run_number,pixel))
                py.close(fig)
                return
        except Exception as e:
            
            print("failed Bi fit for run: %d, pixel: %s, region"%(run_number,pixel))
            py.close(fig)
            return
        return df