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

    def run(self):
	self.cdot_api_obj = CdotPerf('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
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
		## Compare old and new here
		## TODO
		##  - This needs to be extended to automatically handle average counters, base counters and percent counters.
		##  - targ_counters should be a dict which contains metric, metric-type and base-counter as required
		## 
		##  Take old and new dicts.
		##   - for each metric in new
		##       - if its of type average or percentage
		##            - make sure values for new and old are present
		##            - make sure base-counter values for new and old are present
		## 
		## 
		## 
		## 
		## 
		print self.cdot_api_obj.load_vol_counters()
		if (old_data['timestamps'] != {}):
		    for metric in new_data.keys():
			try:
			    if ((metric == 'timestamps') or (string.split(metric, '.')[-1] == 'volname')):
				pass
			    elif (string.split(metric, '.')[-1] == 'avg_latency'):
				metric_delta = long((new_data[metric])) - long((old_data[metric]))
				self.cdot_api_obj.tellme("metric_delta = %s - %s = %s" % (long(new_data[metric]), long(old_data[metric]), metric_delta))
				base_counter_lst = string.split(metric, '.')[:-1]
				base_counter_lst.append('total_ops')
				base_counter = string.join(base_counter_lst, '.')
				try:
				    metric_base_delta = long((new_data[base_counter])) - long((old_data[base_counter]))
				    self.cdot_api_obj.tellme("metric_base_delta = %s - %s = %s" % (long(new_data[base_counter]), long(old_data[base_counter]), metric_base_delta))
				except KeyError:
				    metric_base_delta = 0
				    self.cdot_api_obj.tellme("Hit KeyError - setting metric_base_delta = 0")
				try:
				    metric_rate = metric_delta / metric_base_delta
				except ZeroDivisionError:
				    self.cdot_api_obj.tellme("hit div by 0")
				    metric_rate = 0
				self.cdot_api_obj.tellme("metric_rate = %s / %s" % (metric_delta, metric_base_delta))
				self.cdot_api_obj.tellme(">>>%s -> %s" % (metric, metric_rate))
				cs.gauge(metric, metric_rate)
				self.cdot_api_obj.tellme("Submitted Gauge for %s, %s" % (metric, metric_rate))
			    else:
				## For each metric in new_data & old_data;
				##  - Calculate elapsed time
				##  - Work out diff between values, divide by secs
				##TODO:
				old_ts = long((old_data['timestamps'][metric]).encode('ascii','ignore'))
				new_ts = long((new_data['timestamps'][metric]).encode('ascii','ignore'))
				self.cdot_api_obj.tellme("Doing comparison for %s" % metric)
				#self.cdot_api_obj.tellme("old_ts:: %s" % old_ts)
				#self.cdot_api_obj.tellme("new_ts:: %s" % new_ts)
				#self.cdot_api_obj.tellme("old: %s -> value: %s" % (metric, old_data[metric]))
				#self.cdot_api_obj.tellme("new: %s -> value: %s" % (metric, new_data[metric]))
				ts_delta = new_ts - old_ts
				metric_delta = long((new_data[metric])) - long((old_data[metric]))
				metric_rate = metric_delta / ts_delta
				#self.cdot_api_obj.tellme("ts_delta: %s, metric_delta %s" % (ts_delta, metric_delta))
				#self.cdot_api_obj.tellme("metric_rate: %s" % metric_rate)
				cs.gauge(metric, metric_rate)
				self.cdot_api_obj.tellme("Submitted Gauge for %s, %s" % (metric, metric_rate))
			except KeyError:
			    self.cdot_api_obj.tellme("cdot_api_pull.py:run(): Caught Exception processing metric %s" % metric)
		## New stats set to old, old ones nuked
		old = new
		new = []
	    else:
		## Should only be executed on first run
		old = new
		new = []
	    time.sleep(1)

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
