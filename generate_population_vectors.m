%cell groups
% Generate population vectors as in Curto&Itskov 2008

clear
close all

datafilename = 'st1215_cat_P01_S01_2ndPen_moremerged_20151102T090824';
load(strcat(datafilename, '.mat'));

%toedata = data_to_save.toedata;
% parameters for analysis
bin_width = 10; % time bin width for cell groups in ms
n_bin_start = 5; % number of different bin start times.
pre_stim_ms = 2000; % number of milliseconds pre-stim
post_stim_ms = 2000; % number of milliseconds post-stim
stim_ms = 1000; % stimuli duration in milliseconds

fs = 31250;

trial_duration = pre_stim_ms + post_stim_ms + stim_ms;
nwin = floor(trial_duration / bin_width);

starts_dt = floor(bin_width/n_bin_start); % equally spaced in each win.

% get n_bin_start starting points for the windows within one bin time frame
bin_starts = starts_dt.*[0:n_bin_start-1] - pre_stim_ms;

windows_starts = zeros(n_bin_start, nwin);
windows_ends = zeros(n_bin_start, nwin);

windows_starts(:, 1) = bin_starts;
windows_ends(:, 1) = bin_starts + bin_width;
for i = 2:nwin
    windows_starts(:, i) = windows_starts(:, i-1) + bin_width;
    windows_ends(:, i) = windows_ends(:, i-1) + bin_width;
end

% build population vectors
ncells = length(toedata);
nstim = 41;
population_vectors = zeros(ncells, nwin, nstim, n_bin_start);

% For each cell, for each stim, for each trial, count the number of spikes
% in each time bin to arrive at population vectors.
for cell = 1:ncells
    for stim = 1:nstim
        spiketimes = toedata{cell,1}.stims{stim, 1}.toes;
        ntrials = length(spiketimes);
        for bin_start = 1:n_bin_start
            spikecounts_thiscellstimbinst = zeros(1, 500);
            for trial = 1:ntrials
                spikes_this_trial = 1000*spiketimes{trial, 1}; %convert to ms
                Nspikes = length(spikes_this_trial);
                repspike = repmat(spikes_this_trial, [1, nwin]);
                repbinst = repmat(windows_starts(bin_start, :), [Nspikes, 1]);
                repbinend = repmat(windows_ends(bin_start, :), [Nspikes, 1]);
                bool_spike = repspike >= repbinst & repspike < repbinend;
                spikecounts_thistrial = sum(bool_spike, 1);
                spikecounts_thiscellstimbinst = spikecounts_thiscellstimbinst + spikecounts_thistrial;
            end
            rate_this = spikecounts_thiscellstimbinst / bin_width;
            population_vectors(cell, :, stim, bin_start) = rate_this;
        end
    end
end

% Save population vector data
% popvec_data_to_save = rmfield(data_to_save, 'toedata');
% popvec_data_to_save.popvecs = population_vectors;
% popvec_data_to_save.binwidth = bin_width;
% popvec_data_to_save.winstarts = windows_starts;
popvecfilename = strcat(datafilename, '_popvec');
save(popvecfilename, 'population_vectors', 'bin_width', 'windows_starts');


