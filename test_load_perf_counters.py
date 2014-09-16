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
from Daemon import Daemon
from cdot_api_pull import MyDaemon

cdot_api_obj = CdotPerf('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")

cdot_api_obj.load_perf_counters()

cdot_api_obj.perf_ctr_info

objs = cdot_api_obj.perf_ctr_info
#objs.sort()

test23 = objs['processor']['brisvegas-01:kernel:processor0'].keys()

print test23


#for o in objs:
    #print cdot_api_obj.perf_ctr_info[o]
    #brisvegas-01:kernel:processor0','processor'
