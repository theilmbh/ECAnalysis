% make_neurogram.m
% Brad Theilman September 2015

clear
close all

load('st1215_cat_P01_S01_3rdPen_20150927T155818.mat');

%TODO:  Get sampling frequency from data file.
fs = 31250.0;

nstims = 41;
n_units = length(toedata);

psth_winsize = 150; %ms
psth_winsize_samps = floor((psth_winsize/1000)*fs);

figure();
for stim_index = 1:nstims
    % unit_index is which cell you wish to plot
    
    spike_density = zeros(n_units, 1);
    for unit_index = 1:n_units
        
        % Get the data for the chosen cell
        unit_data = toedata{unit_index, 1};
        
        % Collapse across all trials.  
        trialdata = unit_data.stims{stim_index, 1};
        ntrials = length(trialdata.toes);
        spiketimes_across_trials = [];
        for trial = 1:ntrials
            spiketimes_across_trials = [spiketimes_across_trials; trialdata.toes{trial, 1}];
        end
        trial_length = floor(mean(trialdata.trial_end_times - trialdata.trial_start_times));
        stim_start = floor(mean(trialdata.stim_start_times - trialdata.trial_start_times));
        stim_end_secs = floor(mean(trialdata.stim_end_times - trialdata.stim_start_times))/fs;
        winnum = 1;
        for win_start = 1:psth_winsize_samps:trial_length
            
            win_end = min(win_start+psth_winsize_samps, trial_length) - stim_start;
            win_start_stim = win_start - stim_start;
            nspikes_in_win = sum(spiketimes_across_trials <= win_end/fs & spiketimes_across_trials >= win_start_stim/fs);
            spike_density(unit_index, winnum) = nspikes_in_win / (ntrials * (psth_winsize/1000));
            win_starts(winnum) = win_start_stim / fs;
            winnum = winnum+1;
        end
        
    end
    max_firing_rate = max(max(spike_density))
    subplot(7, 6, stim_index)
    imagesc(win_starts, 1:n_units, spike_density, [0 85] );
    colormap('gray');
    
    line([0, 0], [0, n_units+1], 'Color', 'red')
    line([stim_end_secs, stim_end_secs], [0, n_units+1], 'Color', 'red');
end

            
        