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
#    for t in cdot_api_obj.get_perf_objects():
#	counter_info[t] = {}
#        for line in cdot_api_obj.get_object_counter_info(t):
#	    counter_info[t][string.split(line,'|')[0]] = line
    for a in cdot_api_obj.get_aggregates():
	try:
	    print string.join((a['cluster-name'],a['owner-name'],a['aggr-name'],a['aggr-uuid']),'|')
        except KeyError:
            continue

if __name__ == "__main__":
    main()
    sys.exit(0)
