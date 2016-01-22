/* Kwik2CellGroups
 * Brad Theilman 01/2016
 */

 #define STIMNAMEMAX 255

/* Linked list node for a spike */
typedef struct spike_t {
	spike_t *prev;
	spike_t *next;
	int spike_time;
	int cluster_id;
	int cluster_group;
} spike_t;

typedef struct trial_t {
	trial_t *prev;
	trial_t *next;
	int stim_start_time;
	int stim_end_time;
	char stim_name[STIMNAMEMAX];
	spike_t *spike_list;  /* pointer to head of spike list */
} trial_t;


spike_t *spike_list_make_empty()
{
	spike_t *list;
	list = NULL;
	return list;
}

spike_t *spike_list_add(spike_t *list, spike_t *spike)
{
	if (list == NULL) {
		return spike;
	} else {
		if (list->next == NULL) {
			list->next = spike;
			spike->prev = list;
		} else {
			spike_list_add(list->next, spike);
		}
		return list;
	}
}

void spike_list_remove(spike_t *list, spike_t *spike)
{
	if (list != NULL) {
		if (spikecmp(list, spike)){
			spike_t *prev = list->prev;
			spike_t *next = list->next;
			prev->next = next;
			next->prev = prev;
			return;
		} else {
			spike_list_remove(list->next, spike);
		}
	} else {
		printf("spike_list_remove: Spike not in list!!\n");
	}
}

spike_t *spike_list_slice(spike_t *list, int t_start, int t_end)
{
	/* Cuts out a chunk from the spike list where
	 * t_start <= spike_time <= t_end
	 */
	 /* TODO */
	 return NULL

}

int spikecmp(spike_t *spike1, spike_t *spike2)
{
	if ((spike1->spike_time == spike2->spike_time) && (spike1->cluster_id == spike2->cluster_id)) {
		return 1;
	} else {
		return 0;
	}
}


