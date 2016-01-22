/* Kwik2CellGroups
 * Brad Theilman 01/2016
 * 
 * Conventions: sl_ (spike list) tl_ (trial list)
 */


 #define STIMNAMEMAX 255
 #define SL_HEADER_ID -1

/* Linked list node for a spike */
typedef struct spike_t {
	spike_t *prev;
	spike_t *next;
	int spike_time;
	int cluster_id;
	int cluster_group;
} spike_t;

#define spike_list_t spike_t; /* make a spike list type */

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
	/* We use a header implementation of the double linked list.  */
	spike_t *list = malloc(sizeof(spike_t));
	list->prev = NULL;
	list->next = NULL;
	list->cluster_id = SL_HEADER_ID;
	return list;
}

int spike_list_is_empty(sl_t *list)
{
	return list->next == NULL;
}

spike_t *spike_list_add_end(spike_t *list, spike_t *spike)
{
	/* adds a spike to the end of a spike list */
	if (list == NULL) {
		printf("spike_list_add: invalid spike list\n");
	} else {
		while(list->next != NULL) {
			list = list->next;
		} 
			list->next = spike;
			spike->prev = list;
		return list;
	}
}

spike_t *spike_list_find(spike_t *list, spike_t *spike)
{
	
}

void spike_list_remove(spike_t *list, spike_t *spike)
{
	if (list != NULL) {
		while (!spikecmp(list, spike)){
			list = list->next;
		} 
			spike_t *prev = list->prev;
			spike_t *next = list->next;
			prev->next = next;
			next->prev = prev;
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

find_spikes_by_cluid(spike_list_t *list, int cluid)
{
	/* returns a spike_list that contains all spikes from given list with given cluid */
	
}


