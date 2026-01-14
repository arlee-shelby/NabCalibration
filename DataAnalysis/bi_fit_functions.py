import numpy as np
from lmfit import Parameters
import pylab as py
from scipy.signal import find_peaks
from DataAnalysis.basic_functions import gauss
from DataAnalysis.basic_functions import lower_exp
from DataAnalysis.basic_functions import step_function
from DataAnalysis.basic_functions import background
from DataAnalysis.basic_functions import get_hist_data_uncert
from DataAnalysis.basic_functions import get_fit

def bi_model(params,x):

    num_peaks = params['num_peaks'].value

    sig_ratio = params['sig_ratio'].value
    amp_ratio = params['amp_ratio'].value
    
    intercept = params['intercept'].value
    slope = params['slope'].value

    peak_func = 0
    for i in range(num_peaks):
        i+=1
        amp = params['amp%d'%i].value
        cen = params['cen%d'%i].value
        sig = params['sig%d'%i].value
        step_ratio = params['step%d_ratio'%i].value

        z = (x-cen)/sig

        peak = gauss(z,amp) + lower_exp(z,amp_ratio*amp,sig_ratio*sig) + step_function(z,step_ratio*amp)
        peak_func += peak
    
    linear_background = background(x, slope, intercept)

    return peak_func + linear_background

def LDETbi_model(params,x):

    num_peaks = params['num_peaks'].value
    
    intercept = params['intercept'].value
    slope = params['slope'].value
    # sig3 = params['sig3'].value

    peak_func = 0
    for i in range(num_peaks):
        i+=1
        amp = params['amp%d'%i].value
        cen = params['cen%d'%i].value
        sig = params['sig%d'%i].value
        

        z = (x-cen)/sig
        # if i==2:
        #     zs = (x-cen)/sig3
        #     step_ratio = params['step%d_ratio'%i].value
        #     peak = gauss(z,amp)+ step_function(zs,step_ratio*amp)
        # else:
        peak = gauss(z,amp)
        peak_func += peak
    
    linear_background = background(x, slope, intercept)

    return peak_func + linear_background

def bi_residual(params, x, y, alpha):
    model = bi_model(params, x)
    return (model - y) / alpha

def LDETbi_residual(params, x, y, alpha):
    model = LDETbi_model(params, x)
    return (model - y) / alpha

def add_bi_params(params,initial_peak_props):

    params.add('sig_ratio',value=0.05,min=0)
    params.add('amp_ratio',value=0.6,min=0, max=1)

    params.add('slope',value=-1e-3)
    params.add('intercept',value=0)

    for i in range(params['num_peaks'].value):
        i+=1
        params.add('amp%d'%i,value=initial_peak_props['amp%d'%i],min=0)
        params.add('cen%d'%i,value=initial_peak_props['cen%d'%i],min=0)
        params.add('sig%d'%i,value=initial_peak_props['sig%d'%i],min=0)
        params.add('step%d_ratio'%i, value=0.01,min=-1e-1, max=1)

def add_LDETbi_params(params,initial_peak_props):

    params.add('slope',value=-1e-3)
    params.add('intercept',value=0)

    for i in range(params['num_peaks'].value):
        i+=1
        params.add('amp%d'%i,value=initial_peak_props['amp%d'%i],min=0)
        params.add('cen%d'%i,value=initial_peak_props['cen%d'%i],min=0)
        # if i==1:
        params.add('sig%d'%i,value=initial_peak_props['sig%d'%i],min=0)
        # if i==2:
        #     params.add('step%d_ratio'%i, value=0.01,min=0, max=1)

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
        
        elif len(peaks)==num_peaks-1:
            if i!=num_peaks:
                initial_peak_props['amp%d'%i] = props['peak_heights'][i-1]
                initial_peak_props['cen%d'%i] = xdat[peaks[i-1]]
                initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
            else:
                initial_peak_props['amp%d'%i] = props['peak_heights'][-1]*0.5
                initial_peak_props['cen%d'%i] = xdat[peaks[-1]]+36
                initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
        else:
            if num_peaks==2:
                if i<num_peaks:
                    initial_peak_props['amp%d'%i] = max(ydat)
                    initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0])
                    initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
                else:
                    initial_peak_props['amp%d'%i] = max(ydat)*0.5
                    initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0])+36
                    initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
            if num_peaks==3:
                if i==1:
                    amp_scale = 1
                    cen_shift = 0
                if i==2:
                    amp_scale = 1/3
                    cen_shift = 216
                if i==3:
                    amp_scale = 1/6
                    cen_shift = 252
                initial_peak_props['amp%d'%i] = max(ydat)*amp_scale
                initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0]) + cen_shift
                initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]


    return initial_peak_props

