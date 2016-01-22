% From population vectors, generate cell groups
% Must activate Plex library before running
clear
close all

load('/Users/brad/Documents/Research/GentnerLab/st1215_cat_P01_S01_2ndPen_moremerged_20151102T090824_popvec.mat');

%population_vectors(ncell, nwin, nstim, nbinstart);
[ncell, nwin, nstim, n_bin_start] = size(population_vectors);

%first compute average firing rate for cell:
avg_fr = sum(sum(sum(population_vectors, 4), 3), 2)/(nwin*nstim*n_bin_start);

%threshold population vectors with FR > 6*avgFR
cell_thresh = repmat(6*avg_fr, [1, nwin, nstim, n_bin_start]);
cell_groups = population_vectors > cell_thresh;

% pull out activity during stimulus
% windows_in_stim = (windows_starts >= 0 - bin_width & (windows_starts + bin_width) <= 1500 + bin_width)';
% window_win = squeeze(windows_in_stim(:, 2));
% cell_groups = cell_groups(:, window_win, :, :);

% Now, build simplicial complex
stream = api.Plex4.createExplicitSimplexStream();

% Add vertices for each cell
for i = 1:ncell
    stream.addVertex(i);
end

%% Now go through each population vector and add simplicial complex
for win = 1:nwin
    for stim = 1:nstim
        for binst = 1:n_bin_start
            cell_group_this = squeeze(cell_groups(:, win, stim, binst));
            cells_in_this_group = find(cell_group_this);
            if(any(cells_in_this_group))
                cells_in_this_group;
                stream.addElement(cells_in_this_group);
                stream.ensureAllFaces();
            end
        end
    end
end
stream.finalizeStream();

%% Compute homology
persis = api.Plex4.getModularSimplicialAlgorithm(10, 7);
persis.computeIntervals(stream)