import numpy as numpy
import glob 
import sys
import os

def main():

	bettifiles = glob.glob('*_betti.txt')

	for bettifile in bettifiles:
		with open(bettifile, 'r') as fd:
			for line in fd:
				bettidata = line.split(' ')
				nbetti = len(bettidata) - 1 # First element is filtration level, always 1
				
