%% make_raster_all_cells.m 
%  Given a toefile, plot a spike raster plot for all trials of all stimuli
%  Does this for every unit in the file, saving the figures to png
%  Brad Theilman September 2015

clear
close all

% Make a spike raster for a given cell

datafile = './pen2/more_merged/st1215_cat_P01_S01_2ndPen_moremerged_MUA20151102T092630';

load(strcat(datafile, '.mat'));
fs = 31250.0;


for unit_index = 1:31
    
    disp(unit_index)
    % Get the data for the chose cell
    unit_data = toedata{unit_index, 1};
    nstims = length(unit_data.stims);
    
    fig = gcf;
    fig.Visible='off'
    for stimnum = 1:nstims
        subplot(7, 7, stimnum)
        
        stim_data = unit_data.stims{stimnum, 1};
        stim_end_secs = double(stim_data.stim_end_times - stim_data.stim_start_times)/fs;
        ntrials = stim_data.ntrials;
        for trialnum = 1:ntrials
            ys = [trialnum-1, trialnum];
            if ~isempty(stim_data.toes{trialnum, 1})
                for spikenum = 1:length(stim_data.toes{trialnum, 1})
                    line([stim_data.toes{trialnum, 1}(spikenum), stim_data.toes{trialnum, 1}(spikenum)], ys);
                end
            end
            xlim([-2, stim_end_secs(trialnum)+2])
            ylim([0, ntrials]);
            line([0, 0], [0, ntrials+1], 'Color', 'red');
            line([stim_end_secs(trialnum), stim_end_secs(trialnum)], [0, ntrials+1], 'Color', 'red');
        end
    end
    
    fig.PaperUnits = 'inches';
    fig.PaperPosition = [0 0 11 8.5];
    fig.PaperPositionMode = 'manual';  % TODO: Save in a large resolution
    figfilename = strcat(datafile, '_cell', num2str(unit_index));
    print(figfilename, '-dpng', '-r600');
    close all
    
    
end
