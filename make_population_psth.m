% make_population_psth

clear
close all

load('st1215_cat_P01_S01_3rdPen_20150927T155818.mat');

%TODO:  Get sampling frequency from data file.
fs = 31250.0;

nstims = 41;
n_units = length(toedata);

psth_winsize = 150; %ms
psth_winsize_samps = floor((psth_winsize/1000)*fs);

for stim_index = 1:nstims
    