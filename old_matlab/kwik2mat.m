% kwik to mat.  Get good units out of sorted kwik file with stimulus
% information and store in one well formatted mat file
% Brad Theilman August/September 2015

function kwik2mat(kwikfile, outfile)
% get information
kwikinfo = h5info(kwikfile);

% Get cluster and time information for each spike
spike_clusters = h5read(kwikfile, '/channel_groups/0/spikes/clusters/main');
spike_times = h5read(kwikfile, '/channel_groups/0/spikes/time_samples');

% extract all the unique cluster ids:
clusters = unique(spike_clusters);

%% Build a boolean vector with 1 by a cluster id if it is a good cluster
good_cluster_inds = zeros(1, length(clusters));

for i = 1:length(clusters)
    
    cluster_num = clusters(i);
    cluster_attr_path = strcat('/channel_groups/0/clusters/main/', num2str(cluster_num));
    cluster_group = h5readatt(kwikfile, cluster_attr_path, 'cluster_group');
    disp(cluster_group);
    %cluster_group 2 is Good
    % 1 is MU
    if cluster_group ~= 0
        good_cluster_inds(i) = 1;
        
    end
    
end
% vector containing IDs of good clusters
good_cluster_ids = clusters(logical(good_cluster_inds));
cluster_classes = cluster_group(logical(good_cluster_inds));

%% Now, pull all spikes that belong to good clusters
good_spikes = cell(length(good_cluster_ids), 2);
for i = 1:length(good_cluster_ids)
    cluster_num = good_cluster_ids(i);
    %pull spikes from teh good cluster
    this_cluster_spiketimes = spike_times(spike_clusters == cluster_num);
    good_spikes{i, 1} = cluster_num;
    good_spikes{i, 2} = this_cluster_spiketimes;
end

%% Now get stimulus information

digmark_timesamples = h5read(kwikfile, '/event_types/DigMark/time_samples');
digmark_codes = cell2mat(h5read(kwikfile, '/event_types/DigMark/codes'));
stim_timesamples = h5read(kwikfile, '/event_types/Stimulus/time_samples');
stim_codes = h5read(kwikfile, '/event_types/Stimulus/codes');
stim_text = h5read(kwikfile, '/event_types/Stimulus/text');

stim_start_times = double(digmark_timesamples(digmark_codes == '<'));
stim_end_times = double(digmark_timesamples(digmark_codes == '>'));
intertrial_start_times = double(digmark_timesamples(digmark_codes == '('));
intertrial_end_times = double(digmark_timesamples(digmark_codes == ')'));

stim_start_filename = cell2mat(stim_text);
stim_start_filename = stim_start_filename(2:2:end, :);
stim_start_filename = cellstr(stim_start_filename);

% stim_start_times = h5read(kwikfile, '/event_types/60/time_samples');
% stim_start_filename = h5read(kwikfile, '/event_types/60/stim_filename');
% stim_end_times = h5read(kwikfile, '/event_types/62/time_samples');
% intertrial_start_times = h5read(kwikfile, '/event_types/40/time_samples');
% intertrial_end_times = h5read(kwikfile, '/event_types/41/time_samples');

stim_files_unique = unique(stim_start_filename);
nstims = length(stim_files_unique);


%%
% For each stimulus, get number of trials for that stimulus
% start building final_mat
final_data = struct;
final_data.nstims = nstims;
numtrials = zeros(1, nstims);
stim_data = cell(nstims, 1);

for i = 1:nstims
    
    stim_entry = struct;
    numtrials(i) = sum(strcmp(stim_files_unique(i), stim_start_filename));
    
    stim_start_times_this_stim = stim_start_times(strcmp(stim_files_unique(i), stim_start_filename));
    stim_end_times_this_stim = stim_end_times(strcmp(stim_files_unique(i), stim_start_filename));
    stim_entry.name = stim_files_unique(i);
    stim_entry.start_times = stim_start_times_this_stim;
    stim_entry.end_times = stim_end_times_this_stim;
    stim_entry.ntrials = sum(strcmp(stim_files_unique(i), stim_start_filename));
    stim_data{i, 1} = stim_entry;
    
end

%% Go through each cell and build final data matrix

fs = 31250.0; % TODO: get fs from data file itself 
pre_stim_duration = 2; %in seconds
post_stim_duration = 2; %seconds
pre_stim_duration_samps = pre_stim_duration*fs;
post_stim_duration_samps = post_stim_duration*fs;

n_good_units = length(good_cluster_ids);
toedata = cell(n_good_units, 1);


for unit_num = 1:length(good_cluster_ids)
    
    unit_entry = struct;
    unit_entry.id = good_cluster_ids(unit_num);
    unit_entry.sort_class = cluster_classes(unit_num)
    stims = cell(nstims, 1);
    
    % Loop through each stimulus
    for stim_num = 1:nstims
        
        stim_unit_entry = struct;
        
        this_stim_data = stim_data{stim_num, 1};
        stim_unit_entry.name = this_stim_data.name;
        stim_unit_entry.ntrials = this_stim_data.ntrials;
        
        %create trial times
        trial_start_times = this_stim_data.start_times - pre_stim_duration_samps;
        trial_end_times = this_stim_data.end_times + post_stim_duration_samps;
        stim_unit_entry.stim_start_times = this_stim_data.start_times;
        stim_unit_entry.stim_end_times = this_stim_data.end_times;
        stim_unit_entry.trial_start_times = trial_start_times;
        stim_unit_entry.trial_end_times = trial_end_times;
        
        %Go through each trial to divy up spike times relative to stim
        %start
        toes = cell(this_stim_data.ntrials, 1);
        for trialnum = 1:this_stim_data.ntrials
            trial_start = trial_start_times(trialnum);
            trial_end = trial_end_times(trialnum);
            
            spiketimes_thisunit = double(good_spikes{unit_num, 2});
            spiketimes_samps_thistrial = spiketimes_thisunit(spiketimes_thisunit >= trial_start & spiketimes_thisunit <= trial_end);
            spiketimes_samps_thistrial_relstimonset = spiketimes_samps_thistrial - this_stim_data.start_times(trialnum);
            spiketimes_secs_thistrial_relstimonset = double(spiketimes_samps_thistrial_relstimonset) / fs;
            
            toes{trialnum, 1} = spiketimes_secs_thistrial_relstimonset;
        end
        stim_unit_entry.toes = toes;
        stims{stim_num, 1} = stim_unit_entry;     
    end
    
    unit_entry.stims = stims;
    toedata{unit_num, 1} = unit_entry;
   
end

%% Format output file name

data_to_save = struct();
data_to_save.birdID = '';
data_to_save.penetrationID = 1;
data_to_save.siteID = 1;
data_to_save.siteID = 1;
data_to_save.XYpos = [0, 0];
data_to_save.Zpos = 0;
data_to_save.target_structure = 'NCM';

data_to_save.fs = 31250;
data_to_save.toedata = toedata;

sav_date = datestr(now, 30);

save(outfile, 'toedata');

end

