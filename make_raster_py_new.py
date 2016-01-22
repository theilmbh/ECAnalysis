#!/usr/bin/env python
# This script makes various kinds of raster plots from pandas data and saves them
# Brad Theilman 010716

import h5py
import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse
import glob
import os
try: import simplejson as json
except ImportError: import json
import spike_funcs as btsf

sort_types_dict = {'2': 'Good', '0': 'Noise', '1': 'MUA', '3': 'Unsorted'}

def get_args():
    parser = argparse.ArgumentParser(description='Convert manually sorted KWIK file to pandas DataFrame')
    parser.add_argument('datadir', nargs='?', help='Path to directory with PANDAS DataFrame containing spike data')
    parser.add_argument('destdir', default='./', nargs='?', help='Directory in which to place raster plots')

    return parser.parse_args()

def main():
	print('Make Raster')
	args = get_args()
	data_folder = os.path.abspath(args.datadir)
	dest_folder = os.path.abspath(args.destdir)

	info_json = glob.glob(os.path.join(data_folder,'*_info.json'))[0]
	with open(info_json, 'r') as f:
		experiment = json.load(f)

	pd_data_file = os.path.join(data_folder,info['name']+'.pd')
	# open the datafile
	spikedata = pd.read_pickle(pd_data_file)
	make_raster(spikedata, experiment)


def make_raster(spike_data, experiment, prestim, poststim):
	# get number of units, number of stims
	cells = btsf.get_cluids(spikedata)
	stim_names = btsf.get_stim_names(spikedata)
	for stimn in stim_names:
		ntrials = btsf.get_num_trials(spikedata, stimn)

		for cluid in cells:
			cellstimdata = btsf.find_spikes_by_stim_name(btsf.find_spikes_by_cluid(spikedata, cluid), stimnm)
			cell_clugroup = btsf.get_clugroups(cellstimdata)
			plt.figure()

			for trialnum in range(ntrials):
				spikes_to_plot = btsf.find_spikes_stim_trial(cellstimdata, stimn, trialnum)
				[stim_start_samps, stim_end_samps] = btsf.get_stim_times(cellstimdata, stimnm, trialnum)
				stim_start = (stim_start_samps - stim_start_samps)/info['fs']
				stim_end = (stim_end_samps - stim_start_samps)/info['fs']
				nspikes = btsf.get_num_spikes(spikes_to_plot)
				spiketimes = btsf.get_spike_times_seconds_stim_aligned(spikes_to_plot)
				ylimits = [trialnum, trialnum+1]

				for j in range(nspikes):
					ydata = ylimits
					xdata = [spiketimes[j], spiketimes[j]]
					plt.plot(xdata, ydata, 'b')

				stim_start_x = [stim_start, stim_start]
				stim_end_x = [stim_end, stim_end]
				stim_start_y = [0, ntrials]
				stim_end_y = [0, ntrials]

				plt.plot(stim_start_x, stim_start_y, 'r')
				plt.plot(stim_end_x, stim_end_y, 'r')
				plt.title("Bird: " + experiment['name'] + " Cell: " + str(cluid) + " Type: " + str(cell_clugroup) + " Stim: " + stimn)
				plt.xlabel('Time (s)')
				plt.ylabel('Trial')
				plt.xlim(-1.0*prestim, poststim + stim_end)
				plt.ylim(0, ntrials)


def make_raster(events, cell, stim, experiment, plot_args):
	''' Generate a well-formated raster plot with all metadata

		events: dataframe
		cell: Dict with cellid, sort_type
		stim: Dict with stim_name, StartTime, EndTime
		experiment: Dict with Bird, Site XYZ, DataFrame
	'''

	raster = plt.figure()
	ntrials = btsf.get_num_trials(events)
	
	for i in range(ntrials):
		spikes_this_trial = events.loc[events['trial'] == i, 'TOE'].values.astype('float')
		# get number of spikes in this trial
		nspikes = btsf.get_num
		# generate ydata for this trial
		ylimits = [i, i+1]

		for j in range(nspikes):
			ydata = ylimits
			xdata = [spikes_this_trial[j], spikes_this_trial[j]]
			plt.plot(xdata, ydata, 'b')

	stim_start_x = [stim['start'], stim['start']]
	stim_start_y = [0, ntrials]
	stim_end_x = [stim['end'], stim['end']]
	stim_end_y = [0, ntrials]
	plt.plot(stim_start_x, stim_start_y, 'r')
	plt.plot(stim_end_x, stim_end_y, 'r')

	plt.title("Bird: " + experiment['bird'] + " Cell: " + str(cell['cellid']) + " Type: " + str(cell['sort_type']) + " Stim: " + stim['stim_name'])
	plt.xlabel('Time (s)')
	plt.ylabel('Trial')
	plt.xlim(-1.0*plot_args['prestim'], plot_args['poststim'] + stim['end'])
	plt.ylim(0, ntrials)

	return raster

def save_raster(spike_raster, dest, cell, stim, exp):
	raster_fname = exp['bird'] + "_cell_" + str(cell['cellid']) +"_stim_" + stim['stim_name'] + "_raster.png"
	print('Saving Raster: ' + raster_fname)
	save_f = os.path.join(dest, raster_fname)
	spike_raster.savefig(save_f)
	plt.close(spike_raster)

if __name__ == '__main__':
    main()