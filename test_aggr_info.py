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

import sys
sys.path.append("<path_to_nmsdk_root>/lib/python/NetApp")
from NaServer import *


api = NaElement("aggr-get-iter")

xi = NaElement("desired-attributes")
api.child_add(xi)


xi1 = NaElement("aggr-attributes")
xi.child_add(xi1)


xi2 = NaElement("aggr-64bit-upgrade-attributes")
xi1.child_add(xi2)


xi3 = NaElement("aggr-check-attributes")
xi2.child_add(xi3)

#xi3.child_add_string("added-space","<added-space>")
#xi3.child_add_string("check-last-errno","<check-last-errno>")
#xi3.child_add_string("cookie","<cookie>")
#xi3.child_add_string("is-space-estimate-complete","<is-space-estimate-complete>")

xi4 = NaElement("aggr-start-attributes")
xi2.child_add(xi4)

#xi4.child_add_string("min-space-for-upgrade","<min-space-for-upgrade>")
#xi4.child_add_string("start-last-errno","<start-last-errno>")

xi5 = NaElement("aggr-status-attributes")
xi2.child_add(xi5)

#xi5.child_add_string("is-64-bit-upgrade-in-progress","<is-64-bit-upgrade-in-progress>")

xi6 = NaElement("aggr-fs-attributes")
xi1.child_add(xi6)

#xi6.child_add_string("block-type","<block-type>")
#xi6.child_add_string("fsid","<fsid>")
#xi6.child_add_string("type","<type>")

xi7 = NaElement("aggr-inode-attributes")
xi1.child_add(xi7)

#xi7.child_add_string("files-private-used","<files-private-used>")
#xi7.child_add_string("files-total","<files-total>")
#xi7.child_add_string("files-used","<files-used>")
#xi7.child_add_string("inodefile-private-capacity","<inodefile-private-capacity>")
#xi7.child_add_string("inodefile-public-capacity","<inodefile-public-capacity>")
#xi7.child_add_string("maxfiles-available","<maxfiles-available>")
#xi7.child_add_string("maxfiles-possible","<maxfiles-possible>")
#xi7.child_add_string("maxfiles-used","<maxfiles-used>")
#xi7.child_add_string("percent-inode-used-capacity","<percent-inode-used-capacity>")

xi8 = NaElement("aggr-ownership-attributes")
xi1.child_add(xi8)

#xi8.child_add_string("home-id","<home-id>")
#xi8.child_add_string("home-name","<home-name>")
#xi8.child_add_string("owner-id","<owner-id>")
#xi8.child_add_string("owner-name","<owner-name>")

xi9 = NaElement("aggr-performance-attributes")
xi1.child_add(xi9)

#xi9.child_add_string("free-space-realloc","<free-space-realloc>")
#xi9.child_add_string("max-write-alloc-blocks","<max-write-alloc-blocks>")

xi10 = NaElement("aggr-raid-attributes")
xi1.child_add(xi10)

#xi10.child_add_string("cache-raid-group-size","<cache-raid-group-size>")
#xi10.child_add_string("checksum-status","<checksum-status>")
#xi10.child_add_string("checksum-style","<checksum-style>")
#xi10.child_add_string("disk-count","<disk-count>")
#xi10.child_add_string("ha-policy","<ha-policy>")
#xi10.child_add_string("has-local-root","<has-local-root>")
#xi10.child_add_string("has-partner-root","<has-partner-root>")
#xi10.child_add_string("is-checksum-enabled","<is-checksum-enabled>")
#xi10.child_add_string("is-hybrid","<is-hybrid>")
#xi10.child_add_string("is-hybrid-enabled","<is-hybrid-enabled>")
#xi10.child_add_string("is-inconsistent","<is-inconsistent>")
#xi10.child_add_string("mirror-status","<mirror-status>")
#xi10.child_add_string("mount-state","<mount-state>")
#xi10.child_add_string("plex-count","<plex-count>")

