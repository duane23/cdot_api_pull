#!/usr/bin/env python
# coding: utf-8

import argparse
import os
import sys
import string
import time
import atexit
import logging
import signal

sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
sys.path.append("/home/duane/cdot_api_pull")
from NaServer import *
import xmltodict
import statsd
from CdotPerf import CdotPerf

from Daemon import Daemon

class MyDaemon(Daemon):

    ## TODO - Instrument this code
    ##
    ##  Add timing points to this code
    ##   - Before and after API calls. 
    ##   - Also try and record number of metrics sent to grpahite

    """
    processor|processor0|brisvegas-01:kernel:processor0|domain_busy|Array of processor time in percentage spent in various domains|diag||processor_elapsed_time||idle,kahuna,storage,exempt,raid,raid_exempt,target,dnscache,cifs,wafl_exempt,wafl_xcleaner,sm_exempt,cluster,protocol,nwk_exclusive,nwk_exempt,nwk_legacy,hostOS,ssan_exempt|percent||array|percent
    processor|processor1|brisvegas-01:kernel:processor1|domain_busy|Array of processor time in percentage spent in various domains|diag||processor_elapsed_time||idle,kahuna,storage,exempt,raid,raid_exempt,target,dnscache,cifs,wafl_exempt,wafl_xcleaner,sm_exempt,cluster,protocol,nwk_exclusive,nwk_exempt,nwk_legacy,hostOS,ssan_exempt|percent||array|percent
    processor|processor2|brisvegas-01:kernel:processor2|domain_busy|Array of processor time in percentage spent in various domains|diag||processor_elapsed_time||idle,kahuna,storage,exempt,raid,raid_exempt,target,dnscache,cifs,wafl_exempt,wafl_xcleaner,sm_exempt,cluster,protocol,nwk_exclusive,nwk_exempt,nwk_legacy,hostOS,ssan_exempt|percent||array|percent
    processor|processor3|brisvegas-01:kernel:processor3|domain_busy|Array of processor time in percentage spent in various domains|diag||processor_elapsed_time||idle,kahuna,storage,exempt,raid,raid_exempt,target,dnscache,cifs,wafl_exempt,wafl_xcleaner,sm_exempt,cluster,protocol,nwk_exclusive,nwk_exempt,nwk_legacy,hostOS,ssan_exempt|percent||array|percent

    #>>> print j.get_counters_by_uuid('brisvegas-01:kernel:processor0','processor')
    {
     u'instance_uuid'         : u'brisvegas-01:kernel:processor0',
     u'sk_switches'           : u'3778533186',
     u'node_uuid'             : u'3b686de5-bef4-11e2-9018-d13886323cbe',
      'timestamp'             : u'1410744971',
     u'process_name'          : None,
     u'domain_busy'           : u'3780667529877,17683496612,6420263317,114178115781,2176445056,22605800472,13381459,798,457659,13839395007,1063674698,117297187,324,1237590223,8612971078,23202170840,7266309575,212719775716,10773833',
     u'instance_name'         : u'processor0',
      'uuid'                  : u'brisvegas-01:kernel:processor0',
      'name'                  : u'processor0',
     u'processor_busy'        : u'461596150749',
     u'node_name'             : u'brisvegas-01',
     u'processor_elapsed_time': u'4242263680626',
     u'hard_switches'         : u'915768253'
    }

    processor:node|brisvegas-01|3b686de5-bef4-11e2-9018-d13886323cbe|domain_busy|Array of processor time in percentage spent in various domains|diag||processor_elapsed_time||idle,kahuna,storage,exempt,raid,raid_exempt,target,dnscache,cifs,wafl_exempt,wafl_xcleaner,sm_exempt,cluster,protocol,nwk_exclusive,nwk_exempt,nwk_legacy,hostOS,ssan_exempt|percent||array|percent

    #>>> print j.get_counters_by_uuid('3b686de5-bef4-11e2-9018-d13886323cbe','processor:node')
    {
     u'instance_uuid'         : u'3b686de5-bef4-11e2-9018-d13886323cbe',
     u'sk_switches'           : u'10111551525',
      'timestamp'             : u'1410745504',
     u'domain_busy'           : u'15320395468179,68507628068,56916037163,351980330102,7379812795,192243111605,77939641,852,1624756,76351228741,4516588547,439078082,580,4339912961,27265831707,84145293040,31294278317,696206360151,68120605',
     u'instance_name'         : u'brisvegas-01',
      'voluuid'               : u'3b686de5-bef4-11e2-9018-d13886323cbe',
      'volname'               : u'brisvegas-01',
     u'processor_busy'        : u'1650792621702',
     u'processor_elapsed_time': u'16971188089881',
     u'hard_switches'         : u'9991143890'
    }
    """
    def get_cpu_counters(self, old_data, counter_req_list=None):
	pass
	## Accepts:
	##  - old_data (dict of old counter values)
	##  - counter_req_list
	## Returns:
	##  - dict of new counter values
	## 
	## Actions:
	##   Collect new dict of new counter values
	##     (1) First get list of name/uuid for instances of processor & processor:node
	##     (2) For each uuid cal get_counters by uuid
	##     (3) Use new and old dicts of ctrs to cal cpu stats and %'ages
	##     (4) Log stats to statsd
	## Return dict of new counter values
	##
	## Calling function maintains track of new & old stats, accepting new ones as retval before 
	## doing sleep, nuking old stats, resubmitting new as old when calling this sub again.
	##
	## First get details for object processor:node
	object_name = "processor:node"
	api = NaElement("perf-object-instance-list-info-iter")
	api.child_add_string("max-records",4294967295)
	api.child_add_string("objectname",object_name)
	xo = self.cdot_api_obj.s.invoke_elem(api)
	for res in xmltodict.parse(xo.sprintf())['results']['attributes-list']['instance-info']:
	    instance_uuid = res['uuid']
	    ret = self.cdot_api_obj.get_counters_by_uuid(instance_uuid, object_name)
	    for k in ret.keys():
		print k, ret[k]
	    print
	#print xo.sprintf()
	## Then get details for object processor

	return {}

    def run(self):
	self.cdot_api_obj = CdotPerf('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
	print self.get_cpu_counters({})
	## Connect to statsd
	cs = statsd.StatsClient('localhost',8125)
	## old / new are the lists of volumes as returned by get_volumes()
	old = []
	new = []
	## new_data / old data are the dicts of data
	new_data = {}
	new_data['timestamps'] = {}
	old_data = {}
	while True:
	    ## Iterate over existing volumes for given set of counters
	    new = self.cdot_api_obj.get_volumes()
	    if (len(old) != 0):
		old_data = new_data
		new_data = {}
		new_data['timestamps'] = {}
		for v in new:
		    try:
			v_cn  = v['cluster-name']
			v_svm = v['owning-vserver-name']
			v_vol = v['name']
			targ_counters = self.cdot_api_obj.targ_vol_counters
			c = self.cdot_api_obj.get_counters_by_uuid(v['instance-uuid'], "volume", targ_counters)
			c_ts = c['timestamp']
			for res in c.keys():
			    if ((res != 'timestamp') and (res != 'voluuid')):
				metric_string = string.join((self.cdot_api_obj.CLUSTER_NAME, v_svm, v_vol, res), '.')
				new_data[metric_string] = c[res]
				new_data['timestamps'][metric_string] = c_ts
		    except KeyError:
			self.cdot_api_obj.tellme("caught error for vol %s" % v_vol)
			continue
		## This loads the vol counter info into cdot_api_obj.vol_ctr_info
		self.cdot_api_obj.load_vol_counters()
		if (old_data['timestamps'] != {}):
		    for metric in new_data.keys():
			try:
			    try:
				self.cdot_api_obj.tellme("Processing metric %s" % metric)
				m_fields  = string.split(metric, '.')
				m_cluster = m_fields[0]
				m_svm     = m_fields[1]
				m_vol     = m_fields[2]
				m_ctr     = m_fields[3]
				m_ctr_info = self.cdot_api_obj.vol_ctr_info[m_cluster][m_svm][m_vol][m_ctr]
				m_base_counter = m_ctr_info['base-counter']  # if this exists we need to process counter more carefully
				m_properties   = m_ctr_info['properties']    # raw, rate, average, delta, percentage
				m_units        = m_ctr_info['unit']          # seconds, microseconds, bytes, etc
				m_type         = m_ctr_info['type']          # array or blank
			    except IndexError:
				self.cdot_api_obj.tellme("hit IndexError for metric: %s" % metric)
			    ## Is this a valid counter?
			    if ((metric == 'timestamps') or (string.split(metric, '.')[-1] == 'volname') or (string.split(metric, '.')[-1] == 'voluuid')):
				self.cdot_api_obj.tellme("hit timestamps, volname or voluuid for metric: %s" % metric)
				pass
			    ## If its a valid counter, does it need to be calculated as an average ?
			    elif ((m_properties == 'average') or (m_properties == 'percentage')):
				## Need to calculate average using metric and base-counter.
				# Step 1 is to get difference between new and old values of metric
				metric_delta = long((new_data[metric])) - long((old_data[metric]))
				self.cdot_api_obj.tellme("metric_delta = %s - %s = %s" % (long(new_data[metric]), long(old_data[metric]), metric_delta))
				# Next create metric string for base counter
				base_counter_lst = string.split(metric, '.')[:-1]
				base_counter_lst.append(m_base_counter)
				base_counter = string.join(base_counter_lst, '.')
				# Now get difference between base counter (new ) and base counter (old)
				metric_base_delta = long((new_data[base_counter])) - long((old_data[base_counter]))
				# Now divide counter value by base counter value and we have our actual metric
				# percentage gets multiplied by 100, average is left alone
				if (m_properties == 'percentage'):
				    try:
					metric_rate = 100 * (metric_delta / metric_base_delta)
				    except ZeroDivisionError:
					self.cdot_api_obj.tellme("hit div by 0")
					metric_rate = 0
				else:
				    try:
					metric_rate = metric_delta / metric_base_delta
				    except ZeroDivisionError:
					self.cdot_api_obj.tellme("hit div by 0")
					metric_rate = 0
				self.cdot_api_obj.tellme(">>>metric_rate = %s / %s" % (metric_delta, metric_base_delta))
				self.cdot_api_obj.tellme(">>>%s -> %s" % (metric, metric_rate))
				cs.gauge(metric, metric_rate)
				self.cdot_api_obj.tellme("Submitted Gauge for %s, %s, m_properties = %s" % (metric, metric_rate, m_properties))
			    elif (m_properties == 'raw'):
				## Raw metrics are simply logged as the most recent value, no maths required.
				metric_stored = long(new_data[metric])
				cs.gauge(metric, metric_stored)
			    elif (m_properties == 'delta'):
				## Deltas are generally used for arrays - we don't handle these at this point.
				pass
			    elif (m_properties == 'rate'):
				## Rate is the most common case - different between two values, divided by time elapsed.
				# Calc elapsed time between new and old
				old_ts = long((old_data['timestamps'][metric]).encode('ascii','ignore'))
				new_ts = long((new_data['timestamps'][metric]).encode('ascii','ignore'))
				ts_delta = new_ts - old_ts
				# Calc counter change between new and old
				metric_delta = long((new_data[metric])) - long((old_data[metric]))
				# Divide change by elapapsed time (secs)
				metric_rate = metric_delta / ts_delta
				# Log resulting value
				cs.gauge(metric, metric_rate)
				self.cdot_api_obj.tellme("Submitted Gauge for %s, %s, m_properties = %s" % (metric, metric_rate, m_properties))
			except KeyError:
			    self.cdot_api_obj.tellme("cdot_api_pull.py:run(): Caught Exception processing metric %s" % metric)
		## New stats set to old, old ones nuked
		old = new
		new = []
	    else:
		## Should only be executed on first run
		old = new
		new = []
	    time.sleep(30)

def main():
    """
    The application entry point
    """
    parser = argparse.ArgumentParser(description='Daemon runner', epilog="That's all folks")
    parser.add_argument('operation',
			metavar='OPERATION',
			type=str,
			help='Operation with daemon. Accepts any of these values: start, stop, restart, status',
			choices=['start', 'stop', 'restart', 'status'])
    args = parser.parse_args()
    operation = args.operation
    # Daemon
    daemon = MyDaemon('/var/run/cdot_api_pull.pid')
    if operation == 'start':
        print("Starting daemon")
        daemon.start()
        pid = daemon.get_pid()
        if not pid:
            print("Unable run daemon")
        else:
            print("Daemon is running [PID=%d]" % pid)
    elif operation == 'stop':
        print("Stoping daemon")
        daemon.stop()
    elif operation == 'restart':
        print("Restarting daemon")
        daemon.restart()
    elif operation == 'status':
        print("Viewing daemon status")
        pid = daemon.get_pid()
        if not pid:
            print("Daemon isn't running ;)")
        else:
            print("Daemon is running [PID=%d]" % pid)
    sys.exit(0)

if __name__ == '__main__':
    main()
