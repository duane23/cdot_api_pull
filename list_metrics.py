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
    cdot_vol_obj = CdotPerf('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
    counter_info = {}
    for t in cdot_vol_obj.get_objects():
	print "Called get_objects, processing %s" % t
	counter_info[t] = {}
        for line in cdot_vol_obj.get_object_counter_info(t):
	    #print "Called get_object_counter_info for %s" % line
	    counter_info[t][string.split(line,'|')[0]] = line
    for v in cdot_vol_obj.get_volumes():
	try:
	    c = cdot_vol_obj.get_counters(v['instance-uuid'],u"cifs_read_ops,cifs_write_ops")
	    print c
	    ctr_names = c.keys()
	    ctr_names.sort()
	    for ctr in ctr_names:
		print "%s|%s|%s|%s" % ("brisvegas", v['owning-vserver-name'], v['name'], counter_info['volume'][ctr])
	except KeyError:
	    print "hit keyerror processing %s" % v['name']
	    continue

if __name__ == "__main__":
    main()
    sys.exit(0)
