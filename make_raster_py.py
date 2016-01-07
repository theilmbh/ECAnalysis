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
    parser.add_argument('datafile', type=str, nargs='?', help='Path to PANDAS DataFrame containing spike data')
    parser.add_argument('destination_dir', type=str, nargs='?', help='Directory in which to place raster plots')

    return parser.parse_args()

def main():
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
	

