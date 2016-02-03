# cellgroups.py

import numpy as np
import pandas as pd 
import os

import spike_funcs as spf 

spikedatafile = "./somefile.pd"
bird = 'B999'

spikedata = pd.read_pickle(spikedatafile)
stim_names = spf.get_stim_names(spikedata)
prestim_dt = 2.0 # seconds pre stim to take
win_dt = 50 #milliseconds

for stim in stim_names:
	ntrials = spf.get_num_trials(spikedata, stim)
	for trial in range(ntrials):
		stim_period_vert_list = set()
		prestim_vert_list = set()

		stimtimes = get_stim_times(spikedata, stim, trial)
		trialdata = find_spikes_by_stim_trial(spikedata, stim, trial)
		prestimwin = [stimtimes[0] - 2.0, stimtimes[0]]

		# Subdivide a given time period into windows
		prestim_cg_win_list = win_subdivide(prestimwin)
		stim_cg_win_list = win_subdivide(stimtimes)

		for winl, winh in stim_cg_win_list:
			# Get cell groups
			cgs = spf.get_cluster_group(trialdata, winl, winh)
			# Convert to tuple and add to the vertex set list. 
			stim_period_vert_list.add(tuple(cgs))
		write_vert_list_to_perseus(stim_period_vert_list, stim, trial, bird)

		for winl, winh in prestim_cg_win_list:
			cgs = spf.get_cluster_group(trialdata, winl, winh)
			prestim_vert_list.add(tuple(cgs))
		write_vert_list_to_perseus(prestim_vert_list, stim, trial, bird)


def win_subdivide(win, nstarts, dt, fs):
	# given a large win, returns a list of subdivisions
	# nsubwin x 2 array:   Win1L Win1H
	#					   Win2L Win2H
	#					   Win3L Win3H

def write_vert_list_to_perseus(vert_list, destdir, stimn, trialnum, bird):
	# first create the output file name:
	fname = bird + '_' + stimn + '_' + str(trialnum) +'.pers'
	fname = os.path.join(destdir, fname)

	with open(fname) as fd:
		#write num coords per vertex
		fd.write('1\n')
		for grp in vert_list:
			grp_dim = len(grp) - 1
    		vert_str = str(grp)
    		vert_str = vert_str.replace('(', '')
    		vert_str = vert_str.replace(')', '')
    		vert_str = vert_str.replace(' ', '')
    		vert_str = vert_str.replace(',', ' ')
    		out_str = str(dim) + ' ' + vert_str + ' 1\n'
    		fd.write(out_str)


