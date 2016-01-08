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

def get_args():
    parser = argparse.ArgumentParser(description='Convert manually sorted KWIK file to pandas DataFrame')
    parser.add_argument('datafile', nargs='?', help='Path to PANDAS DataFrame containing spike data')
    parser.add_argument('dest', default='./', nargs='?', help='Directory in which to place raster plots')

    return parser.parse_args()

def main():
	print('Make Raster')
	args = get_args()
	datafile = os.path.abspath(args.datafile)
	dest = os.path.abspath(args.dest)

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
			cellinfo = {'cellid': cellind, 'sort_type': 'Unimplemented'}
			stiminfo = {'stim_name': simnm, 'start_time': 0.0, 'end_time': 1.0}
			expinfo = {'bird': 'Unimplemented', 'site': 'unimplemented'}

			events = cellstimdata[['stim_aligned_time_stamp_seconds', 'stim_presentation']]
			events.rename(columns={'stim_aligned_time_stamp_seconds': 'TOE', 'stim_presentation': 'trial'})
			rasterplot = make_raster(events, cellinfo, stiminfo, expinfo)



def make_raster(events, cell, stim, experiment):
	''' Generate a well-formated raster plot with all metadata

		events: DataFrame with TOE, trial columns
		cell: Dict with cellid, sort_type
		stim: Dict with stim_name, StartTime, EndTime
		experiment: Dict with Bird, Site XYZ, DataFrame
	'''

	raster = plt.figure()
	ntrials = events['trial'].unique().size
	for i in range(ntrials):
		spikes_this_trial = events.loc[events['trial'] == i+1, 'TOE'].values.astype('float')
		# get number of spikes in this trial
		nspikes = np.size(spikes_this_trial)
		# generate ydata for this trial
		ylimits = [i, i+1]

		for j in range(nspikes):
			ydata = ylimits
			xdata = [spikes_this_trial[j], spikes_this_trial[j]]
			plt.plot(xdata, ydata, 'r')

	plt.title("Bird: " + experiment['bird'] + " Cell: " + str(cell['cellid']) + " Type: " + cell['sort_type'] + " Stim: " + stim['stim_name'])
	plt.xlabel('Time (s)')
	plt.ylabel('Trial')
	return raster

def save_raster(spike_raster, dest, cell, stim, exp):
	
	raster_fname = "cell_" + str(cell['cellid']) +"_stim_" + stim['stim_name'] _ "_raster.png"
	save_f = os.path.join(dest, raster_fname)
	spike_raster.savefig(save_f)

if __name__ == '__main__':
    main()