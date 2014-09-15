#!/usr/bin/python
##
## $Id: feed_statsd.py,v 1.2 2014/09/05 07:25:16 duane Exp duane $
##
## Todo:
##  - 
##
import sys,string
sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
from NaServer import *
import xmltodict
import statsd
import time
import os

class CdotPerf:
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
	self.fp = open("/var/tmp/tellme.log", "a")
	try:
	    self.debug = open("/var/tmp/debugenabled")
	    self.debug.close()
	    self.debug = True
	except IOError:
	    self.debug = False
	    pass
	self.targ_vol_counters = "avg_latency,cifs_other_latency,cifs_other_ops,cifs_read_data,cifs_read_latency,cifs_read_ops,cifs_write_data,cifs_write_latency,cifs_write_ops,fcp_other_latency,fcp_other_ops,fcp_read_data,fcp_read_latency,fcp_read_ops,fcp_write_data,fcp_write_latency,fcp_write_ops,flexcache_other_ops,flexcache_read_data,flexcache_read_ops,flexcache_receive_data,flexcache_send_data,flexcache_write_data,flexcache_write_ops,iscsi_other_latency,iscsi_other_ops,iscsi_read_data,iscsi_read_latency,iscsi_read_ops,iscsi_write_data,iscsi_write_latency,iscsi_write_ops,nfs_other_latency,nfs_other_ops,nfs_read_data,nfs_read_latency,nfs_read_ops,nfs_write_data,nfs_write_latency,nfs_write_ops,other_latency,other_ops,read_blocks,read_data,read_latency,read_ops,san_other_latency,san_other_ops,san_read_data,san_read_latency,san_read_ops,san_write_data,san_write_latency,san_write_ops,total_ops,write_blocks,write_data,write_latency,write_ops"



    def tellme(self, message):
	if (self.debug):
	    self.fp.write("%s\n" % message)

    def get_aggregates(self):
	"""
	    Get list of volumes from cluster
	"""
	api = NaElement("aggr-get-iter")
	#xi = NaElement("desired-attributes")
	#api.child_add(xi)
	## This specifies max number of volume records to pull from sdk api
	## Default is 20. 20000 is enough for most clusters
	api.child_add_string("max-records",self.MAX_VOLUMES)
	#xi1 = NaElement("aggr-attributes")
	#xi.child_add(xi1)
	#xi41 = NaElement("volume-id-attributes")
	#xi41.child_add_string("instance-uuid","<instance-uuid>")
	#xi41.child_add_string("name","<name>")
	#xi41.child_add_string("owning-vserver-name","<owning-vserver-name>")
	#xi41.child_add_string("uuid","<uuid>")
	#xi1.child_add(xi41)
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	#print xo.sprintf()
	f = xmltodict.parse(xo.sprintf())
	#print xo.sprintf()
	aggrs = f['results']['attributes-list']['aggr-attributes']
	aggr_list = []
	for aggr in aggrs:
	    for z in aggr.keys():
		try:
		    if (z == 'aggregate-name'):
			aggr_name = aggr[z]
			#print "aggr_name: %s" % aggr_name
		    elif (z == 'aggregate-uuid'):
			aggr_uuid = aggr[z]
			#print "aggr_uuid: %s" % aggr_uuid
		    elif (z == 'aggr-ownership-attributes'):
			aggr_ownr = aggr[z]['owner-name']
			#print "aggr_ownr: %s" % aggr_ownr
		    #print "z: %s" % z
		    #print "kggr[z].keys: %s" % aggr[z].keys()
		except AttributeError:
		    #print "In Exception - aggr[z]: %s" % aggr[z]
		    pass
	    aggr_list.append({
			      'cluster-name':self.CLUSTER_NAME,
			      'aggr-name':aggr_name,
			      'aggr-uuid':aggr_uuid,
			      'owner-name':aggr_ownr
			     })
	return aggr_list

    def get_volumes(self):
	"""
	    Get list of volumes from cluster
	"""
	api = NaElement("volume-get-iter")
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	## This specifies max number of volume records to pull from sdk api
	## Default is 20. 20000 is enough for most clusters
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
	#xi = NaElement("counters")
	#api.child_add(xi)
	#xi.child_add_string("counter",counter_filter_list)
	xi2 = NaElement("instances")
	api.child_add(xi2)
	xi2.child_add_string("instance",instance_name)
	#xi3 = NaElement("instance-uuids")
	#api.child_add(xi3)
	#xi3.child_add_string("instance-uuid",instance_uuid)
	##
	## TODO - make this generic to get counters for non-volume uuids
	##
	api.child_add_string("objectname",object_name)
	#xi1 = NaElement("instance-uuids")
	#api.child_add(xi1)
	#xi1.child_add_string("instance-uuid",instance_uuid)
	ctrs = {}
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    ## Volumes which are currently offline will error here as no counters are collected
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

    def get_object_instance_list_info(self, object_name):

	api = NaElement("perf-object-instance-list-info-iter")
	#
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	#
	#
	#xi1 = NaElement("instance-info")
	#xi.child_add(xi1)
	#
	#xi1.child_add_string("name","<name>")
	#xi1.child_add_string("uuid","<uuid>")
	#api.child_add_string("filter-data","<filter-data>")
	api.child_add_string("max-records",1000000)
	api.child_add_string("objectname",object_name)
	#
