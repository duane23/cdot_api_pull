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

    counter_file = "/home/duane/cdot_api_pull/vol-perf-counters.txt"

    cdot_api_obj.load_vol_counters(counter_file)

    print cdot_api_obj.vol_ctr_info['brisvegas'].keys()

    #cdot_api_obj.tellme("list_vol_metrics.py: Hit keyerror - ctr = %s, vol = %s" % (ctr, v['name']))

if __name__ == "__main__":
    main()
    sys.exit(0)
