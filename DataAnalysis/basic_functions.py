import numpy as np
from lmfit import Minimizer
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