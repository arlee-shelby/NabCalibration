import numpy as np
from scipy.signal import find_peaks
from lmfit import Parameters
import pylab as py
from DataAnalysis.basic_functions import D1
from DataAnalysis.basic_functions import get_hist_data_uncert
from DataAnalysis.basic_functions import get_fit
from DataAnalysis.bi_fit_functions import get_UDETinitial_peak_props

def modified_expo_model(params, x):
    num_peaks = params['num_peaks'].value
    num_mods = params['num_mods'].value
    source = params['source'].value
    func = 0
    for i in range(num_peaks):
        i+=1
        cen = params['cen%d'%i].value
        sig = params['sig%d'%i].value
        area = params['area%d'%i].value
        
        peak_func = 0
        for j in range(num_mods):
            j+=1
            t = params['t%d'%j].value
            if i==1:
                n = params['n%d'%(i+j-1)].value
                mod = D1(x,n,cen,t,sig)
                peak_func+=area*mod
            if i>1:
                if j==1:
                    n = params['n%d'%1].value
                else:
                    n = params['n%d'%(i+j-1)].value
                mod = D1(x,n,cen,t,sig)
                peak_func+=area*mod
        
        if source==1 or source==2:
            if i==num_peaks:
                cen_ratio = params['cen_ratio'].value
                amp_ratio = params['amp_ratio'].value
                peak_func+=area*D1(x,amp_ratio*params['n1'],cen*cen_ratio,params['t%d'%1].value,sig)

        func+=peak_func
    return func

# def modified_expo_model2(params,x):
#     num_peaks = params['num_peaks'].value
#     source = params['source'].value
#     func = 0
#     for i in range(num_peaks):
#         i+=1
#         cen = params['cen%d'%i].value
#         sig = params['sig%d'%i].value
#         area = params['area%d'%i].value


def modified_expo_residual(params, x, y, alpha):
    model = modified_expo_model(params, x)
    return (model - y) / alpha

def add_modified_expo_params(params,initial_peak_props):
    if params['source'].value==1 or params['source'].value==2:
        params.add('cen_ratio',value=initial_peak_props['cen_ratio'],min=1,max=1.3)
        params.add('amp_ratio',value=initial_peak_props['amp_ratio'],min=0.1,max=0.5)
    if params['source'].value==3:
        params.add('cen_ratio',value=initial_peak_props['cen_ratio'],vary=False)
        params.add('amp_ratio',value=initial_peak_props['amp_ratio'],vary=False)
    for j in range(params['num_mods'].value):
        j+=1
        if j==1:
            params.add('t%d'%j,value = initial_peak_props['t%d'%j],min=0)
        else:
            params.add('delta%d'%(j-1),value = initial_peak_props['delta%d'%(j-1)],min=0)
            params.add('t%d'%j,expr='t%d + delta%d'%(j-1,j-1),min=0)

    for i in range(params['num_peaks'].value):
        i+=1
        params.add('cen%d'%i,value = initial_peak_props['cen%d'%i],min=0)
        # params.add('sig%d'%i,value = initial_peak_props['sig%d'%i],min=0,max=10)
        params.add('sig%d'%i,value = initial_peak_props['sig%d'%i],min=0)
        if params['source'].value==3:
            params.add('area%d'%i,value = initial_peak_props['area%d'%i],min=0)
        else:
            params.add('area%d'%i,value = initial_peak_props['area%d'%i],min=0)

    n_indx = np.arange((params['num_peaks'].value*params['num_mods'].value)-(params['num_peaks'].value-1))+1
    n_expr = '1-n1'
    for i in n_indx:
        if i==1:
            params.add('n%d'%i,value = initial_peak_props['n%d'%i],min=0,max=1)
        elif i==n_indx[-1]:
            if i==params['num_mods'].value+1:
                n_expr = '1-n1'
            n_expr+='-n1*amp_ratio'
            params.add('n%d'%i,expr=n_expr,min=0,max=1) 
        elif i==params['num_mods'].value+1:
            n_expr = '1-n1'
            params.add('n%d'%i,value=0.1,min=0,max=1)
            n_expr+='-n%d'%(i)
        elif i%params['num_mods'].value==0:
            params.add('n%d'%i,expr=n_expr,min=0,max=1) 
            n_expr+='-n%d'%(i)
        else:
            params.add('n%d'%i,value=0.1,min=0,max=1)
            n_expr+='-n%d'%(i)

def get_initial_mod_expo_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas,num_mods,source):
    initial_peak_props = {}
    
    if source=='bi':
        initial_peak_props = get_UDETinitial_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas)
        initial_peak_props['n1'] = 0.7
        initial_peak_props['cen_ratio'] = 0
        initial_peak_props['amp_ratio'] = 0
    
    if source=='cd' or source=='sn':
        initial_peak_props = {}
    
    for j in range(num_mods):
        j+=1
        if j==1:
            initial_peak_props['t%d'%j]=10.2
        else:
            initial_peak_props['delta%d'%(j-1)] = 100*(j-1)
#     else:
    find_peaks.__defaults__ = peak_finder_props
    peaks, props = find_peaks(ydat)
    while len(peaks)>num_peaks:
        prop_list = list(peak_finder_props)
        prop_list[3] += 10
        peak_finder_props = tuple(prop_list)
        find_peaks.__defaults__ = peak_finder_props
        peaks, props = find_peaks(ydat)
    if source=='cd':
        initial_peak_props['cen_ratio'] = 1.05
        initial_peak_props['amp_ratio'] = 0.25
        initial_peak_props['n1'] = 0.7
    if source=='sn':
        initial_peak_props['cen_ratio'] = 1.03
        initial_peak_props['amp_ratio'] = 0.25
        initial_peak_props['n1'] = 0.9
        
    for i in range(num_peaks):
        i+=1
        # initial_peak_props['area%d'%i] = props['peak_heights'][i-1]
        # initial_peak_props['cen%d'%i] = xdat[peaks[i]]
        # initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
        # if len(peaks)==num_peaks:
