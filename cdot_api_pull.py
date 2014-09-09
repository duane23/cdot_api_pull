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

    def get_vol_counters(self, vol_inst_uuid, counter_list):
	## Takes volume instance-uuid & list of counters to return.
	## List of counters is string containing counter-names separated by commas
	## Returns dict as follows:
	## 
	## { timestamp : <timestamp>
	##   counters  : { counter-name : <counter-value>,
	##                 counter-name : <counter-value>
	##             }
	## }

	c = self.cdot_api_obj.get_counters_by_uuid(vol_inst_uuid, "volume", counter_list)
	r = {}
	r['timestamp'] = c['timestamp']
	c['counters']  = {}

	## TODO

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
			##
			## TODO - Need to fix this;
			##
			##  - metric_string defines where the stats go in the graphite tree
			##  - need to standardise on how metrics are recorded
			##
			v_cn  = v['cluster-name']
			v_svm = v['owning-vserver-name']
			v_vol = v['name']
			c = self.cdot_api_obj.get_counters_by_uuid(v['instance-uuid'], "volume", "read_ops,write_ops,total_ops,nfs_write_latency,nfs_read_latency,nfs_other_latency")
			c_ts = c['timestamp']

			for res in c.keys():
			    if ((res != 'timestamp') and (res != 'voluuid')):
				metric_string = string.join((self.cdot_api_obj.CLUSTER_NAME, v_svm, v_vol, res), '.')
				new_data[metric_string] = c[res]
				new_data['timestamps'][metric_string] = c_ts
		    except KeyError:
			print "caught error for vol %s" % v_vol
			continue
		## Compare old and new here
		if (old_data['timestamps'] != {}):
		    for metric in new_data.keys():
			if ((metric == 'timestamps') or (string.split(metric, '.')[-1] == 'volname')):
			    pass
			else:
			    ##
			    ## For each metric in new_data & old_data;
			    ##  - Calculate elapsed time
			    ##  - Work out diff between values, divide by secs
			    ##
			    print "Doing comparison for %s" % metric
			    old_ts = long((old_data['timestamps'][metric]).encode('ascii','ignore'))
			    new_ts = long((new_data['timestamps'][metric]).encode('ascii','ignore'))
			    print "old_ts:: %s" % old_ts
			    print "new_ts:: %s" % new_ts
			    print "old: %s -> value: %s" % (metric, old_data[metric])
			    print "new: %s -> value: %s" % (metric, new_data[metric])
			    ts_delta = new_ts - old_ts
			    metric_delta = long((new_data[metric])) - long((old_data[metric]))
			    print  "ts_delta: %s, metric_delta %s" % (ts_delta, metric_delta)
			    metric_rate = metric_delta / ts_delta
			    print  "metric_rate: %s" % metric_rate

			    cs.gauge(metric, metric_rate)

			    #old_ts = old_data['timestamp']
			    #old_ts = long(old_data[metric]['timestamp'].encode('ascii','ignore'))
#			    old_read_ops = long(old_data[metric]['read_ops'].encode('ascii','ignore'))
#			    old_write_ops = long(old_data[metric]['write_ops'].encode('ascii','ignore'))
#			    new_ts = long(new_data[metric]['timestamp'].encode('ascii','ignore'))
#			    new_read_ops = long(new_data[metric]['read_ops'].encode('ascii','ignore'))
#			    new_write_ops = long(new_data[metric]['write_ops'].encode('ascii','ignore'))
#			    elapsed_ts = new_ts - old_ts
#			    elapsed_reads = new_read_ops - old_read_ops
#			    elapsed_writes = new_write_ops - old_write_ops
#			    if (string.split(metric, '.')[-1] == "read_ops"):
#				metric2 = string.join((string.split(metric, '.')[0:-1]),'.') + ".read_iops"
#				cs.gauge(metric2, elapsed_reads/elapsed_ts)
#			    elif (string.split(metric, '.')[-1] == "write_ops"):
#				metric2 = string.join((string.split(metric, '.')[0:-1]),'.') + ".write_iops"
#				cs.gauge(metric2, elapsed_writes/elapsed_ts)

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
