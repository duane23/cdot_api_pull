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
#    counter_info = {}
#    objlist = cdot_api_obj.get_perf_objects()
#    for t in objlist:
#	counter_info[t] = {}
#        for line in cdot_api_obj.get_object_counter_info(t):
#	    counter_info[t][string.split(line,'|')[0]] = line
#	    cdot_api_obj.tellme("list_perf_metrics.py: %s, %s" % (t, line))
	    #print "list_perf_metrics.py: object: %s, metric: %s" % (t, line)

    ## Now that we have a list of objects (objlist) and a list of counters
    ## that are available for each type of object (counter_info)
    ## Now we need a list of instances of each object type (instances are the actual 
    ## elements on the cluster, ie vol0 or aggr01_01


    api = NaElement("perf-object-instance-list-info-iter")
    #
#    xi = NaElement("desired-attributes")
#    api.child_add(xi)
    #
    #
#    xi1 = NaElement("instance-info")
#    xi.child_add(xi1)
    #
#    xi1.child_add_string("name","<name>")
#    xi1.child_add_string("uuid","<uuid>")
    #api.child_add_string("filter-data","<filter-data>")
    api.child_add_string("max-records",4294967295)
    api.child_add_string("objectname","cluster_peer")
    #
#    xi2 = NaElement("query")
#    api.child_add(xi2)
    #
    #
#    xi3 = NaElement("instance-info")
#    xi2.child_add(xi3)
    #
#    xi3.child_add_string("name","<name>")
#    xi3.child_add_string("uuid","<uuid>")
#    api.child_add_string("tag","<tag>")

    xo = cdot_api_obj.s.invoke_elem(api)
    if (xo.results_status() == "failed") :
	print ("Error:\n")
	print (xo.sprintf())
	sys.exit (1)
    print ("Received:\n")
    print (xo.sprintf())





    sys.exit(0)
    for v in cdot_api_obj.get_volumes():
	try:
	    c = cdot_api_obj.get_counters_by_uuid(v['instance-uuid'], 'volume')
	    ctr_names = c.keys()
	    ctr_names.sort()
	    cdot_api_obj.tellme("list_vol_metrics.py: read_ops  for vol %s is %s" % (v['name'], counter_info['volume']['read_ops']))
	    cdot_api_obj.tellme("list_vol_metrics.py: write_ops for vol %s is %s" % (v['name'], counter_info['volume']['write_ops']))
	    for ctr in ctr_names:
		try:
		    cdot_api_obj.tellme("list_vol_metrics.py: Processing counter - %s" % (ctr))
		    if ((ctr != "timestamp") and (ctr != "volname")):
			print "%s|%s|%s|%s" % ("brisvegas", v['owning-vserver-name'], v['name'], counter_info['volume'][ctr])
		except:
		    cdot_api_obj.tellme("list_vol_metrics.py: Caught exception for ctr: %s, volume:: %s" % (ctr, v['name']))
	except KeyError:
	    cdot_api_obj.tellme("list_vol_metrics.py: Hit keyerror - ctr = %s, vol = %s" % (ctr, v['name']))
	    continue

if __name__ == "__main__":
    main()
    sys.exit(0)