#	xi2 = NaElement("query")
#	api.child_add(xi2)
	#
	#
#	xi3 = NaElement("instance-info")
#	xi2.child_add(xi3)
	#
#	xi3.child_add_string("name","<name>")
#	xi3.child_add_string("uuid","<uuid>")
#	api.child_add_string("tag","<tag>")
	#
	xo = self.s.invoke_elem(api)
	if (xo.results_status() == "failed") :
	    print ("Error:\n")
	    print (xo.sprintf())
	    sys.exit (1)
	#
	print ("Received:\n")
	print (xo.sprintf())

	ctrs = {}
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    ## Volumes which are currently offline will error here as no counters are collected
	    print xo.sprintf()
	    return ctrs
	try:
	    f = xmltodict.parse(xo.sprintf())
	except xml.parsers.expat.ExpatError:
	    print xo.sprintf()
#	ctrs['timestamp'] = f['results']['timestamp']
#	ctrs['volname']   = f['results']['instances']['instance-data']['name']
#	ctrs['voluuid']   = f['results']['instances']['instance-data']['uuid']
#	for ctr in f['results']['instances']['instance-data']['counters']['counter-data']:
#	    ctrs[ctr['name']] = ctr['value']
#	return ctrs



    def get_counters_by_uuid(self, instance_uuid, object_name, counter_filter_list=None):
	api = NaElement("perf-object-get-instances")
	xi = NaElement("counters")
	api.child_add(xi)
	xi.child_add_string("counter",counter_filter_list)
	#xi2 = NaElement("instances")
	#api.child_add(xi2)
	#xi2.child_add_string("instance",instance)
	xi3 = NaElement("instance-uuids")
	api.child_add(xi3)
	xi3.child_add_string("instance-uuid",instance_uuid)
	##
	## TODO - make this generic to get counters for non-volume uuids
	##
	api.child_add_string("objectname",object_name)
	#xi1 = NaElement("instance-uuids")
	#api.child_add(xi1)
	#xi1.child_add_string("instance-uuid",instance_uuid)
	ctrs = {}
	xo = self.s.invoke_elem(api)
	self.sd.incr("api.invoke")
	if (xo.results_status() == "failed") :
	    ## Volumes which are currently offline will error here as no counters are collected
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
	    ## Need more code to handle case where base-counter is present and where data type is array / histogram
	    ##
	    ## Mandatory fields returned: name, desc, privilege-level
	    ## Optional fields returned:  aggregation-style, base-counter, is-key, labels, properties, translation-input-counter, type, unit
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
		    #
		    # Store details as;
		    #  { object_name : { instance_name : { instance_uuid : { counter_name : { counter_name : value
		    #                                                                         
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
		    print "parsing line failed for >>%s<<" % line

	    except IndexError:
		print "caught exception parsing %s - %s" % (targ_file, line)
		self.tellme("caught exception parsing %s - %s" % (targ_file, line))

