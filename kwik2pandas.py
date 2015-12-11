
# coding: utf-8

# In[1]:

get_ipython().magic(u'pylab inline')
import h5py
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
figsize(16.0, 4.0)

kwikfile = '/home/mthielk/Data/B979/acute/analysis/klusta/Pen04_Lft_AP2555_ML500__Site02_Z2688__st979_cat_P04_S02_1/st979_cat_P04_S02_1.kwik'


# In[2]:

from collections import Counter
class StimCounter(Counter):
    def count(self, key):
        self[key] += 1
        return self[key] - 1


# In[3]:

with h5py.File(kwikfile, 'r') as f:
    sample_rate = None
    for recording in f['recordings']:
        assert sample_rate is None or sample_rate == f['recordings'][recording].attrs['sample_rate']
        sample_rate = f['recordings'][recording].attrs['sample_rate']
    spikes = pd.DataFrame({ 'time_stamp' : f['channel_groups']['0']['spikes']['time_samples'],
                            'cluster' : f['channel_groups']['0']['spikes']['clusters']['main'] })
    cluster_groups = {}
    for cluster in f['channel_groups']['0']['clusters']['main'].keys():
        cluster_groups[int(cluster)] = f['channel_groups']['0']['clusters']['main'][cluster].attrs['cluster_group']
    spikes['cluster_group'] = spikes['cluster'].map(cluster_groups)
    
    with f['event_types']['DigMark']['codes'].astype('str'):
        stims = pd.DataFrame({ 'time_stamp' : f['event_types']['DigMark']['time_samples'],
                               'code' : f['event_types']['DigMark']['codes'][:] })
    stims.loc[stims.code == '<', 'stim_end_time_stamp'] = stims[stims['code'] == '>']['time_stamp'].values
    stims = stims[stims['code'] == '<']
    stims['stim_name'] = f['event_types']['Stimulus']['text'][1::2]
stims['stim_presentation'] = stims[stims['code'] == '<']['stim_name'].map(StimCounter().count)
stims.reset_index(drop=True, inplace=True)


class Stims(object):
    # ['code', 'time_stamp', 'stim_end_time_stamp', 'stim_name', 'stim_presentation']
    # TODO: duplicate spikes that are <2 sec from 2 stimuli
    def __init__(self, stims, stim_index=0):
        self.stim_index = stim_index
        self.stims = stims
        self.prev_stim = None
        self.cur_stim = self.stims.loc[self.stim_index].values
        self.next_stim = self.stims.loc[self.stim_index+1].values
    def stim_checker(self, time_stamp):
        if time_stamp < self.cur_stim[1]:
            if self.stim_index == 0 or self.cur_stim[1] - time_stamp < time_stamp - self.prev_stim[2]:
                return self.cur_stim[[3, 4, 1]]
            else:
                return self.prev_stim[[3, 4, 1]]
        elif time_stamp < self.cur_stim[2]:
            return self.cur_stim[[3, 4, 1]]
        else:
            if self.stim_index + 1 < len(self.stims):
                #print time_stamp, self.stim_index
                self.stim_index += 1
                self.prev_stim = self.cur_stim
                self.cur_stim = self.next_stim
                if self.stim_index + 1 < len(self.stims):
                    self.next_stim = self.stims.loc[self.stim_index+1].values
                else:
                    self.next_stim = None
                return self.stim_checker(time_stamp)
            else:
                return self.cur_stim[[3, 4, 1]]

get_ipython().magic(u'time spikes[\'stim_name\'], spikes[\'stim_presentation\'], spikes[\'stim_time_stamp\'] = zip(*spikes["time_stamp"].map(Stims(stims).stim_checker))')

spikes['stim_aligned_time_stamp'] = spikes['time_stamp'].values.astype('int') - spikes['stim_time_stamp'].values
#print(stims)
#print(spikes)



# In[4]:

spikes['morph_dim'] = spikes[~spikes.stim_name.str.contains('rec')].stim_name.str[0:2]
spikes['morph_pos'] = spikes[~spikes.stim_name.str.contains('rec')].stim_name.str[2:].astype(int)


# In[5]:

