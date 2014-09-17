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
from pyZapi import pyZapi
from Daemon import Daemon
from cdot_api_pull import MyDaemon

cdot_api_obj = pyZapi('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
#cdot_api_obj = CdotPerf('ngslabc82', '10.128.113.63','admin','Netapp01', "1.21")
cs = statsd.StatsClient('localhost',8125)

aggrs = cdot_api_obj.aggr_get_iter()

for aggr in aggrs['results']['attributes-list']['aggr-attributes']:
    aggr_space      = aggr['aggr-space-attributes']
    aggr_name       = aggr['aggregate-name']
    aggr_owner_name = aggr['aggr-ownership-attributes']['owner-name']
    for item in aggr_space.keys():
	aggr_aggregate_metadata              = aggr_space['aggregate-metadata']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'aggregate-metadata'), float(aggr_aggregate_metadata))
	aggr_hybrid_cache_size_total         = aggr_space['hybrid-cache-size-total']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'hybrid-cache-size-total'), float(aggr_hybrid_cache_size_total))
	aggr_percent_used_capacity           = aggr_space['percent-used-capacity']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'percent-used-capacity'), float(aggr_percent_used_capacity))
	aggr_size_available                  = aggr_space['size-available']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'size-available'), float(aggr_size_available))
	aggr_size_total                      = aggr_space['size-total']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'size-total'), float(aggr_size_total))
	aggr_size_used                       = aggr_space['size-used']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'size-used'), float(aggr_size_used))
	aggr_total_reserved_space            = aggr_space['total-reserved-space']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'total-reserved-space'), float(aggr_total_reserved_space))
	aggr_used_including_snapshot_reserve = aggr_space['used-including-snapshot-reserve']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'used-including-snapshot-reserve'), float(aggr_used_including_snapshot_reserve))
	aggr_volume_footprints               = aggr_space['volume-footprints']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, aggr_owner_name, aggr_name, 'volume-footprints'), float(aggr_volume_footprints))
