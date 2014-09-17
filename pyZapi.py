#!/usr/bin/python
##
##
import sys,string
sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
from NaServer import *
import xmltodict
import statsd
import time
import os

class pyZapi:
    def __init__(self, cluster_name, cluster_ip, username, password, sdk_ver, server_type="FILER", transport_type="HTTPS", port="443", style="LOGIN"):
        major, minor = string.split(sdk_ver, '.')
        self.CLUSTER_NAME = cluster_name
        self.MAX_VOLUMES  = 20000
        self.s = NaServer(cluster_ip, major, minor)
        self.s.set_server_type(server_type)
        self.s.set_transport_type(transport_type)
        self.s.set_port(port)
        self.s.set_style(style)
        self.s.set_admin_user(username, password)
	self.sd = statsd.StatsClient('localhost',8125)
	try:
	    self.debug = open("/var/tmp/debugenabled")
	    self.debug.close()
	    self.debug = True
	    self.fp = open("/var/tmp/tellme.log", "a")
	except IOError:
	    self.debug = False
	self.targ_vol_counters = "avg_latency,cifs_other_latency,cifs_other_ops,cifs_read_data,cifs_read_latency,cifs_read_ops,cifs_write_data,cifs_write_latency,cifs_write_ops,fcp_other_latency,fcp_other_ops,fcp_read_data,fcp_read_latency,fcp_read_ops,fcp_write_data,fcp_write_latency,fcp_write_ops,flexcache_other_ops,flexcache_read_data,flexcache_read_ops,flexcache_receive_data,flexcache_send_data,flexcache_write_data,flexcache_write_ops,iscsi_other_latency,iscsi_other_ops,iscsi_read_data,iscsi_read_latency,iscsi_read_ops,iscsi_write_data,iscsi_write_latency,iscsi_write_ops,nfs_other_latency,nfs_other_ops,nfs_read_data,nfs_read_latency,nfs_read_ops,nfs_write_data,nfs_write_latency,nfs_write_ops,other_latency,other_ops,read_blocks,read_data,read_latency,read_ops,san_other_latency,san_other_ops,san_read_data,san_read_latency,san_read_ops,san_write_data,san_write_latency,san_write_ops,total_ops,write_blocks,write_data,write_latency,write_ops"


    def tellme(self, message):
	if (self.debug):
	    self.fp.write("%s\n" % message)

    def get_aggregates(self):
	"""
	    Get list of volumes from cluster
	"""
	api = NaElement("aggr-get-iter")
	api.child_add_string("max-records",self.MAX_VOLUMES)
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	f = xmltodict.parse(xo.sprintf())
	aggrs = f['results']['attributes-list']['aggr-attributes']
	aggr_list = []
	for aggr in aggrs:
	    for z in aggr.keys():
		try:
		    if (z == 'aggregate-name'):
			aggr_name = aggr[z]
		    elif (z == 'aggregate-uuid'):
			aggr_uuid = aggr[z]
		    elif (z == 'aggr-ownership-attributes'):
			aggr_ownr = aggr[z]['owner-name']
		except AttributeError:
		    pass
	    aggr_list.append({
			      'cluster-name':self.CLUSTER_NAME,
			      'aggr-name'   :aggr_name,
			      'aggr-uuid'   :aggr_uuid,
			      'owner-name'  :aggr_ownr
			     })
	return aggr_list

    def get_volumes(self):
	"""
	    Get list of volumes from cluster
	"""
	api = NaElement("volume-get-iter")
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	api.child_add_string("max-records",self.MAX_VOLUMES)
	xi1 = NaElement("volume-attributes")
	xi.child_add(xi1)
	xi41 = NaElement("volume-id-attributes")
	xi41.child_add_string("instance-uuid","<instance-uuid>")
	xi41.child_add_string("name","<name>")
	xi41.child_add_string("owning-vserver-name","<owning-vserver-name>")
	xi41.child_add_string("uuid","<uuid>")
	xi1.child_add(xi41)
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	f = xmltodict.parse(xo.sprintf())
	volumes = f['results']['attributes-list']['volume-attributes']
	vol_list = []
	for volume in volumes:
	    vol_list.append({'cluster-name':self.CLUSTER_NAME,
			     'owning-vserver-name':volume['volume-id-attributes']['owning-vserver-name'],
			     'name':volume['volume-id-attributes']['name'],
			     'instance-uuid':volume['volume-id-attributes']['instance-uuid']
			    })
	return vol_list


    def get_counters_by_name(self, instance_name, object_name, counter_filter_list=None):
	api = NaElement("perf-object-get-instances")
	xi2 = NaElement("instances")
	api.child_add(xi2)
	xi2.child_add_string("instance",instance_name)
	api.child_add_string("objectname",object_name)
	ctrs = {}
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    return ctrs
	try:
	    f = xmltodict.parse(xo.sprintf())
	except xml.parsers.expat.ExpatError:
	    print xo.sprintf()
	ctrs['timestamp'] = f['results']['timestamp']
	ctrs['name']   = f['results']['instances']['instance-data']['name']
	ctrs['uuid']   = f['results']['instances']['instance-data']['uuid']
	for ctr in f['results']['instances']['instance-data']['counters']['counter-data']:
	    ctrs[ctr['name']] = ctr['value']
	return ctrs

    def get_object_instance_list_info(self, object_name):
	api = NaElement("perf-object-instance-list-info-iter")
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	api.child_add_string("max-records",1000000)
	api.child_add_string("objectname",object_name)
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    print ("Error:\n")
	    print (xo.sprintf())
	    sys.exit (1)
	ctrs = {}
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    return ctrs
	try:
	    f = xmltodict.parse(xo.sprintf())
	except xml.parsers.expat.ExpatError:
	    pass

    def get_counters_by_uuid(self, instance_uuid, object_name, counter_filter_list=None):
	api = NaElement("perf-object-get-instances")
	xi = NaElement("counters")
	api.child_add(xi)
	xi.child_add_string("counter",counter_filter_list)
	xi3 = NaElement("instance-uuids")
	api.child_add(xi3)
	xi3.child_add_string("instance-uuid",instance_uuid)
	api.child_add_string("objectname",object_name)
	ctrs = {}
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    print xo.sprintf()
	    return ctrs
	try:
	    f = xmltodict.parse(xo.sprintf())
	except xml.parsers.expat.ExpatError:
	    print xo.sprintf()
	ctrs['timestamp'] = f['results']['timestamp']
	ctrs['name']   = f['results']['instances']['instance-data']['name']
	ctrs['uuid']   = f['results']['instances']['instance-data']['uuid']
	for ctr in f['results']['instances']['instance-data']['counters']['counter-data']:
	    ctrs[ctr['name']] = ctr['value']
	return ctrs

    def get_object_counter_info(self,targObject):
	api = NaElement("perf-object-counter-list-info")
	api.child_add_string("objectname",targObject)
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    sys.exit (1)
	f = xmltodict.parse(xo.sprintf())
	lines = []
	for c in f['results']['counters']['counter-info']:
	    poss_fields = ["name","desc","privilege-level","aggregation-style","base-counter","is-key","labels","properties","translation-input-counter","type","unit"]
	    fields = []
	    for pf in poss_fields:
		if (pf in c.keys()):
		    if (pf == "labels"):
			try:
			    fields.append(c[pf]['label-info'].encode('ascii','ignore'))
			except AttributeError:
			    fields.append(c[pf]['label-info'][0].encode('ascii','ignore'))
		    else:
			try:
			    fields.append(c[pf].encode('ascii','ignore'))
			except AttributeError:
			    print "In AttributeError in get_object_counter_info"
		else:
		    fields.append("")
	    lines.append(string.join(fields, "|"))
	return lines

    def get_perf_objects(self):
	api = NaElement("perf-object-list-info")
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    print ("Error:\n")
	    print (xo.sprintf())
	    sys.exit (1)
	f = xmltodict.parse(xo.sprintf())
	objects = []
	for obj in f['results']['objects']['object-info']:
	    objects.append(obj['name'])
	return objects

    def load_vol_counters(self, targ_file="/home/duane/cdot_api_pull/vol-perf-counters.txt"):
	self.vol_ctr_info = {}
	lines = open(targ_file).read()
	for line in string.split(lines, '\n'):
	    try:
		fields    = string.split(line, '|')
		f_cluster = fields[0]
		f_svm     = fields[1]
		f_vol     = fields[2]
		f_ctr     = fields[3]
		f_desc    = fields[4]
		f_priv    = fields[5]
		f_junk    = fields[6]
		f_basec   = fields[7]    # use
		f_iskey   = fields[8]
		f_labels  = fields[9]
		f_props   = fields[10]   # use
		f_junk    = fields[11]
		f_type    = fields[12]   # use
		f_unit    = fields[13]   # use
		#
		if f_cluster not in self.vol_ctr_info:
		    self.vol_ctr_info[f_cluster] = {}
		if f_svm not in self.vol_ctr_info[f_cluster]:
		    self.vol_ctr_info[f_cluster][f_svm] = {}
		if f_vol not in self.vol_ctr_info[f_cluster][f_svm]:
		    self.vol_ctr_info[f_cluster][f_svm][f_vol] = {}
		if f_ctr not in self.vol_ctr_info[f_cluster][f_svm][f_vol]:
		    self.vol_ctr_info[f_cluster][f_svm][f_vol][f_ctr] = {}
		#
		self.vol_ctr_info[f_cluster][f_svm][f_vol][f_ctr]['base-counter'] = f_basec
		self.vol_ctr_info[f_cluster][f_svm][f_vol][f_ctr]['properties'] = f_props
		self.vol_ctr_info[f_cluster][f_svm][f_vol][f_ctr]['type'] = f_type
		self.vol_ctr_info[f_cluster][f_svm][f_vol][f_ctr]['unit'] = f_unit
	    except IndexError:
		self.tellme("caught exception parsing %s - %s" % (targ_file, line))

    def load_perf_counters(self, targ_file="/home/duane/cdot_api_pull/perf-counter-list.out"):
	self.perf_ctr_info = {}
	lines = open(targ_file).read()
	for line in string.split(lines, '\n'):
	    try:
		fields = string.split(line, '|')
		if (len(fields) == 14):
		    f_object_name   = fields[0]
		    f_instance_name = fields[1]
		    f_instance_uuid = fields[2]
		    f_counter_name  = fields[3]
		    f_counter_desc  = fields[4]
		    f_privs         = fields[5]
		    f_junk          = fields[6]
		    f_base_counter  = fields[7]    # use
		    f_iskey         = fields[8]
		    f_labels        = fields[9]    # use
		    f_properties    = fields[10]   # use
		    f_junk          = fields[11]
		    f_type          = fields[12]   # use
		    f_unit          = fields[13]   # use
		    # Store details as;
		    #  { object_name : { instance_name : { instance_uuid : { counter_name : { counter_name : value
		    # f_object_name.f_instance_uuid.f_counter_name
		    if f_object_name not in self.perf_ctr_info:
			self.perf_ctr_info[f_object_name] = {}
		    if f_instance_uuid not in self.perf_ctr_info[f_object_name]:
			self.perf_ctr_info[f_object_name][f_instance_uuid] = {}
		    if f_counter_name not in self.perf_ctr_info[f_object_name][f_instance_uuid]:
			self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name] = {}
		    #
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['object-name'] = f_object_name
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['counter-name'] = f_counter_name
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['instance-name'] = f_instance_name
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['instance-uuid'] = f_instance_uuid
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['base-counter'] = f_base_counter
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['labels'] = f_labels
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['properties'] = f_properties
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['type'] = f_type
		    self.perf_ctr_info[f_object_name][f_instance_uuid][f_counter_name]['unit'] = f_unit
		else:
		    pass
	    except IndexError:
		self.tellme("caught exception parsing %s - %s" % (targ_file, line))

    def vol_get_iter(self):
	api = NaElement("volume-get-iter")
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	xi1 = NaElement("volume-attributes")
	xi.child_add(xi1)
	xi2 = NaElement("volume-id-attributes")
	xi1.child_add(xi2)
	xi2.child_add_string("comment","<comment>")
	xi2.child_add_string("containing-aggregate-name","<containing-aggregate-name>")
	xi2.child_add_string("containing-aggregate-uuid","<containing-aggregate-uuid>")
	xi2.child_add_string("creation-time","<creation-time>")
	xi2.child_add_string("dsid","<dsid>")
	xi2.child_add_string("fsid","<fsid>")
	xi2.child_add_string("instance-uuid","<instance-uuid>")
	xi2.child_add_string("junction-parent-name","<junction-parent-name>")
	xi2.child_add_string("junction-path","<junction-path>")
	xi2.child_add_string("msid","<msid>")
	xi2.child_add_string("name","<name>")
	xi2.child_add_string("name-ordinal","<name-ordinal>")
	xi2.child_add_string("owning-vserver-name","<owning-vserver-name>")
	xi2.child_add_string("owning-vserver-uuid","<owning-vserver-uuid>")
	xi2.child_add_string("provenance-uuid","<provenance-uuid>")
	xi2.child_add_string("style","<style>")
	xi2.child_add_string("type","<type>")
	xi2.child_add_string("uuid","<uuid>")
	xi3 = NaElement("volume-space-attributes")
	xi1.child_add(xi3)
	xi3.child_add_string("filesystem-size","<filesystem-size>")
	xi3.child_add_string("is-filesys-size-fixed","<is-filesys-size-fixed>")
	xi3.child_add_string("is-space-guarantee-enabled","<is-space-guarantee-enabled>")
	xi3.child_add_string("overwrite-reserve","<overwrite-reserve>")
	xi3.child_add_string("overwrite-reserve-required","<overwrite-reserve-required>")
	xi3.child_add_string("overwrite-reserve-used","<overwrite-reserve-used>")
	xi3.child_add_string("overwrite-reserve-used-actual","<overwrite-reserve-used-actual>")
	xi3.child_add_string("percentage-fractional-reserve","<percentage-fractional-reserve>")
	xi3.child_add_string("percentage-size-used","<percentage-size-used>")
	xi3.child_add_string("percentage-snapshot-reserve","<percentage-snapshot-reserve>")
	xi3.child_add_string("percentage-snapshot-reserve-used","<percentage-snapshot-reserve-used>")
	xi3.child_add_string("size","<size>")
	xi3.child_add_string("size-available","<size-available>")
	xi3.child_add_string("size-available-for-snapshots","<size-available-for-snapshots>")
	xi3.child_add_string("size-total","<size-total>")
	xi3.child_add_string("size-used","<size-used>")
	xi3.child_add_string("size-used-by-snapshots","<size-used-by-snapshots>")
	xi3.child_add_string("snapshot-reserve-size","<snapshot-reserve-size>")
	xi3.child_add_string("space-full-threshold-percent","<space-full-threshold-percent>")
	xi3.child_add_string("space-guarantee","<space-guarantee>")
	xi3.child_add_string("space-mgmt-option-try-first","<space-mgmt-option-try-first>")
	xi3.child_add_string("space-nearly-full-threshold-percent","<space-nearly-full-threshold-percent>")                                                                                           
	api.child_add_string("max-records","20000")                                                                                                                                                   
	api.child_add_string("query","<query>")                                                                                                                                                       
	xo = self.s.invoke_elem(api)                                                                           
	self.sd.incr("api.invoke")

	return xmltodict.parse(xo.sprintf())

    def aggr_get_iter(self):
	api = NaElement("aggr-get-iter")
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	xi1 = NaElement("aggr-attributes")
	xi.child_add(xi1)
	xi2 = NaElement("aggr-ownership-attributes")
	xi1.child_add(xi2)
	xi2.child_add_string("home-id","<home-id>")
	xi2.child_add_string("home-name","<home-name>")
	xi2.child_add_string("owner-id","<owner-id>")
	xi2.child_add_string("owner-name","<owner-name>")
	xi3 = NaElement("aggr-snapshot-attributes")
	xi1.child_add(xi3)
	xi3.child_add_string("files-total","<files-total>")
	xi3.child_add_string("files-used","<files-used>")
	xi3.child_add_string("is-snapshot-auto-create-enabled","<is-snapshot-auto-create-enabled>")
	xi3.child_add_string("is-snapshot-auto-delete-enabled","<is-snapshot-auto-delete-enabled>")
	xi3.child_add_string("maxfiles-available","<maxfiles-available>")
	xi3.child_add_string("maxfiles-possible","<maxfiles-possible>")
	xi3.child_add_string("maxfiles-used","<maxfiles-used>")
	xi3.child_add_string("percent-inode-used-capacity","<percent-inode-used-capacity>")
	xi3.child_add_string("percent-used-capacity","<percent-used-capacity>")
	xi3.child_add_string("size-available","<size-available>")
	xi3.child_add_string("size-total","<size-total>")
	xi3.child_add_string("size-used","<size-used>")
	xi3.child_add_string("snapshot-reserve-percent","<snapshot-reserve-percent>")
	xi4 = NaElement("aggr-space-attributes")
	xi1.child_add(xi4)
	xi4.child_add_string("aggregate-metadata","<aggregate-metadata>")
	xi4.child_add_string("hybrid-cache-size-total","<hybrid-cache-size-total>")
	xi4.child_add_string("percent-used-capacity","<percent-used-capacity>")
	xi4.child_add_string("size-available","<size-available>")
	xi4.child_add_string("size-total","<size-total>")
	xi4.child_add_string("size-used","<size-used>")
	xi4.child_add_string("total-reserved-space","<total-reserved-space>")
	xi4.child_add_string("used-including-snapshot-reserve","<used-including-snapshot-reserve>")
	xi4.child_add_string("volume-footprints","<volume-footprints>")
	xi5 = NaElement("aggr-volume-count-attributes")
	xi1.child_add(xi5)
	xi5.child_add_string("flexvol-count","<flexvol-count>")
	xi5.child_add_string("flexvol-count-collective","<flexvol-count-collective>")
	xi5.child_add_string("flexvol-count-not-online","<flexvol-count-not-online>")
	xi5.child_add_string("flexvol-count-quiesced","<flexvol-count-quiesced>")
	xi5.child_add_string("flexvol-count-striped","<flexvol-count-striped>")
	xi1.child_add_string("aggregate-name","<aggregate-name>")
	xi1.child_add_string("aggregate-uuid","<aggregate-uuid>")
	xi6 = NaElement("nodes")
	xi1.child_add(xi6)
	xi6.child_add_string("node-name","<node-name>")
	api.child_add_string("max-records","2000")
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")

	return xmltodict.parse(xo.sprintf())