get_ipython().magic(u"time spikes['stim_aligned_time'] = spikes['stim_aligned_time_stamp'].values / sample_rate")
good_spikes = spikes[spikes['cluster_group'] == 2]
get_ipython().magic(u"time rec_stims = good_spikes[good_spikes.stim_name.str.contains('rec')]")


# In[50]:

sns.set_context("notebook", font_scale=1.5, rc={'lines.markeredgewidth': .1, 'patch.linewidth':1})
sns.set_style("white")
num_repeats = np.max(rec_stims['stim_presentation'].values)
stim_length = (stims.stim_end_time_stamp.head(1).values[0] - stims.time_stamp.head(1).values[0]) / sample_rate
for cluster in np.unique(rec_stims['cluster'].values):
#for cluster in (44, 182):
    g = sns.FacetGrid(rec_stims[rec_stims['cluster']==cluster], col="stim_name", col_wrap=3, xlim=(-.5, 1), ylim=(0,num_repeats));
    g.map(plt.scatter, "stim_aligned_time", "stim_presentation", marker='|')
    for ax in g.axes.flat:
        ax.plot((0, 0), (0, num_repeats), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, num_repeats), c=".2", alpha=.5)
    g = g.set_titles("cell %d, stim: {col_name}" % (cluster))


# In[39]:

sns.set_context("notebook", font_scale=1.5, rc={'lines.markeredgewidth': .1, 'patch.linewidth':1})
sns.set_style("white")
stim_length = (stims.stim_end_time_stamp.head(1).values[0] - stims.time_stamp.head(1).values[0]) / sample_rate
#for cluster in np.unique(rec_stims['cluster'].values):
#for cluster in (44, 182):
#    for morph_dim in ('ae', 'cg'):
for cluster in (44):
    for morph_dim in ('ae'):
        morph_spikes = good_spikes[(good_spikes['morph_dim']==morph_dim) & (good_spikes['cluster']==cluster)]
        num_repeats = np.max(morph_spikes['stim_presentation'].values)
        g = sns.FacetGrid(morph_spikes, col="stim_name", col_wrap=16, xlim=(-.5, 1), ylim=(0,num_repeats));
        g.map(plt.scatter, "stim_aligned_time", "stim_presentation", marker='|')
        for ax in g.axes.flat:
            ax.plot((0, 0), (0, num_repeats), c=".2", alpha=.5)
            ax.plot((stim_length, stim_length), (0, num_repeats), c=".2", alpha=.5)
        g = g.set_titles("cell %d, stim: {col_name}" % (cluster))


# In[38]:

np.any(good_spikes['morph_dim']==morph_dim)


# In[18]:

def filtered_response(spk_times, tau = .01):
    spk_times = spk_times.reshape((-1, 1))
    norm_factor = 1. / (tau * np.sqrt(2. * np.pi))
    return lambda t: np.sum(np.exp(-(spk_times - t.reshape((1,-1))) ** 2 / (2 * tau * tau)), 0) / norm_factor
def plot_mean_fr(x, y, **kwargs):
    t = np.linspace(-1, 1.5, 1000)
    num_repeats = np.max(y) + 1
    flt_spks = filtered_response(x)
    plot(t, flt_spks(t) / num_repeats)
def plot_fr_dist(x, y, **kwargs):
    t = np.linspace(-1, 1.5, 1000)
    num_repeats = np.max(y) + 1
    flt_spks = filtered_response(x)
    plot(t, flt_spks(t) / num_repeats)
    for presentation in np.unique(y):
        pres_spks = x[y == presentation]
        flt_pres = filtered_response(pres_spks)
        plot(t, flt_pres(t), c=".2", alpha=.05)
def plot_fr_se(x, y, offset=0, **kwargs):
    time_samples = 1000
    t = np.linspace(-1, 1.5, time_samples)
    if x.size == 0 or y.size == 0:
        print x, y, offset
        return
    num_repeats = np.max(y) + 1
    flt_spks = filtered_response(x)
    mean_fr = flt_spks(t) / num_repeats + offset
    p, = plot(t, mean_fr, alpha=1, **kwargs)
    fr_dist = np.zeros((num_repeats, time_samples))
    for presentation in np.unique(y):
        pres_spks = x[y == presentation]
        flt_pres = filtered_response(pres_spks)
        fr_dist[presentation,:] = flt_pres(t)
    se = fr_dist.std(axis=0) / np.sqrt(num_repeats)
    gca().fill_between(t, mean_fr - se, mean_fr + se, color=p.get_color(), alpha=.5)
    