xi11 = NaElement("plexes")
xi10.child_add(xi11)


xi12 = NaElement("plex-attributes")
xi11.child_add(xi12)

#xi12.child_add_string("is-online","<is-online>")
#xi12.child_add_string("is-resyncing","<is-resyncing>")
#xi12.child_add_string("plex-name","<plex-name>")
#xi12.child_add_string("plex-status","<plex-status>")
#xi12.child_add_string("pool","<pool>")

xi13 = NaElement("raidgroups")
xi12.child_add(xi13)


xi14 = NaElement("raidgroup-attributes")
xi13.child_add(xi14)

#xi14.child_add_string("checksum-style","<checksum-style>")
#xi14.child_add_string("is-cache-tier","<is-cache-tier>")
#xi14.child_add_string("is-recomputing-parity","<is-recomputing-parity>")
#xi14.child_add_string("is-reconstructing","<is-reconstructing>")
#xi14.child_add_string("raidgroup-name","<raidgroup-name>")
#xi14.child_add_string("recomputing-parity-percentage","<recomputing-parity-percentage>")
#xi14.child_add_string("reconstruction-percentage","<reconstruction-percentage>")
#xi12.child_add_string("resync-level","<resync-level>")
#xi12.child_add_string("resyncing-percentage","<resyncing-percentage>")
#xi10.child_add_string("raid-lost-write-state","<raid-lost-write-state>")
#xi10.child_add_string("raid-size","<raid-size>")
#xi10.child_add_string("raid-status","<raid-status>")
#xi10.child_add_string("raid-type","<raid-type>")
#xi10.child_add_string("state","<state>")

xi15 = NaElement("aggr-snaplock-attributes")
xi1.child_add(xi15)

#xi15.child_add_string("is-snaplock","<is-snaplock>")
#xi15.child_add_string("snaplock-type","<snaplock-type>")

xi16 = NaElement("aggr-snapmirror-attributes")
xi1.child_add(xi16)

#xi16.child_add_string("dp-snapmirror-destinations","<dp-snapmirror-destinations>")
#xi16.child_add_string("ls-snapmirror-destinations","<ls-snapmirror-destinations>")
#xi16.child_add_string("mv-snapmirror-destinations","<mv-snapmirror-destinations>")

xi17 = NaElement("aggr-snapshot-attributes")
xi1.child_add(xi17)

#xi17.child_add_string("files-total","<files-total>")
#xi17.child_add_string("files-used","<files-used>")
#xi17.child_add_string("is-snapshot-auto-create-enabled","<is-snapshot-auto-create-enabled>")
#xi17.child_add_string("is-snapshot-auto-delete-enabled","<is-snapshot-auto-delete-enabled>")
#xi17.child_add_string("maxfiles-available","<maxfiles-available>")
#xi17.child_add_string("maxfiles-possible","<maxfiles-possible>")
#xi17.child_add_string("maxfiles-used","<maxfiles-used>")
#xi17.child_add_string("percent-inode-used-capacity","<percent-inode-used-capacity>")
#xi17.child_add_string("percent-used-capacity","<percent-used-capacity>")
#xi17.child_add_string("size-available","<size-available>")
#xi17.child_add_string("size-total","<size-total>")
#xi17.child_add_string("size-used","<size-used>")
#xi17.child_add_string("snapshot-reserve-percent","<snapshot-reserve-percent>")

xi18 = NaElement("aggr-space-attributes")
xi1.child_add(xi18)

#xi18.child_add_string("aggregate-metadata","<aggregate-metadata>")
#xi18.child_add_string("hybrid-cache-size-total","<hybrid-cache-size-total>")
#xi18.child_add_string("percent-used-capacity","<percent-used-capacity>")
#xi18.child_add_string("size-available","<size-available>")
#xi18.child_add_string("size-total","<size-total>")
#xi18.child_add_string("size-used","<size-used>")
#xi18.child_add_string("total-reserved-space","<total-reserved-space>")
#xi18.child_add_string("used-including-snapshot-reserve","<used-including-snapshot-reserve>")
#xi18.child_add_string("volume-footprints","<volume-footprints>")