def get_LDETinitial_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas):
    initial_peak_props = {}
    find_peaks.__defaults__ = peak_finder_props
    peaks, props = find_peaks(ydat)
    num_peaks = num_peaks

    if num_peaks==1:
        initial_peak_props['amp1'] = np.max(ydat)
        initial_peak_props['cen1'] = xdat[np.argmax(ydat)]+xdat[0]
        initial_peak_props['sig1'] = initial_peak_sigmas['sig1']
        initial_peak_props['amp2'] = initial_peak_props['amp1']
        initial_peak_props['cen2'] = initial_peak_props['cen1']*1.2
        initial_peak_props['sig2'] = initial_peak_sigmas['sig2']
    else:
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
                if i==num_peaks:
                    initial_peak_props['amp%d'%i] = props['peak_heights'][i-1]
                    initial_peak_props['cen%d'%i] = xdat[peaks[i-1]]
                    initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]

                    initial_peak_props['amp%d'%(i+1)] = initial_peak_props['amp%d'%i]
                    initial_peak_props['cen%d'%(i+1)] = initial_peak_props['cen%d'%i]
                    initial_peak_props['sig%d'%(i+1)] = initial_peak_sigmas['sig%d'%i]
            
            elif len(peaks)==num_peaks-1:
                if i!=num_peaks:
                    initial_peak_props['amp%d'%i] = props['peak_heights'][i-1]
                    initial_peak_props['cen%d'%i] = xdat[peaks[i-1]]
                    initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
                else:
                    initial_peak_props['amp%d'%i] = props['peak_heights'][-1]
                    initial_peak_props['cen%d'%i] = xdat[peaks[-1]]
                    initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
            else:
                if num_peaks==2:
                    if i<num_peaks:
                        initial_peak_props['amp%d'%i] = max(ydat)
                        initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0])
                        initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
                    else:
                        initial_peak_props['amp%d'%i] = max(ydat)*0.5
                        initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0])+36
                        initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]
                if num_peaks==3:
                    if i==1:
                        amp_scale = 1
                        cen_shift = 0
                    if i==2:
                        amp_scale = 1/3
                        cen_shift = 216
                    if i==3:
                        amp_scale = 1/6
                        cen_shift = 252
                    initial_peak_props['amp%d'%i] = max(ydat)*amp_scale
                    initial_peak_props['cen%d'%i] = (np.argmax(ydat)+xdat[0]) + cen_shift
                    initial_peak_props['sig%d'%i] = initial_peak_sigmas['sig%d'%i]


    return initial_peak_props

# def get_bi_fit_short(data,time_data,num_groups,pixel,low_region,up_region,num_peaks,peak_finder_props,initial_peak_sigmas,plot=False):
#     cnt = 0
#     nrows,ncols=8,4
#     py.figure(figsize=(8*ncols,6*nrows))
#     df = {}
#     df['time'] = {}
#     for i in range(num_groups):
#         df[i] = {}

#         xdat = np.array(data['bin_edges']['%d'%i][pixel][low_region:up_region])
#         ydat = np.array(data['hist']['%d'%i][pixel][low_region:up_region])
#         alpha = get_hist_data_uncert(ydat)
#         initial_peak_props = get_initial_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas)
#         params = Parameters()
#         params.add('num_peaks', value=num_peaks,vary=False)
#         add_bi_params(params,initial_peak_props)

#         model=bi_model
#         residual_model = bi_residual

#         bestfit, result = get_fit(model,residual_model, params, xdat, ydat,alpha)

#         if plot:
#             cnt+=1
#             ax=py.subplot(nrows,ncols,cnt)
#             ax.step(xdat, ydat, alpha=0.5)
#             ax.plot(xdat, bestfit, label='fit, no x error')

#         for key in result.params.keys():
#             df[i]['%s'%key] = {}
#             df[i]['%s'%key] = {}
#             df[i]['%s'%key]['value'] = result.params['%s'%key].value
#             df[i]['%s'%key]['error'] = result.params['%s'%key].stderr
#         df['time'][i] = time_data['%d'%i]['subgroup_start'][-8:]
#     return df

