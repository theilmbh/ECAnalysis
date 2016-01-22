%% make_raster.m 
%  Given a toefile, plot a spike raster plot for all trials of all stimuli
%  for a single unit
%  Brad Theilman September 2015

clear
close all

%% Make a spike raster for a given cell

load('st1215_cat_P01_S01_3rdPen_20150927T155818.mat');

%TODO:  Get sampling frequency from data file.
fs = 31250.0;

% unit_index is which cell you wish to plot
unit_index = 9;

% Get the data for the chosen cell
unit_data = toedata{unit_index, 1};
nstims = length(unit_data.stims);

% Plotting parameters
spike_color = 'blue';
stim_color = 'red';

figure();
for stimnum = 1:nstims
    subplot(7, 6, stimnum)
    stim_data = unit_data.stims{stimnum, 1};
    stim_end_secs = double(stim_data.stim_end_times - stim_data.stim_start_times)/fs;
    ntrials = stim_data.ntrials;
    for trialnum = 1:ntrials
        ys = [trialnum-1, trialnum];
        if ~isempty(stim_data.toes{trialnum, 1})
           for spikenum = 1:length( stim_data.toes{trialnum, 1})
           line([stim_data.toes{trialnum, 1}(spikenum), stim_data.toes{trialnum, 1}(spikenum)], ys, 'Color', spike_color);
           end
        end
        xlim([-2, stim_end_secs(trialnum)+2])
        ylim([0, ntrials]);
        line([0, 0], [0, ntrials+1], 'Color', stim_color);
        line([stim_end_secs(trialnum), stim_end_secs(trialnum)], [0, ntrials+1], 'Color', stim_color);
    end
end