xi19 = NaElement("aggr-striping-attributes")
xi1.child_add(xi19)

xi19.child_add_string("member-count","<member-count>")

xi20 = NaElement("aggr-volume-count-attributes")
xi1.child_add(xi20)

#xi20.child_add_string("flexvol-count","<flexvol-count>")
#xi20.child_add_string("flexvol-count-collective","<flexvol-count-collective>")
#xi20.child_add_string("flexvol-count-not-online","<flexvol-count-not-online>")
#xi20.child_add_string("flexvol-count-quiesced","<flexvol-count-quiesced>")
#xi20.child_add_string("flexvol-count-striped","<flexvol-count-striped>")

xi21 = NaElement("aggr-wafliron-attributes")
xi1.child_add(xi21)

#xi21.child_add_string("last-start-errno","<last-start-errno>")
#xi21.child_add_string("last-start-error-info","<last-start-error-info>")
#xi21.child_add_string("scan-percentage","<scan-percentage>")
#xi21.child_add_string("state","<state>")
#xi21.child_add_string("summary-scan-percentage","<summary-scan-percentage>")
#xi1.child_add_string("aggregate-name","<aggregate-name>")
#xi1.child_add_string("aggregate-uuid","<aggregate-uuid>")

xi22 = NaElement("nodes")
xi1.child_add(xi22)

#xi22.child_add_string("node-name","<node-name>")
#xi1.child_add_string("striping-type","<striping-type>")
#api.child_add_string("max-records","200")

xi23 = NaElement("query")
api.child_add(xi23)


xi24 = NaElement("aggr-attributes")
xi23.child_add(xi24)


xi25 = NaElement("aggr-64bit-upgrade-attributes")
xi24.child_add(xi25)


xi26 = NaElement("aggr-check-attributes")
xi25.child_add(xi26)

#xi26.child_add_string("added-space","<added-space>")
#xi26.child_add_string("check-last-errno","<check-last-errno>")
#xi26.child_add_string("cookie","<cookie>")
#xi26.child_add_string("is-space-estimate-complete","<is-space-estimate-complete>")

xi27 = NaElement("aggr-start-attributes")
xi25.child_add(xi27)

#xi27.child_add_string("min-space-for-upgrade","<min-space-for-upgrade>")
#xi27.child_add_string("start-last-errno","<start-last-errno>")

xi28 = NaElement("aggr-status-attributes")
xi25.child_add(xi28)

#xi28.child_add_string("is-64-bit-upgrade-in-progress","<is-64-bit-upgrade-in-progress>")

xi29 = NaElement("aggr-fs-attributes")
xi24.child_add(xi29)

#xi29.child_add_string("block-type","<block-type>")
#xi29.child_add_string("fsid","<fsid>")
#xi29.child_add_string("type","<type>")

xi30 = NaElement("aggr-inode-attributes")
xi24.child_add(xi30)

#xi30.child_add_string("files-private-used","<files-private-used>")
#xi30.child_add_string("files-total","<files-total>")
#xi30.child_add_string("files-used","<files-used>")
#xi30.child_add_string("inodefile-private-capacity","<inodefile-private-capacity>")
#xi30.child_add_string("inodefile-public-capacity","<inodefile-public-capacity>")
#xi30.child_add_string("maxfiles-available","<maxfiles-available>")
#xi30.child_add_string("maxfiles-possible","<maxfiles-possible>")
#xi30.child_add_string("maxfiles-used","<maxfiles-used>")
#xi30.child_add_string("percent-inode-used-capacity","<percent-inode-used-capacity>")

