import numpy as np
from lmfit import Minimizer, Parameters
from scipy import special
import json

def gauss(z,p1):
    return p1*np.exp(-0.5*(z)**2)

def step_function(z,p6):
    return p6/(1+np.exp(z))**2

def lower_exp(z,p4,p5):
    return p4*(np.exp(p5*z))/(1+np.exp(z))**4

def background(x,p7,p8):
    return p7*x+p8

def D1(x,n,x0,beta,sig):
    return n*np.exp((x-x0)/beta)*(1-special.erf((x-x0)/(np.sqrt(2)*sig) + sig/(np.sqrt(2)*beta)))

def get_hist_data_uncert(data):
    alpha = np.sqrt(data)
    for k in range(len(alpha)):
        if alpha[k]<1:
            alpha[k]=1
    return alpha

def linear_model(params, x):
    m = params['m'].value
    b = params['b'].value
    return m * x + b

def linear_residual(params, x, y, yerr):
    model = linear_model(params,x)
    residual = (model - y) / yerr
    return residual

def quad_model(params, x):
    q = params['q'].value
    m = params['m'].value
    b = params['b'].value
    return q * x**2 + m*x + b

def quad_residual(params, x, y, yerr):
    model = quad_model(params,x)
    residual = (model - y) / yerr
    return residual

def get_fit(model,residuals,params,xdat,ydat,alpha):
    mini = Minimizer(residuals, params, fcn_args=(xdat, ydat, alpha))
    result = mini.minimize()
    bestfit = model(result.params, xdat)
    return bestfit, result

def get_energy_time_data(run_numbers,detector_type='UDET',data_type='calibration'):
    data = {}
    time = {}
    for i in range(len(run_numbers)):
        if data_type=='pulser':
            with open('HistData/PulserData/%s/%spulser_data%d.json'%(detector_type,detector_type,run_numbers[i]), 'r') as file:
                d = json.load(file)
        else:
            if detector_type=='LDET':
                with open('HistData/EnergyData/%s/%senergy_data%d_short_trap.json'%(detector_type,detector_type,run_numbers[i]), 'r') as file:
                    d = json.load(file)
            else:
                with open('HistData/EnergyData/%s/%senergy_data%d.json'%(detector_type,detector_type,run_numbers[i]), 'r') as file:
                    d = json.load(file)
        data[run_numbers[i]] = d
        with open('HistData/TimeData/time_data%d.json'%run_numbers[i], 'r') as file:
            t = json.load(file)
        time[run_numbers[i]] = t
    return data, time

def get_summed_df(data):
    df = {}
    for j in data['hist']['0'].keys():
        num_bins = len(data['hist']['0'][j])
        energy_sum = np.zeros(num_bins)
        for i in range(len(data['hist'])):
            energy_sum+=np.array(list(data['hist']['%d'%i][j]))
        df[j] = list(energy_sum)
    return df

def get_energy(run_numbers,data):
    energy = {}
    for i in run_numbers:
        energy[i] = get_summed_df(data[i])
    return energy

def get_results_df(results, energy, bin_edges, pixels, run_numbers, plot=False,pulser=False,BC=112,raw_pulser_bin_edges=None,detector_type=None):
    df = {}
    for i in range(len(pixels)):
        df[pixels[i]] = results(energy, bin_edges, pixels[i], run_numbers, plot=plot,detector_type=detector_type)
    if pulser:
        df['BC %d'%BC] = results(energy, raw_pulser_bin_edges, 'pulser BC %d'%BC, run_numbers, plot=plot,detector_type=detector_type)

    non_empty_df = {}
    for i in df.keys():
        if list(df[i].keys())==[]:
            continue
        else:
            non_empty_df[i] = df[i]
    return non_empty_df