#         print(props['peak_heights'][i-1]*3)
        initial_peak_props['area%d'%i] = props['peak_heights'][i-1]*3
        initial_peak_props['cen%d'%i] = xdat[peaks[i-1]]
        initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]

    return initial_peak_props

def get_mod_expo_fit_short(data,time_data,num_groups,pixel,low_region,up_region,num_peaks,peak_finder_props,initial_peak_sigmas,num_mods,source,plot=False):
    cnt = 0
    nrows,ncols=8,4
    py.figure(figsize=(8*ncols,6*nrows))

    df = {}
    df['time'] = {}
    for i in range(num_groups):
        xdat = np.array(data['bin_edges']['%d'%i][pixel][low_region:up_region])
        ydat = np.array(data['hist']['%d'%i][pixel][low_region:up_region])

        alpha = get_hist_data_uncert(ydat)

        initial_peak_props = get_initial_mod_expo_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas,num_mods,source)

        params = Parameters()
        params.add('num_peaks', value=num_peaks,vary=False)
        params.add('num_mods', value=num_mods,vary=False)

        if source=='cd':
            params.add('source',value=1,vary=False)
        if source=='sn':
            params.add('source',value=2,vary=False)
        if source=='bi':
            params.add('source',value=3,vary=False)
        
        add_modified_expo_params(params,initial_peak_props)

        model=modified_expo_model
        residual_model = modified_expo_residual

        bestfit, result = get_fit(model,residual_model, params, xdat, ydat,alpha)

        if result.errorbars:
            df[i] = {}
            if plot:
                cnt+=1
                ax=py.subplot(nrows,ncols,cnt)
                ax.step(data['bin_edges']['%d'%i][pixel][low_region:up_region], data['hist']['%d'%i][pixel][low_region:up_region],alpha=0.5)
                ax.plot(xdat, bestfit, label='%.2f'%result.redchi)

            for key in result.params.keys():
                df[i]['%s'%key] = {}
                df[i]['%s'%key] = {}
                df[i]['%s'%key]['value'] = result.params['%s'%key].value
                df[i]['%s'%key]['error'] = result.params['%s'%key].stderr

        else:
            print('errors were not calculated for subgroup:%d'%i)

        df['time'][i] = time_data['%d'%i]['subgroup_start'][-8:]
    return df

def get_mod_expo_fit_long(run_number,data,bin_edges,pixel,low_region,up_region,num_peaks,peak_finder_props,initial_peak_sigmas,num_mods,source,plot=False):
    cnt = 0
    nrows,ncols=8,4
    fig = py.figure(figsize=(8*ncols,6*nrows))
    if not any(value==pixel for value in data.keys()):
        py.close(fig)
        print('pixel %s not found for run %d'%(pixel,run_number))
        return {}
    else:
        df = {}
        df['time'] = {}
        xdat = np.array(bin_edges[low_region:up_region])
        ydat = np.array(data[pixel][low_region:up_region])

        alpha = get_hist_data_uncert(ydat)

        try:
            initial_peak_props = get_initial_mod_expo_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas,num_mods,source)
        except Exception as e:
            print("could not get initial fit params for run: %d, pixel: %s"%(run_number,pixel))
            py.close(fig)
            return {}
        
        params = Parameters()
        params.add('num_peaks', value=num_peaks,vary=False)
        params.add('num_mods', value=num_mods,vary=False)

        if source=='cd':
            params.add('source',value=1,vary=False)
        if source=='sn':
            params.add('source',value=2,vary=False)
        if source=='bi':
            params.add('source',value=3,vary=False)
        
        add_modified_expo_params(params,initial_peak_props)

        model=modified_expo_model
        residual_model = modified_expo_residual

        try:
            print(params)
            bestfit, result = get_fit(model,residual_model, params, xdat, ydat,alpha)

            if result.errorbars:
                df['chi2'] = result.chisqr
                df['red chi2'] = result.redchi

                if plot:
                    cnt+=1
                    ax=py.subplot(nrows,ncols,cnt)
                    ax.step(xdat, ydat,alpha=0.5)
                    ax.plot(xdat, bestfit, label='red chi: %.2f'%result.redchi)
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
            print("failed mod expo fit for run: %d, pixel: %s"%(run_number,pixel))
            py.close(fig)
            return {}
        
        return df
    
def get_mod_expo_results(energy, bin_edges, pixel, run_numbers,plot=False,source='cd'):
    results = {}
    peak_finder_props = (10,None,5,35,3,None,0.5,None)
    if int(pixel)>1000:
        sigs0_df = {'sig1':20,'sig2':25}
        low_region = 100
    else:
        sigs0_df = {'sig1':5,'sig2':5}
        low_region = 20
    for i in run_numbers:
        if not any(value==pixel for value in energy[i].keys()) or np.argmax(energy[i][pixel][40:])>300 or max(energy[i][pixel][40:])<1000:
            pass
        else:
            try:
                r = get_mod_expo_fit_long(i,energy[i],bin_edges,pixel,low_region,400,2,peak_finder_props,sigs0_df,2,source,plot=plot)
                if len(r)==0:
                    pass
                else:
                    results[i] = {}
                    results[i][0] = r
            except Exception as e:
                print(i,pixel,e)
    return results