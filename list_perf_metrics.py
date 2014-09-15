#!/usr/bin/python
##
## $Id$
##
## Todo:
##  - 
##
import sys,string
sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
from NaServer import *
import xmltodict
import statsd
from CdotPerf import CdotPerf

def main():
    cdot_api_obj = CdotPerf('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
    counter_info = {}
    objlist = cdot_api_obj.get_perf_objects()
    for t in objlist:
	counter_info[t] = {}
        for line in cdot_api_obj.get_object_counter_info(t):
	    counter_info[t][string.split(line,'|')[0]] = line
	    cdot_api_obj.tellme("list_perf_metrics.py: %s, %s" % (t, line))
	    #print "list_perf_metrics.py: object: %s, metric: %s" % (t, line)
    ##
    ## Now that we have a list of objects (objlist) and a list of counters
    ## that are available for each type of object (counter_info)
    ## Now we need a list of instances of each object type (instances are the actual 
    ## elements on the cluster, ie vol0 or aggr01_01
    ##
    for t in objlist:
	if (t != 'iscsi_conn:session'):
	    print "### getting for obj: %s" % t
	    api = NaElement("perf-object-instance-list-info-iter")
	    api.child_add_string("max-records",4294967295)
	    api.child_add_string("objectname",t)
	    xo = cdot_api_obj.s.invoke_elem(api)
	    try:
		if (xo.results_status() == "failed"):
		    print "### lookup failed - no records found"
		else:
		    api_result = xmltodict.parse(xo.sprintf())
		    num_results = int(api_result['results']['num-records'])
		    if (num_results > 1):
			for instance in xmltodict.parse(xo.sprintf())['results']['attributes-list']['instance-info']:
			    if isinstance(instance, dict):
				for ctr in counter_info[t].keys():
				    print "%s|%s|%s|%s" % (t, instance['name'], instance['uuid'], counter_info[t][ctr])
			    else:
				print "### instance isn't dict: %s\n%s\n%s" % (instance, xo.sprintf(), xmltodict.parse(xo.sprintf()))
		    elif (num_results == 1):
			for ctr in counter_info[t].keys():
			    print "%s|%s|%s|%s" % (t, api_result['results']['attributes-list']['instance-info']['name'], api_result['results']['attributes-list']['instance-info']['uuid'], counter_info[t][ctr])
		    else:
			print "### no records - valid lookup but no results"
	    except:
		print "### caught general exception - %s\n%s" % (xmltodict.parse(xo.sprintf()), xo.sprintf())
	else:
	    print "### skipping %s - known issue parsing results" % t

if __name__ == "__main__":
    main()
    sys.exit(0)
