# cellgroups.py

import numpy as np
import pandas as pd 

import spike_funcs as spf 

spikedatafile = "./somefile.pd"

spikedata = pd.read_pickle(spikedatafile)
stim_names = spf.get_stim_names(spikedata)
prestim_dt = 2.0 # seconds pre stim to take
win_dt = 50 #milliseconds

for stim in stim_names:
	ntrials = spf.get_num_trials(spikedata, stim)
	for trial in range(ntrials):
		stimtimes = get_stim_times(spikedata, stim, trial)
		trialdata = find_spikes_by_stim_trial(spikedata, stim, trial)
		prestimwin = [stimtimes[0] - 2.0, stimtimes[0]]

		# Subdivide a given time period into windows
		prestim_cg_win_list = win_subd(prestimwin)
		stim_cg_win_list = win_subd(stimtimes)

def win_subd(win, nstarts, dt, fs):
	# given a large win, returns a list of subdivisions