def get_LDETbi_fit_long(run_number,data,bin_edges,pixel,low_region,up_region,num_peaks,peak_finder_props,initial_peak_sigmas,plot=False):
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

        try:
            initial_peak_props = get_LDETinitial_peak_props(xdat,ydat,peak_finder_props,num_peaks,initial_peak_sigmas)

        except Exception as e:
            print('could not get initial peak props for run: %d, pixel: %s'%(run_number,pixel))
            return
        
        params = Parameters()
        params.add('num_peaks', value=num_peaks,vary=False)
        try:
            add_LDETbi_params(params,initial_peak_props)
            # print(params)
        except Exception as e:
            print('could not add params, run: %d, pixel: %s, low reg: %d'%(run_number,pixel,low_region),e)
            return

        if low_region<1000:
            # print(params)
            params.add('delta',min=0.9,max=1.3)
            params.add('cen2', value=initial_peak_props['cen1']*1.1,expr='cen1*delta')
            # params.add('sig3',value=initial_peak_props['sig2'])
            params.add('delta2',min=0.4,max=1,value=0.45)
            params.add('amp2', value=initial_peak_props['amp1']*0.45,expr='amp1*delta2')
            # params.add('delta1',min=-5,value=1.1)
            params.add('sig2',value=initial_peak_props['sig1'],min=0,expr='sig1')
        
        if low_region>1000:
            params.add('sig3',value=initial_peak_props['sig3'],min=0,expr='sig2')
            params.add('delta2',min=0,max=1)
            params.add('amp3',value=initial_peak_props['amp3'],min=0,expr='amp2*delta2')
            params.add('delta3',min=1,max=1.03)
            params.add('cen3',value=initial_peak_props['cen3'],min=0,expr='cen2*delta3')
        model=LDETbi_model
        residual_model = LDETbi_residual

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
                print("no errors found for run: %d, pixel: %s, region %d"%(run_number,pixel,region))
                py.close(fig)
                return
        except Exception as e:
            if low_region<=1000:
                region=1
            elif low_region==1200:
                region=2
            elif low_region>2000:
                region=3
            
            print("failed Bi fit for run: %d, pixel: %s, region %d"%(run_number,pixel,region))
            py.close(fig)
            return
        return df
    
def get_UDETbi_fit_long(run_number,data,bin_edges,pixel,low_region,up_region,num_peaks,peak_finder_props,initial_peak_sigmas,plot=False):
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
            add_bi_params(params,initial_peak_props)
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
                print("no errors found for run: %d, pixel: %s, region %d"%(run_number,pixel,region))
                py.close(fig)
                return
        except Exception as e:
            if low_region==100 or low_region==40 or low_region==50:
                region=1
            elif low_region==500 or low_region==800 or low_region==1200:
                region=2
            elif low_region==1100 or low_region==1500 or low_region==2700:
                region=3
            
            print("failed Bi fit for run: %d, pixel: %s, region %d"%(run_number,pixel,region))
            py.close(fig)
            return
        return df
    