# In[49]:

ymax = .05
for cluster in (44, 182):
    g = sns.FacetGrid(rec_stims[rec_stims['cluster']==cluster], col="stim_name", col_wrap=3, xlim=(-.5, 1), ylim=(0,ymax));
    g.map(plot_fr_se, "stim_aligned_time", "stim_presentation")
    for ax in g.axes.flat:
        ax.plot((0, 0), (0, ymax), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, ymax), c=".2", alpha=.5)
    g = g.set_titles("cell %d, stim: {col_name}" % (cluster))
    g = g.set_axis_labels("Time from stim onset (S)", "Firing Rate (Hz)")
    plt.xticks([0, .5])


# In[33]:

ymax = .05
for cluster in (44, 182):
    g = sns.FacetGrid(rec_stims[rec_stims['cluster']==cluster], col="stim_name", col_wrap=3, xlim=(-.5, 1), ylim=(0,ymax));
    g.map(plot_fr_dist, "stim_aligned_time", "stim_presentation")
    for ax in g.axes.flat:
        ax.plot((0, 0), (0, ymax), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, ymax), c=".2", alpha=.5)
    g = g.set_titles("cell %d, stim: {col_name}" % (cluster))


# In[43]:

def plot_morph(good_spikes, cluster, morph_dim, spacing=.02, ymax=.04):
    plt.figure(figsize=(20,20))
    with sns.color_palette(sns.xkcd_palette(["twilight blue", "kermit green"]), 2):
        plt.subplot(222)
        stim_name = morph_dim[1]+"_rec"
        spks2plot = good_spikes[(good_spikes['cluster']==cluster) & (good_spikes['stim_name'].str.contains(stim_name))]
        plot_fr_se(spks2plot["stim_aligned_time"].values, spks2plot["stim_presentation"].values, label=stim_name)
        stim_name = morph_dim+'128'
        spks2plot = good_spikes[(good_spikes['cluster']==cluster) & (good_spikes['stim_name'].str.contains(stim_name))]
        plot_fr_se(spks2plot["stim_aligned_time"].values, spks2plot["stim_presentation"].values, label=stim_name)
        plt.legend(loc=1)
        ax = plt.gca()
        ax.plot((0, 0), (0, ymax), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, ymax), c=".2", alpha=.5)
        xlim(-.5, 1)
        ylim(0,ymax)
        plt.xticks([0, .5])
        plt.yticks([0, .5*ymax, ymax])
        plt.title('cell: %d   morph dim: %s' % (cluster, morph_dim))

        plt.subplot(224)
        stim_name = morph_dim[0]+"_rec"
        spks2plot = good_spikes[(spikes['cluster']==cluster) & (good_spikes['stim_name'].str.contains(stim_name))]
        plot_fr_se(spks2plot["stim_aligned_time"].values, spks2plot["stim_presentation"].values, label=stim_name)
        stim_name = morph_dim+'001'
        spks2plot = good_spikes[(spikes['cluster']==cluster) & (good_spikes['stim_name'].str.contains(stim_name))]
        plot_fr_se(spks2plot["stim_aligned_time"].values, spks2plot["stim_presentation"].values, label=stim_name)
        plt.legend(loc=1)
        ax = plt.gca()
        ax.plot((0, 0), (0, ymax), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, ymax), c=".2", alpha=.5)
        xlim(-.5, 1)
        ylim(0,ymax)
        plt.xticks([0, .5])
        plt.yticks([0, .5*ymax, ymax])

    with sns.color_palette(sns.diverging_palette(262, 359, s=99, l=43, sep=1, n=128, center="dark"), 128):
        plt.subplot(121)
        spks_morph = good_spikes[(good_spikes['cluster']==cluster) & (good_spikes['morph_dim']==morph_dim)]
        morph_ymax = 128*spacing+ymax
        for morph_pos in np.unique(spks_morph['morph_pos'].values):
            stim_name = morph_dim + str(int(morph_pos))
            spks2plot = spks_morph[spks_morph['morph_pos'] == morph_pos]
            plot_fr_se(spks2plot["stim_aligned_time"].values, spks2plot["stim_presentation"].values, offset=morph_pos*spacing, label=stim_name)
        ax = plt.gca()
        ax.plot((0, 0), (0, morph_ymax), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, morph_ymax), c=".2", alpha=.5)
        xlim(-.5, 1)
        ylim(0,morph_ymax)
        plt.xticks([0, .5])
        plt.yticks([])
        plt.tick_params(axis='y', which='both', bottom='off', top='off', labelbottom='off')
    sns.despine()