xi31 = NaElement("aggr-ownership-attributes")
xi24.child_add(xi31)

#xi31.child_add_string("home-id","<home-id>")
#xi31.child_add_string("home-name","<home-name>")
#xi31.child_add_string("owner-id","<owner-id>")
#xi31.child_add_string("owner-name","<owner-name>")

xi32 = NaElement("aggr-performance-attributes")
xi24.child_add(xi32)

#xi32.child_add_string("free-space-realloc","<free-space-realloc>")
#xi32.child_add_string("max-write-alloc-blocks","<max-write-alloc-blocks>")

xi33 = NaElement("aggr-raid-attributes")
xi24.child_add(xi33)

#xi33.child_add_string("cache-raid-group-size","<cache-raid-group-size>")
#xi33.child_add_string("checksum-status","<checksum-status>")
#xi33.child_add_string("checksum-style","<checksum-style>")
#xi33.child_add_string("disk-count","<disk-count>")
#xi33.child_add_string("ha-policy","<ha-policy>")
#xi33.child_add_string("has-local-root","<has-local-root>")
#xi33.child_add_string("has-partner-root","<has-partner-root>")
#xi33.child_add_string("is-checksum-enabled","<is-checksum-enabled>")
#xi33.child_add_string("is-hybrid","<is-hybrid>")
#xi33.child_add_string("is-hybrid-enabled","<is-hybrid-enabled>")
#xi33.child_add_string("is-inconsistent","<is-inconsistent>")
#xi33.child_add_string("mirror-status","<mirror-status>")
#xi33.child_add_string("mount-state","<mount-state>")
#xi33.child_add_string("plex-count","<plex-count>")

xi34 = NaElement("plexes")
xi33.child_add(xi34)


xi35 = NaElement("plex-attributes")
xi34.child_add(xi35)

#xi35.child_add_string("is-online","<is-online>")
#xi35.child_add_string("is-resyncing","<is-resyncing>")
#xi35.child_add_string("plex-name","<plex-name>")
#xi35.child_add_string("plex-status","<plex-status>")
#xi35.child_add_string("pool","<pool>")

xi36 = NaElement("raidgroups")
xi35.child_add(xi36)


xi37 = NaElement("raidgroup-attributes")
xi36.child_add(xi37)

#xi37.child_add_string("checksum-style","<checksum-style>")
#xi37.child_add_string("is-cache-tier","<is-cache-tier>")
#xi37.child_add_string("is-recomputing-parity","<is-recomputing-parity>")
#xi37.child_add_string("is-reconstructing","<is-reconstructing>")
#xi37.child_add_string("raidgroup-name","<raidgroup-name>")
#xi37.child_add_string("recomputing-parity-percentage","<recomputing-parity-percentage>")
#xi37.child_add_string("reconstruction-percentage","<reconstruction-percentage>")
#xi35.child_add_string("resync-level","<resync-level>")
#xi35.child_add_string("resyncing-percentage","<resyncing-percentage>")
#xi33.child_add_string("raid-lost-write-state","<raid-lost-write-state>")
#xi33.child_add_string("raid-size","<raid-size>")
#xi33.child_add_string("raid-status","<raid-status>")
#xi33.child_add_string("raid-type","<raid-type>")
#xi33.child_add_string("state","<state>")

xi38 = NaElement("aggr-snaplock-attributes")
xi24.child_add(xi38)

#xi38.child_add_string("is-snaplock","<is-snaplock>")
#xi38.child_add_string("snaplock-type","<snaplock-type>")

xi39 = NaElement("aggr-snapmirror-attributes")
xi24.child_add(xi39)

#xi39.child_add_string("dp-snapmirror-destinations","<dp-snapmirror-destinations>")
#xi39.child_add_string("ls-snapmirror-destinations","<ls-snapmirror-destinations>")
#xi39.child_add_string("mv-snapmirror-destinations","<mv-snapmirror-destinations>")

