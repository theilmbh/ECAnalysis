%% make_raster.m 
%  Given a toefile, plot a spike raster plot for all trials of one stimulus
%  for all units
%  Brad Theilman September 2015


clear
close all

load('st1215_cat_P01_S01_2ndPen_fixalignment_20150924T141526.mat');

fs = 31250.0; % TODO: get this from the data file

stimnum = 49;

nstims = 49; % TODO: get this from the data file

figure();
for unit_index= 1:31
    subplot(8, 4, unit_index)

    unit_data = toedata{unit_index, 1};
    stim_data = unit_data.stims{stimnum, 1};
    stim_end_secs = double(stim_data.stim_end_times - stim_data.stim_start_times)/fs;
    ntrials = stim_data.ntrials;
    for trialnum = 1:ntrials
        ys = [0 + trialnum, 1+trialnum];
        if ~isempty(stim_data.toes{trialnum, 1})
           for spikenum = 1:length( stim_data.toes{trialnum, 1})
           line([stim_data.toes{trialnum, 1}(spikenum), stim_data.toes{trialnum, 1}(spikenum)], ys);
           end
        end
        xlim([-2, stim_end_secs(trialnum)+2])
        ylim([0, ntrials+1]);
        line([0, 0], [0, ntrials+1], 'Color', 'red');
        line([stim_end_secs(trialnum), stim_end_secs(trialnum)], [0, ntrials+1], 'Color', 'red');
    end
end

