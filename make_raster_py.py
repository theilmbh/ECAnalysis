#!/usr/bin/env python
# This script makes various kinds of raster plots from pandas data and saves them
# Brad Theilman 010716

import h5py
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import glob
import os
import seaborn as sns
try: import simplejson as json
except ImportError: import json

sort_types_dict = {'2': 'Good', '0': 'Noise', '1': 'MUA', '3': 'Unsorted'}

def get_args():
    parser = argparse.ArgumentParser(description='Convert manually sorted KWIK file to pandas DataFrame')
    parser.add_argument('datafile', nargs='?', help='Path to directory with PANDAS DataFrame containing spike data')
    parser.add_argument('dest', default='./', nargs='?', help='Directory in which to place raster plots')

    return parser.parse_args()

def main():
	print('Make Raster')
	args = get_args()
	datafile = os.path.abspath(args.datafile)
	dest = os.path.abspath(args.dest)
	datafiledir, datafilename = os.path.split(datafile)
	exp_name, exp_ext = os.path.splitext(datafilename)

	info_json = os.path.join(datafiledir, exp_name + "_info.json")
	#info_json = glob.glob(os.path.join(datadir, '*_info.json'))[0]
	with open(info_json, 'r') as f:
		info = json.load(f)

	#[AP, L, Z] = zip(info['pen']['anterior'], info['pen']['lateral'])
	#pandas_datafile = os.path.join(datadir, info['name']+'.pd')

	# open the datafile
	spikedata = pd.read_pickle(datafile)
	# get number of units, number of stims
	cells = spikedata['cluster'].unique()
	stim_names = spikedata['stim_name'].unique()
	nstim = np.size(stim_names)

	for cellind in cells:
		for stimnm in stim_names:
			celldata = spikedata[spikedata['cluster'] == cellind]
			cellstimdata = celldata[celldata['stim_name'] == stimnm]

			stim_starts = cellstimdata['stim_time_stamp'].values
			stim_ends = cellstimdata['stim_end_time_stamp'].values
			stim_start_samps = np.unique(stim_starts)[0]
			stim_end_samps = np.unique(stim_ends)[0]
			stim_start = (stim_start_samps - stim_start_samps)/info['fs']
			stim_end = (stim_end_samps - stim_start_samps)/info['fs']

			cell_sort_type = np.unique(cellstimdata['cluster_group'].values)
			assert (np.size(cell_sort_type) == 1), "Cell has multiple sort types"

			cellinfo = {'cellid': cellind, 'sort_type': sort_types_dict[str(cell_sort_type[0])]}
			stiminfo = {'stim_name': stimnm, 'start': stim_start, 'end': stim_end}
			expinfo = {'bird': info['name'], 'site': '', 'fs': info['fs']}
			plot_args = {'prestim': 2.0, 'poststim': 2.0}

			events = cellstimdata[['stim_aligned_time_stamp_seconds', 'stim_presentation']]
			events.rename(columns={'stim_aligned_time_stamp_seconds': 'TOE', 'stim_presentation': 'trial'}, inplace=True)
			rasterplot = make_raster(events, cellinfo, stiminfo, expinfo, plot_args)
			save_raster(rasterplot, dest, cellinfo, stiminfo, expinfo)

def make_raster(events, cell, stim, experiment, plot_args):
	''' Generate a well-formated raster plot with all metadata

		events: DataFrame with TOE, trial columns
		cell: Dict with cellid, sort_type
		stim: Dict with stim_name, StartTime, EndTime
		experiment: Dict with Bird, Site XYZ, DataFrame
	'''

	raster = plt.figure()
	ntrials = events['trial'].unique().size
	
	for i in range(ntrials):
		spikes_this_trial = events.loc[events['trial'] == i, 'TOE'].values.astype('float')
		# get number of spikes in this trial
		nspikes = np.size(spikes_this_trial)
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