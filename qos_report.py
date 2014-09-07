#!/usr/bin/python
##
## $Id: qos_report.py,v 1.1 2014/09/05 02:18:33 duane Exp duane $
##
## Todo:
##
import sys,string,time
sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
from NaServer import *
import xmltodict
#from collectd_unixsock import Collectd

import statsd

class QoS_info:
    def __init__(self, cluster_name, cluster_ip, username, password, sdk_ver, server_type="FILER", transport_type="HTTPS", port="443", style="LOGIN"):
	major, minor = string.split(sdk_ver, '.')
	self.CLUSTER_NAME = cluster_name
	self.MAX_VOLUMES  = 2000
	self.s = NaServer(cluster_ip, major, minor)
	self.s.set_server_type(server_type)
	self.s.set_transport_type(transport_type)
	self.s.set_port(port)
	self.s.set_style(style)
	self.s.set_admin_user(username, password)

    def get_qos_stats(self):
	self.policy_groups = self.get_qos_pgs()
	self.workloads     = self.get_qos_workloads()
	self.pgs = {}
	for pg in self.policy_groups['results']['attributes-list']['qos-policy-group-info']:
	    max_iops = int(string.split(pg['max-throughput'], 'IOPS')[0])
	    curr_pg = pg['policy-group']
	    self.pgs[curr_pg] = {}
	    self.pgs[curr_pg]['policy-group']       = pg['policy-group']
	    self.pgs[curr_pg]['max-throughput']     = max_iops
	    self.pgs[curr_pg]['pgid']               = pg['pgid']
	    self.pgs[curr_pg]['policy-group-class'] = pg['policy-group-class']
	    self.pgs[curr_pg]['uuid']               = pg['uuid']
	    self.pgs[curr_pg]['timestamp']          = string.split(str(time.time()),'.')[0]
	for wl in self.workloads['results']['attributes-list']['qos-workload-info']:
	    targ_pg = wl['policy-group']
	    try:
		self.pgs[targ_pg]['vserver'] = wl['vserver']
		self.pgs[targ_pg]['volume'] = wl['volume']
	    except:
		pass
	lines = []
	for line in self.pgs.values():
	    try:
		metric_string =  "%s.%s.qos_max_iops" % (line['vserver'], line['volume'])
		data = {}
		data[metric_string] = float(line['max-throughput'])
		lines.append(data)
	    except KeyError:
		pass
	return lines

    def get_vol_stats(self):
	ret = []
	for v in self.get_volumes():
	    try:
		v_cn  = v['cluster-name']
		v_svm = v['owning-vserver-name']
		v_vol = v['name']
		c = self.get_vol_counters(v['instance-uuid'])
		c_ts = c['timestamp']                                                                                                                                                             
		c_read_ops  = c['read_ops']                                                                                                                                                       
		c_write_ops = c['write_ops']                                                                                                                                                      
		c_total_ops = c['total_ops']                                                                                                                                                      
		metric_string =  "%s.%s.total_ops" % (v_svm, v_vol)                                                                                                                                
		data = {}
		read_ops_key_u = "%s.%s.%s.read_ops" % (self.CLUSTER_NAME, v_svm, v_vol)
		read_ops_key = read_ops_key_u.encode('ascii','ignore')
		data[read_ops_key] = float(c['read_ops'])

		write_ops_key_u = "%s.%s.%s.write_ops" % (self.CLUSTER_NAME, v_svm, v_vol)
		write_ops_key = write_ops_key_u.encode('ascii','ignore')
		data[write_ops_key] = float(c['write_ops'])

		total_ops_key_u = "%s.%s.%s.total_ops" % (self.CLUSTER_NAME, v_svm, v_vol)
		total_ops_key = total_ops_key_u.encode('ascii','ignore')
		data[total_ops_key] = float(c['total_ops'])
		ret.append(data)
	    except KeyError:                                                                                                                                                                      
		continue                                                         
	return ret


    def get_volumes(self):
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
	    vol_list.append({
			     'cluster-name':self.CLUSTER_NAME,
			     'owning-vserver-name':volume['volume-id-attributes']['owning-vserver-name'],
			     'name':volume['volume-id-attributes']['name'],
			     'instance-uuid':volume['volume-id-attributes']['instance-uuid']
			    })
	return vol_list


    def get_vol_counters(self, instance_uuid):
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
	    ##
	    ## Volumes which are currently offline will error here as no counters are collected
	    ##
	    fp = open('/var/tmp/ctrs-fail.xml','a')
	    fp.write(xo.sprintf())
	    fp.close()
	    return ctrs
	fp = open('/var/tmp/ctrs.xml','a')
	fp.write(xo.sprintf())
	fp.close()
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

    def get_qos_pgs(self):
	api = NaElement("qos-policy-group-get-iter")
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	xi1 = NaElement("qos-policy-group-info")
	xi.child_add(xi1)
	# These control what fields are returned for each record
	xi1.child_add_string("max-throughput","<max-throughput>")
	#xi1.child_add_string("num-workloads","<num-workloads>")
	xi1.child_add_string("pgid","<pgid>")
	xi1.child_add_string("policy-group","<policy-group>")
	xi1.child_add_string("policy-group-class","<policy-group-class>")
	xi1.child_add_string("uuid","<uuid>")
	xi1.child_add_string("vserver","<vserver>")
	api.child_add_string("max-records",100000)
	xi2 = NaElement("query")
	api.child_add(xi2)
	xi3 = NaElement("qos-policy-group-info")
	xi2.child_add(xi3)
	# These control what records are returned
	#xi3.child_add_string("max-throughput","<max-throughput>")
	#xi3.child_add_string("num-workloads","<num-workloads>")
	#xi3.child_add_string("pgid","<pgid>")
	#xi3.child_add_string("policy-group","<policy-group>")
	xi3.child_add_string("policy-group-class","user-defined")
	#xi3.child_add_string("uuid","<uuid>")
	#xi3.child_add_string("vserver","<vserver>")
	#api.child_add_string("tag","<tag>")
	xo = self.s.invoke_elem(api)
	if (xo.results_status() == "failed") :
	    print ("Error:\n")
	    print (xo.sprintf())
	    sys.exit (1)
	return xmltodict.parse(xo.sprintf())

    def get_qos_workloads(self):
	api = NaElement("qos-workload-get-iter")
	xi = NaElement("desired-attributes")
	api.child_add(xi)
	xi1 = NaElement("qos-workload-info")
	xi.child_add(xi1)
	xi1.child_add_string("category","<category>")
	xi1.child_add_string("file","<file>")
	xi1.child_add_string("lun","<lun>")
	xi1.child_add_string("policy-group","<policy-group>")
	xi1.child_add_string("qtree","<qtree>")
	xi1.child_add_string("read-ahead","<read-ahead>")
	xi1.child_add_string("volume","<volume>")
	xi1.child_add_string("vserver","<vserver>")
	xi1.child_add_string("wid","<wid>")
	xi1.child_add_string("workload-class","<workload-class>")
	xi1.child_add_string("workload-name","<workload-name>")
	xi1.child_add_string("workload-uuid","<workload-uuid>")
	api.child_add_string("max-records",100000)
	xi2 = NaElement("query")
	api.child_add(xi2)
	xi3 = NaElement("qos-workload-info")
	xi2.child_add(xi3)
	#xi3.child_add_string("category","<category>")
	#xi3.child_add_string("file","<file>")
	#xi3.child_add_string("lun","<lun>")
	#xi3.child_add_string("policy-group","<policy-group>")
	#xi3.child_add_string("qtree","<qtree>")
	#xi3.child_add_string("read-ahead","<read-ahead>")
	#xi3.child_add_string("volume","<volume>")
	#xi3.child_add_string("vserver","<vserver>")
	#xi3.child_add_string("wid","<wid>")
	xi3.child_add_string("workload-class","user_defined")
	#xi3.child_add_string("workload-name","<workload-name>")
	#xi3.child_add_string("workload-uuid","<workload-uuid>")
	#api.child_add_string("tag","<tag>")
	xo = self.s.invoke_elem(api)
	if (xo.results_status() == "failed") :
	    print ("Error:\n")
	    print (xo.sprintf())
	    sys.exit (1)
	return xmltodict.parse(xo.sprintf())

def main():
    qos_obj = QoS_info('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
    for l in qos_obj.get_qos_stats():
	c = statsd.StatsClient('localhost',8125)
	for k in l.keys():
	    #print ">>> k: %s, %s" % (k, l[k])
	    c.gauge("brisvegas.%s" % k, l[k])
	    print "brisvegas.%s" % k, l[k]



if __name__ == "__main__":
    main()

