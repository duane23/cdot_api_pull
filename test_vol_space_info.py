#!/usr/bin/python
##
## $Id$
##
## Todo:
##  - 
##
import sys
import string
sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
from NaServer import *
import xmltodict
import statsd
from pyZapi import pyZapi
from Daemon import Daemon
from cdot_api_pull import MyDaemon

cdot_api_obj = pyZapi('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
#cdot_api_obj = pyZapi('ngslabc82', '10.128.113.63','admin','Netapp01', "1.21")

cs = statsd.StatsClient('localhost',8125)

volumes = cdot_api_obj.vol_get_iter()
for vol in volumes['results']['attributes-list']['volume-attributes']:
    id_attr    = vol['volume-id-attributes']
    space_attr = vol['volume-space-attributes']
    try:
	v_name                                = id_attr['name']
	v_inst_uuid                           = id_attr['instance-uuid']
	v_ownr_vserver                        = id_attr['owning-vserver-name']
	v_aggr_name                           = id_attr['containing-aggregate-name']
	v_aggr_uuid                           = id_attr['containing-aggregate-uuid']
	v_fs_size                             = space_attr['filesystem-size']
	v_overwrite_reserve                   = space_attr['overwrite-reserve']
	v_overwrite_reserve_required          = space_attr['overwrite-reserve-required']
	v_overwrite_reserve_used              = space_attr['overwrite-reserve-used']
	v_overwrite_reserve_used_actual       = space_attr['overwrite-reserve-used-actual']
	v_percentage_size_used                = space_attr['percentage-size-used']
	v_percentage_snapshot_reserve         = space_attr['percentage-snapshot-reserve']
	v_percentage_snapshot_reserve_used    = space_attr['percentage-snapshot-reserve-used']
	v_size                                = space_attr['size']
	v_size_available                      = space_attr['size-available']
	v_size_available_for_snapshots        = space_attr['size-available-for-snapshots']
	v_size_total                          = space_attr['size-total']
	v_size_used                           = space_attr['size-used']
	v_size_used_by_snapshots              = space_attr['size-used-by-snapshots']
	v_snapshot_reserve_size               = space_attr['snapshot-reserve-size']
	v_space_full_threshold_percent        = space_attr['space-full-threshold-percent']
	v_space_nearly_full_threshold_percent = space_attr['space-nearly-full-threshold-percent']

	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'filesystem-size'), float(v_fs_size))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'overwrite-reserve'), float(v_overwrite_reserve))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'overwrite-reserve-required'), float(v_overwrite_reserve_required))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'overwrite-reserve-used'), float(v_overwrite_reserve_used))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'overwrite-reserve-used-actual'), float(v_overwrite_reserve_used_actual))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'percentage-size-used'), float(v_percentage_size_used))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'percentage-snapshot-reserve'), float(v_percentage_snapshot_reserve))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'percentage-snapshot-reserve-used'), float(v_percentage_snapshot_reserve_used))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'size'), float(v_size))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'size-available'), float(v_size_available))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'size-available-for-snapshots'), float(v_size_available_for_snapshots))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'size-total'), float(v_size_total))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'size-used'), float(v_size_used))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'size-used-by-snapshots'), float(v_size_used_by_snapshots))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'snapshot-reserve-size'), float(v_snapshot_reserve_size))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'space-full-threshold-percent'), float(v_space_full_threshold_percent))
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'space-nearly-full-threshold-percent'), float(v_space_nearly_full_threshold_percent))
    except KeyError:
	v_size                                = space_attr['size']
	cs.gauge("%s.%s.%s.%s" % (cdot_api_obj.CLUSTER_NAME, v_ownr_vserver, v_name, 'size'), float(v_size))
