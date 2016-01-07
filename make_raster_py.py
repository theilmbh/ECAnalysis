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

def make_raster(events, cell, stim, experiment):
	''' Generate a well-formated raster plot with all metadata

		events: DataFrame with TOE, trial columns
		cell: Dict with CellID, sort_type
		stim: Dict with StimName, StartTime, EndTime
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

def save_raster(spike_raster, dest):
	spike_raster.savefig(dest)

if __name__ == '__main__':
    main()