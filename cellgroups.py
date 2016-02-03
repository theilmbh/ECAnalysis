# cellgroups.py

import numpy as np
import pandas as pd 
import os

import spike_funcs as spf 

spikedatafile = "./somefile.pd"
bird = 'B999'


def get_args():
    parser = argparse.ArgumentParser(description='Make cellgroups with a certain window size')
    parser.add_argument('datafile', nargs='?', help='Path to directory with PANDAS DataFrame containing spike data')
    parser.add_argument('destdir', default='./', nargs='?', help='Directory in which to place raster plots')
    parser.add_argument('-t' dest='win_dt', default=50.0, help='Window size in milliseconds')
    parser.add_argument('-n', dest='numstarts', default=5, help='Number of window starts')
    parser.add_argument('-p', dest='prestim', default=2.0, help='Prestim time period in seconds')
    parser.add_argument('-f', dest='fs', default=31250.0, help='Sampling rate in Hertz')
    return parser.parse_args()

def main():

	args = get_args()
	spikedata = pd.read_pickle(args.datafile)

	prestim_dt = args.prestim # seconds pre stim to take
	win_n = args.numstarts
	win_dt = args.win_dt #milliseconds
	fs = args.fs
	print('Running make_cell_groups...\n')
	make_cell_groups(spikedata, win_dt, win_n, prestim_dt, fs)


def make_cell_groups(spikedata, win_dt, win_n, prestim_dt, fs):
	stim_names = spf.get_stim_names(spikedata)
	for stim in stim_names:
		ntrials = spf.get_num_trials(spikedata, stim)
		for trial in range(ntrials):
			print('make_cell_groups: Stim %s, Trial %s...\n' % (stim, trial))
			stim_period_vert_list = set()
			prestim_vert_list = set()

			print('- Extracting spikes\n')
			stimtimes = get_stim_times(spikedata, stim, trial)
			trialdata = find_spikes_by_stim_trial(spikedata, stim, trial)
			prestimwin = [stimtimes[0] - 2.0, stimtimes[0]]

			print('- Creating Windows\n')
			# Subdivide a given time period into windows
			prestim_cg_win_list = win_subdivide(prestimwin)
			stim_cg_win_list = win_subdivide(stimtimes)

			print('- Extracting stim period cell groups\n')
			for winl, winh in stim_cg_win_list:
				# Get cell groups
				cgs = spf.get_cluster_group(trialdata, winl, winh)
				# Convert to tuple and add to the vertex set list. 
				stim_period_vert_list.add(tuple(cgs))
			
			print('- Extracting prestim period cell groups\n')
			for winl, winh in prestim_cg_win_list:
				cgs = spf.get_cluster_group(trialdata, winl, winh)
				prestim_vert_list.add(tuple(cgs))
				
			print('- Writing perseus input files\n')	
			write_vert_list_to_perseus(stim_period_vert_list, destdir, stim, trial, bird)
			write_vert_list_to_perseus(prestim_vert_list, destdir, 'pretrial'+stim, trial, bird)
			print('DONE\n')


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