# In[44]:

ymax = .04
spacing = .02
sns.set_context(rc={'lines.linewidth': .5})
for cluster in (44, 182):
    for morph_dim in ('ae', 'cg'):
        plot_morph(good_spikes, cluster, morph_dim)


# In[7]:

get_ipython().magic(u"time MUA_spikes = spikes[spikes['cluster_group'] == 1]")
get_ipython().magic(u"time rec_stims_MUA = MUA_spikes[MUA_spikes.stim_name.str.contains('rec')]")


# In[45]:

sns.set_context(rc={'lines.markeredgewidth': .1, 'patch.linewidth':1})
num_repeats = np.max(rec_stims_MUA['stim_presentation'].values)
stim_length = (stims.stim_end_time_stamp.head(1).values[0] - stims.time_stamp.head(1).values[0]) / sample_rate
ymaxes = (.3, .04)
for idx, cluster in enumerate(np.unique(rec_stims_MUA['cluster'].values)):
    g = sns.FacetGrid(rec_stims_MUA[rec_stims_MUA['cluster']==cluster], col="stim_name", col_wrap=3, xlim=(-.5, 1), ylim=(0,num_repeats));
    g.map(plt.scatter, "stim_aligned_time", "stim_presentation", marker='|')
    for ax in g.axes.flat:
        ax.plot((0, 0), (0, num_repeats), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, num_repeats), c=".2", alpha=.5)
    g = g.set_titles("cell %d, stim: {col_name}" % (cluster))
    
    ymax = ymaxes[idx]
    g = sns.FacetGrid(rec_stims_MUA[rec_stims_MUA['cluster']==cluster], col="stim_name", col_wrap=3, xlim=(-1, 1.5), ylim=(0,ymax));
    g.map(plot_fr_se, "stim_aligned_time", "stim_presentation")
    for ax in g.axes.flat:
        ax.plot((0, 0), (0, ymax), c=".2", alpha=.5)
        ax.plot((stim_length, stim_length), (0, ymax), c=".2", alpha=.5)
    g = g.set_titles("cell %d, stim: {col_name}" % (cluster))


# In[46]:

ymaxes = (.3, .04)
spacings = (.07, .01)
sns.set_context(rc={'lines.linewidth': .5})
for idx, cluster in enumerate([193, 200]):
    for morph_dim in ('ae', 'cg'):
        plot_morph(MUA_spikes, cluster, morph_dim, ymax=ymaxes[idx], spacing=spacings[idx])


# In[34]:

np.sqrt(128)


# In[79]:

data2analyze = spikes[spikes['cluster'] == 44]
temp = data2analyze.time_stamp.values
temp2 = (temp[1:] - temp[0:-1]).astype(float) / sample_rate
data2analyze['pretime'] = np.concatenate(([0], temp2))
data2analyze['posttime'] = np.concatenate((temp2, [0]))
data2analyze = data2analyze[data2analyze.stim_name.str.contains('rec')]


# In[86]:

data2analyze['stim_aligned_time'] = data2analyze['stim_aligned_time_stamp'] / sample_rate
data2analzye = data2analyze[(data2analyze['stim_aligned_time'] > 0) & (data2analyze['stim_aligned_time'] < .5)]


# In[99]:

g = sns.FacetGrid(data2analyze, col='stim_name', col_wrap=3, xlim=(0,.5), ylim=(0,.5))
g.map(plt.scatter, "pretime", "posttime", s=1)


# In[88]:

data2analyze