def get_UDETbi_fit_results(energy, bin_edges, pixel, run_numbers,low_region=40,plot=False,detector_type='UDET'):
    sigs0_df = {'sig1':5,'sig2':5}
    sigs1_df = {'sig1':5,'sig2':6,'sig3':6}
    sigs2_df = {'sig1':5,'sig2':6,'sig3':6}

    if detector_type=='UDET':
        peak_finder_props = (10,None,5,35,3,None,0.5,None)
    if detector_type=='LDET':
        peak_finder_props = (10,None,5,35,6,None,0.5,None)
        if pixel=='1017' or pixel=='1021' or pixel=='1028' or pixel=='1032' or pixel=='1043' or pixel=='1054':
            low_region=50
        else:
            low_region=100
    results = {}

    for i in run_numbers:
        if not any(value==pixel for value in energy[i].keys()) or np.argmax(energy[i][pixel][low_region:])<300:
            # print('cd pixel')
            pass
        
        else:
            r1,r2,r3 = None,None,None
            idx1,idx2,idx3 = None,None,None
            if detector_type=='LDET':
                mean = np.mean(energy[i][pixel][low_region:400])
                if mean<15:
                    print('LDET average too low, run %d, pixel %s'%(i, pixel))
                    pass
                else:
                    # print('here1')
                    r = get_UDETbi_fit_long(i,energy[i],bin_edges,pixel,low_region,400,2,peak_finder_props,sigs0_df,plot=plot)
            else:
                # print('here2')
                r = get_UDETbi_fit_long(i,energy[i],bin_edges,pixel,low_region,400,2,peak_finder_props,sigs0_df,plot=plot)
            try:
                if detector_type=='UDET':
                    if r['amp1']['value']<15:
                        print('run: %d, pixel: %s too low amp, region 1'%(i, pixel))
                        pass
                    else:
                        r1 = r
                        idx1 = 0
                else:
                    # print('here3')
                    if r['amp1']['value']<15 or r['sig1']['value']<2 or r['sig2']['value']<2:
                        print('run: %d, pixel: %s too low amp, sig1 or sig2 region 1'%(i, pixel))
                        # print('here4')
                        pass
                    else:
                        # print('here5')
                        r1 = r
                        idx1 = 0
            except Exception as e:
                pass
            low_region2 = 1200
            high_region2 = 1900
            if detector_type=='LDET':
                if pixel=='1017' or pixel=='1021' or pixel=='1028' or pixel=='1032' or pixel=='1043' or pixel=='1054':
                    low_region2 = 800
                    high_region2 = 1300
            if detector_type=='UDET':
                if pixel=='9' or pixel=='91' or pixel=='95' or pixel=='96':
                    low_region2 = 500
                    high_region2 = 900
            r = get_UDETbi_fit_long(i,energy[i],bin_edges,pixel,low_region2,high_region2,3,peak_finder_props,sigs1_df,plot=plot)
            try:
                if r['amp1']['value']<15 or r['amp2']['value']<0 or r['amp3']['value']<0 or r['sig1']['value']<2 or r['sig2']['value']<2 or r['sig3']['value']<2:
                    print('run: %d, pixel: %s too low amp, region 2'%(i, pixel))
                    pass
                else:
                    r2 = r
                    idx2 = 1

            except Exception as e:
                pass
            
            low_region3 = 2700
            high_region3 = 3400
            if detector_type=='LDET':
                peak_finder_props = (10,None,20,35,6,None,0.5,None)
                if pixel=='1017' or pixel=='1021' or pixel=='1028' or pixel=='1032' or pixel=='1043' or pixel=='1054':
                    low_region3 = 1500
                    high_region3 = 2500
            if detector_type=='UDET':
                if pixel=='9' or pixel=='91' or pixel=='95' or pixel=='96':
                    low_region3 = 1100
                    high_region3 = 1600
            r = get_UDETbi_fit_long(i,energy[i],bin_edges,pixel,low_region3,high_region3,3,peak_finder_props,sigs2_df,plot=plot)
            try:
                if r['amp1']['value']<15:
                    print('run: %d, pixel: %s too low amp, region 3'%(i, pixel))
                    pass
                else:
                    r3 = r
                    idx3 = 2
            except Exception as e:
                pass

            if r1!=None or r2!=None or r3!=None:
                results[i] = {}
                if r1!=None:
                    results[i][idx1] = r1
                if r2!=None:
                    results[i][idx2] = r2
                if r3!=None:
                    results[i][idx3] = r3
        r = None
    return results

def get_LDETbi_fit_results(energy, bin_edges, pixel, run_numbers,low_region=40,plot=False):
    
    peak_finder_props = (10,None,15,45,3,None,0.5,None)
    sigs0_df = {'sig1':15,'sig2':25}
    sigs1_df = {'sig1':25,'sig2':35,'sig3':35}
    sigs2_df = {'sig1':30,'sig2':35,'sig3':35}

    results = {}
    for i in run_numbers:
        if not any(value==pixel for value in energy[i].keys()) or np.argmax(energy[i][pixel][40:])<300:
            pass
        
        else:
            r1,r2,r3 = None,None,None
            max_pnt = np.argmax(energy[i][pixel][:400])
            # if max_pnt>50:
            #     pass
            # else:
            #     low_region=max_pnt-70

            r = get_LDETbi_fit_long(i,energy[i],bin_edges,pixel,low_region,400,2,peak_finder_props,sigs0_df,plot=plot)
            try:
                if r['amp1']['value']<15:
                    print('run: %d, pixel: %s too low amp, region 1'%(i, pixel))
                    pass
                else:
                    r1 = r
                    idx1 = 0
            except Exception as e:
                pass
            
            r = get_LDETbi_fit_long(i,energy[i],bin_edges,pixel,1200,1900,3,peak_finder_props,sigs1_df,plot=plot)
            try:
                if r['amp1']['value']<15:
                    print('run: %d, pixel: %s too low amp, region 2'%(i, pixel))
                    pass
                else:
                    r2 = r
                    idx2 = 1

            except Exception as e:
                pass
            
            r = get_LDETbi_fit_long(i,energy[i],bin_edges,pixel,2400,3400,3,peak_finder_props,sigs2_df,plot=plot)
            try:
                if r['amp1']['value']<15:
                    print('run: %d, pixel: %s too low amp, region 3'%(i, pixel))
                    pass
                else:
                    r3 = r
                    idx3 = 2
            except Exception as e:
                pass

            if r1!=None or r2!=None or r3!=None:
                results[i] = {}
                if r1!=None:
                    results[i][idx1] = r1
                if r2!=None:
                    results[i][idx2] = r2
                if r3!=None:
                    results[i][idx3] = r3
        
    return results