xi40 = NaElement("aggr-snapshot-attributes")
xi24.child_add(xi40)

#xi40.child_add_string("files-total","<files-total>")
#xi40.child_add_string("files-used","<files-used>")
#xi40.child_add_string("is-snapshot-auto-create-enabled","<is-snapshot-auto-create-enabled>")
#xi40.child_add_string("is-snapshot-auto-delete-enabled","<is-snapshot-auto-delete-enabled>")
#xi40.child_add_string("maxfiles-available","<maxfiles-available>")
#xi40.child_add_string("maxfiles-possible","<maxfiles-possible>")
#xi40.child_add_string("maxfiles-used","<maxfiles-used>")
#xi40.child_add_string("percent-inode-used-capacity","<percent-inode-used-capacity>")
#xi40.child_add_string("percent-used-capacity","<percent-used-capacity>")
#xi40.child_add_string("size-available","<size-available>")
#xi40.child_add_string("size-total","<size-total>")
#xi40.child_add_string("size-used","<size-used>")
#xi40.child_add_string("snapshot-reserve-percent","<snapshot-reserve-percent>")

xi41 = NaElement("aggr-space-attributes")
xi24.child_add(xi41)

#xi41.child_add_string("aggregate-metadata","<aggregate-metadata>")
#xi41.child_add_string("hybrid-cache-size-total","<hybrid-cache-size-total>")
#xi41.child_add_string("percent-used-capacity","<percent-used-capacity>")
#xi41.child_add_string("size-available","<size-available>")
#xi41.child_add_string("size-total","<size-total>")
#xi41.child_add_string("size-used","<size-used>")
#xi41.child_add_string("total-reserved-space","<total-reserved-space>")
#xi41.child_add_string("used-including-snapshot-reserve","<used-including-snapshot-reserve>")
#xi41.child_add_string("volume-footprints","<volume-footprints>")

xi42 = NaElement("aggr-striping-attributes")
xi24.child_add(xi42)

xi42.child_add_string("member-count","<member-count>")

xi43 = NaElement("aggr-volume-count-attributes")
xi24.child_add(xi43)

#xi43.child_add_string("flexvol-count","<flexvol-count>")
#xi43.child_add_string("flexvol-count-collective","<flexvol-count-collective>")
#xi43.child_add_string("flexvol-count-not-online","<flexvol-count-not-online>")
#xi43.child_add_string("flexvol-count-quiesced","<flexvol-count-quiesced>")
#xi43.child_add_string("flexvol-count-striped","<flexvol-count-striped>")

xi44 = NaElement("aggr-wafliron-attributes")
xi24.child_add(xi44)

#xi44.child_add_string("last-start-errno","<last-start-errno>")
#xi44.child_add_string("last-start-error-info","<last-start-error-info>")
#xi44.child_add_string("scan-percentage","<scan-percentage>")
#xi44.child_add_string("state","<state>")
#xi44.child_add_string("summary-scan-percentage","<summary-scan-percentage>")
#xi24.child_add_string("aggregate-name","<aggregate-name>")
#xi24.child_add_string("aggregate-uuid","<aggregate-uuid>")

xi45 = NaElement("nodes")
xi24.child_add(xi45)

#xi45.child_add_string("node-name","brisvegas-01")
#xi24.child_add_string("striping-type","<striping-type>")
#api.child_add_string("tag","<tag>")

#print api.sprintf()

xo = cdot_api_obj.s.invoke_elem(api)
cs = statsd.StatsClient('localhost',8125)

if (xo.results_status() == "failed") :
    print ("Error:\n")
    print (xo.sprintf())
    sys.exit (1)
else:
    for aggr in xmltodict.parse(xo.sprintf())['results']['attributes-list']['aggr-attributes']:
	aggr_space = aggr['aggr-space-attributes']
	aggr_name = aggr['aggregate-name']
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

