#!/usr/bin/python
##
## $Id: feed_statsd.py,v 1.2 2014/09/05 07:25:16 duane Exp duane $
##
## Todo:
##  - 
##
import sys,string

sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")

from NaServer import *
import xmltodict
import statsd
import time

from CdotPerf import CdotPerf

def main():
    cdot_vol_obj = CdotPerf('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")

    ## Connect to statsd
    cs = statsd.StatsClient('localhost',8125)
    old = []
    new = []
    new_data = {}
    old_data = {}
    while True:
	new = cdot_vol_obj.get_volumes()
	if (len(old) != 0):
	    old_data = new_data
	    new_data = {}
	    for v in new:
		try:
		    v_cn  = v['cluster-name']
		    v_svm = v['owning-vserver-name']
		    v_vol = v['name']
		    c = cdot_vol_obj.get_counters(v['instance-uuid'])
		    c_ts = c['timestamp']
		    c_read_ops  = c['read_ops']
		    c_write_ops = c['write_ops']
		    c_total_ops = c['total_ops']
		    metric_string =  "brisvegas.%s.%s.read_ops" % (v_svm, v_vol)
		    new_data[metric_string] = {}
		    new_data[metric_string]['timestamp'] = c_ts
		    new_data[metric_string]['read_ops']  = c_read_ops
		    new_data[metric_string]['write_ops'] = c_write_ops
		    metric_string =  "brisvegas.%s.%s.write_ops" % (v_svm, v_vol)
		    new_data[metric_string] = {}
		    new_data[metric_string]['timestamp'] = c_ts
		    new_data[metric_string]['read_ops']  = c_read_ops
		    new_data[metric_string]['write_ops'] = c_write_ops
		except KeyError:
		    print "caught error for vol %s" % v_vol
		    continue
	    ## Compare old and new here
	    if (old_data != {}):
		for metric in new_data.keys():
		    print "Doing comparison for %s" % metric
		    old_ts = long(old_data[metric]['timestamp'].encode('ascii','ignore'))
		    old_read_ops = long(old_data[metric]['read_ops'].encode('ascii','ignore'))
		    old_write_ops = long(old_data[metric]['write_ops'].encode('ascii','ignore'))
		    new_ts = long(new_data[metric]['timestamp'].encode('ascii','ignore'))
		    new_read_ops = long(new_data[metric]['read_ops'].encode('ascii','ignore'))
		    new_write_ops = long(new_data[metric]['write_ops'].encode('ascii','ignore'))
		    elapsed_ts = new_ts - old_ts
		    elapsed_reads = new_read_ops - old_read_ops
		    elapsed_writes = new_write_ops - old_write_ops
		    if (string.split(metric, '.')[-1] == "read_ops"):
			metric2 = string.join((string.split(metric, '.')[0:-1]),'.') + ".read_iops"
			cs.gauge(metric2, elapsed_reads/elapsed_ts)
		    elif (string.split(metric, '.')[-1] == "write_ops"):
			metric2 = string.join((string.split(metric, '.')[0:-1]),'.') + ".write_iops"
			cs.gauge(metric2, elapsed_writes/elapsed_ts)
	    ## New stats set to old, old ones nuked
	    old = new
	    new = []
	else:
	    ## Should only be executed on first run
	    old = new
	    new = []
	time.sleep(1)

if __name__ == "__main__":
    main()

    sys.exit(0)
