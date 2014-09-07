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

#CLUSTER_NAME = "brisvegas"
#MAX_VOLUMES  = 20000

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


    def get_counters(self, instance_uuid):
	"""
	    Get counters for volume instance-uuid's

	    A string, representing filter data, in the format of key=value pairs. Multiple pairs can be specified via comma (",")
	    or pipe ("|") separation. The applied filter is a combination of ANDing and ORing the key-value pairs.
	    A comma indicates ANDing, a pipe indicates ORing, and the order of precedence is AND and then OR. For example,
	    "instance_name=volA,vserver_name=vs1|vserver_name=vs2" equates to "(instance_name=volA && vserver_name=vs1) |
	    (vserver_name=vs2)". This would return instances on Vserver vs1 with name volA and all instances on Vserver vs2.
	"""

	api = NaElement("perf-object-get-instances")
	xi = NaElement("counters")
	api.child_add(xi)
	xi2 = NaElement("instances")
	api.child_add(xi2)
	api.child_add_string("objectname","volume")
	xi1 = NaElement("instance-uuids")
	api.child_add(xi1)
	xi1.child_add_string("instance-uuid",instance_uuid)
	ctrs = {}
	xo = self.s.invoke_elem(api)
	if (xo.results_status() == "failed") :
	    ## Volumes which are currently offline will error here as no counters are collected
	    return ctrs
	try:
	    f = xmltodict.parse(xo.sprintf())
	except xml.parsers.expat.ExpatError:
	    print xo.sprintf()
	ctrs['timestamp'] = f['results']['timestamp']
	ctrs['volname']   = f['results']['instances']['instance-data']['name']
	ctrs['voluuid']   = f['results']['instances']['instance-data']['uuid']
	for ctr in f['results']['instances']['instance-data']['counters']['counter-data']:
	    ctrs[ctr['name']] = ctr['value']
	return ctrs

    def get_object_counter_info(self,targObject):
	api = NaElement("perf-object-counter-list-info")
	api.child_add_string("objectname",targObject)
	xo = self.s.invoke_elem(api)
	if (xo.results_status() == "failed") :
	    sys.exit (1)
	f = xmltodict.parse(xo.sprintf())
	lines = []
	for c in f['results']['counters']['counter-info']:
	    ##
	    ## Need more code to handle case where base-counter is present and where data type is array / histogram
	    ##
	    lines.append("%s|%s|%s|%s" % (c["name"],c["properties"],c["unit"],c["desc"]))
	return lines

    def get_objects(self):
	api = NaElement("perf-object-list-info")
	#api.child_add_string("filter-data", "<filter-data>")
	xo = self.s.invoke_elem(api)
	if (xo.results_status() == "failed") :
	    print ("Error:\n")
	    print (xo.sprintf())
	    sys.exit (1)
	f = xmltodict.parse(xo.sprintf())
	objects = []
	for obj in f['results']['objects']['object-info']:
	    objects.append(obj['name'])
	return objects