def get_cal_peaks_df(result_df,simulated_keV_values,simulated_keV_errors):
    df = {}
    width_df = {}
    amp_df = {}
    pixels = list(result_df.keys())
    for i in range(len(pixels)):
        df[pixels[i]] = {}
        width_df[pixels[i]] = {}
        amp_df[pixels[i]] = {}
        runs = list(result_df[pixels[i]].keys())
        for j in range(len(runs)):
            df[pixels[i]][runs[j]] = {}
            width_df[pixels[i]][runs[j]] = {}
            amp_df[pixels[i]][runs[j]] = {}
            run_results = result_df[pixels[i]][runs[j]]
            try:
                df[pixels[i]][runs[j]]['peak1'] = run_results[0]['cen1']
                df[pixels[i]][runs[j]]['peak2'] = run_results[0]['cen2']
                width_df[pixels[i]][runs[j]]['peak1'] = run_results[0]['sig1']
                width_df[pixels[i]][runs[j]]['peak2'] = run_results[0]['sig2']
                amp_df[pixels[i]][runs[j]]['peak1'] = run_results[0]['amp1']
                amp_df[pixels[i]][runs[j]]['peak2'] = run_results[0]['amp2']
                df[pixels[i]][runs[j]]['peak1']['keV value'] = simulated_keV_values[0]
                df[pixels[i]][runs[j]]['peak1']['keV error'] = simulated_keV_errors[0]
                df[pixels[i]][runs[j]]['peak2']['keV value'] = simulated_keV_values[1]
                df[pixels[i]][runs[j]]['peak2']['keV error'] = simulated_keV_errors[1]
            except Exception as e:
                # print(pixels[i],runs[j],e,1)
                pass

            try:
                df[pixels[i]][runs[j]]['peak3'] = run_results[1]['cen1']
                df[pixels[i]][runs[j]]['peak4'] = run_results[1]['cen2']
                df[pixels[i]][runs[j]]['peak5'] = run_results[1]['cen3']
                width_df[pixels[i]][runs[j]]['peak3'] = run_results[1]['sig1']
                width_df[pixels[i]][runs[j]]['peak4'] = run_results[1]['sig2']
                width_df[pixels[i]][runs[j]]['peak5'] = run_results[1]['sig3']
                amp_df[pixels[i]][runs[j]]['peak3'] = run_results[1]['amp1']
                amp_df[pixels[i]][runs[j]]['peak4'] = run_results[1]['amp2']
                amp_df[pixels[i]][runs[j]]['peak5'] = run_results[1]['amp3']
                df[pixels[i]][runs[j]]['peak3']['keV value'] = simulated_keV_values[2]
                df[pixels[i]][runs[j]]['peak3']['keV error'] = simulated_keV_errors[2]
                df[pixels[i]][runs[j]]['peak4']['keV value'] = simulated_keV_values[3]
                df[pixels[i]][runs[j]]['peak4']['keV error'] = simulated_keV_errors[3]
                df[pixels[i]][runs[j]]['peak5']['keV value'] = simulated_keV_values[4]
                df[pixels[i]][runs[j]]['peak5']['keV error'] = simulated_keV_errors[4]
            except Exception as e:
                # print(pixels[i],runs[j],e,2)
                pass
            
            try:
                df[pixels[i]][runs[j]]['peak6'] = run_results[2]['cen1']
                df[pixels[i]][runs[j]]['peak7'] = run_results[2]['cen2']
                df[pixels[i]][runs[j]]['peak8'] = run_results[2]['cen3']
                width_df[pixels[i]][runs[j]]['peak6'] = run_results[2]['sig1']
                width_df[pixels[i]][runs[j]]['peak7'] = run_results[2]['sig2']
                width_df[pixels[i]][runs[j]]['peak8'] = run_results[2]['sig3']
                amp_df[pixels[i]][runs[j]]['peak6'] = run_results[2]['amp1']
                amp_df[pixels[i]][runs[j]]['peak7'] = run_results[2]['amp2']
                amp_df[pixels[i]][runs[j]]['peak8'] = run_results[2]['amp3']
                df[pixels[i]][runs[j]]['peak6']['keV value'] = simulated_keV_values[5]
                df[pixels[i]][runs[j]]['peak6']['keV error'] = simulated_keV_errors[5]
                df[pixels[i]][runs[j]]['peak7']['keV value'] = simulated_keV_values[6]
                df[pixels[i]][runs[j]]['peak7']['keV error'] = simulated_keV_errors[6]
                df[pixels[i]][runs[j]]['peak8']['keV value'] = simulated_keV_values[7]
                df[pixels[i]][runs[j]]['peak8']['keV error'] = simulated_keV_errors[7]
            except Exception as e:
                # print(pixels[i],runs[j],e,3)
                pass

    return df, width_df, amp_df

def calibrate_data(calibration_data_points,calibration_amplitude,calibration_order='linear',uncertainty_scaling=False):
    df = {}
    if calibration_order=='linear':
        model = linear_model
        residuals = linear_residual
    if calibration_order=='quadratic':
        model = quad_model
        residuals = quad_residual
    pixels = list(calibration_data_points.keys())
    for i in range(len(pixels)):
        df[pixels[i]] = {}
        runs = list(calibration_data_points[pixels[i]].keys())
        for j in range(len(runs)):
            peaks = list(calibration_data_points[pixels[i]][runs[j]].keys())
            if len(peaks)>=6 and calibration_amplitude[pixels[i]][runs[j]]['peak3']['value']>50:
                peak_values = []
                peak_errors = []
                keV_values = []
                keV_errors = []
                for k in range(len(peaks)):
                    peak_values.append(calibration_data_points[pixels[i]][runs[j]][peaks[k]]['value'])
                    peak_errors.append(calibration_data_points[pixels[i]][runs[j]][peaks[k]]['error'])
                    keV_values.append(calibration_data_points[pixels[i]][runs[j]][peaks[k]]['keV value'])
                    keV_errors.append(calibration_data_points[pixels[i]][runs[j]][peaks[k]]['keV error'])
                params = Parameters()
                params.add('m', value=3)
                params.add('b', value=0)
                if calibration_order=='quadratic':
                    params.add('q', value=1e-5)

                if uncertainty_scaling==False:
                    bestfit, results = get_fit(model,residuals,params,np.array(keV_values),np.array(peak_values),np.array(peak_errors))
                if uncertainty_scaling==True:
                    bestfit, results = get_fit(model,residuals,params,np.array(keV_values),np.array(peak_values),np.array(peak_errors))
                    reduced_chi2 = results.redchi
                    if reduced_chi2 > 1.1 or reduced_chi2 < 0.9:
                        new_errors = np.array(peak_errors)*np.sqrt(reduced_chi2)
                        try:
                            bestfit, results = get_fit(model,residuals,params,np.array(keV_values),np.array(peak_values),new_errors)
                        except Exception as e:
                            print('failed new fit for pixel %s, run %d'%(pixels[i],runs[j]))
            else:
                continue
            df[pixels[i]][runs[j]] = results
    return df

def get_calibration_fit_params(results,gain=False,offset=False,quad=False):
    pixels = list(results.keys())
    df = {}
    for pixel in pixels:
        runs = list(results[pixel].keys())
        if runs==[]:
            continue
        df[pixel] = {}
        for run in runs:
            df[pixel][run] = {}
            if gain==True:
                df[pixel][run]['value'] = results[pixel][run].params['m'].value
                df[pixel][run]['error'] = results[pixel][run].params['m'].stderr
            if offset==True:
                df[pixel][run]['value'] = results[pixel][run].params['b'].value
                df[pixel][run]['error'] = results[pixel][run].params['b'].stderr
            if quad==True:
                df[pixel][run]['value'] = results[pixel][run].params['q'].value
                df[pixel][run]['error'] = results[pixel][run].params['q'].stderr
    return df

def get_calibration_param_props(param_df,weighted=False):
    pixels = list(param_df.keys())
    average = {}
    standard_deviation = {}
    average_error = {}
    for pixel in pixels:
        runs = list(param_df[pixel].keys())
        values = []
        errors = []
        for run in runs:
            values.append(param_df[pixel][run]['value'])
            errors.append(param_df[pixel][run]['error'])
        average_error[pixel] = np.average(errors)
        if weighted==False:
            average[pixel] = np.average(values)
            if len(runs)==1:
                continue
            else:
                standard_deviation[pixel] = np.std(values)
        if weighted==True:
            average[pixel] = np.average(values,weights=errors)
            if len(runs)==1:
                continue
            else:
                weights = 1/(np.array(errors)**2)
                varience = 1/np.sum(weights)
                standard_deviation[pixel] = np.sqrt(varience)
    return average,average_error,standard_deviation