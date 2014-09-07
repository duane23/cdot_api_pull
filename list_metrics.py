#!/usr/bin/python
##
## $Id: list_metrics.py,v 1.1 2014/09/07 00:19:10 duane Exp duane $
##
## Todo:
##  - 
##
import sys,string
sys.path.append("/home/duane/lib/netapp-manageability-sdk-5.2.1R1/lib/python/NetApp")
from NaServer import *
import xmltodict
import statsd

CLUSTER_NAME = "brisvegas"
MAX_VOLUMES  = 20000

def get_volumes(s):
    api = NaElement("volume-get-iter")
    xi = NaElement("desired-attributes")
    api.child_add(xi)
    ## This specifies max number of volume records to pull from sdk api
    ## Default is 20. 20000 is enough for most clusters
    api.child_add_string("max-records",MAX_VOLUMES)
    xi1 = NaElement("volume-attributes")
    xi.child_add(xi1)
    xi41 = NaElement("volume-id-attributes")
    xi41.child_add_string("instance-uuid","<instance-uuid>")
    xi41.child_add_string("name","<name>")
    xi41.child_add_string("owning-vserver-name","<owning-vserver-name>")
    xi41.child_add_string("uuid","<uuid>")
    xi1.child_add(xi41)
    xo = s.invoke_elem(api)

    f = xmltodict.parse(xo.sprintf())
    volumes = f['results']['attributes-list']['volume-attributes']
    vol_list = []
    for volume in volumes:
	vol_list.append({
			 'cluster-name':CLUSTER_NAME,
			 'owning-vserver-name':volume['volume-id-attributes']['owning-vserver-name'],
			 'name':volume['volume-id-attributes']['name'],
			 'instance-uuid':volume['volume-id-attributes']['instance-uuid']
			})
    return vol_list

def get_counters(s,instance_uuid):
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

    xo = s.invoke_elem(api)

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

def main():
    s = NaServer("10.128.153.60", 1 , 21)
    s.set_server_type("FILER")
    s.set_transport_type("HTTPS")
    s.set_port(443)
    s.set_style("LOGIN")
    s.set_admin_user("BNELAB\\duanes", "D3m0open")

    cs = statsd.StatsClient('localhost',8125)


    for v in get_volumes(s):
	try:
	    v_cn  = v['cluster-name']
	    v_svm = v['owning-vserver-name']
	    v_vol = v['name']
	    c = get_counters(s, v['instance-uuid'])

	    c_ts = c['timestamp']
	    c_read_ops  = c['read_ops']
	    c_write_ops = c['write_ops']
	    c_total_ops = c['total_ops']

	    metric_string =  "brisvegas.%s.%s.read_ops" % (v_svm, v_vol)
	    print metric_string, c_read_ops, c_write_ops

	    cs.gauge(metric_string, c_read_ops)
	    metric_string =  "brisvegas.%s.%s.write_ops" % (v_svm, v_vol)
	    cs.gauge(metric_string, c_write_ops)

	    #print c

	except KeyError:
	    continue




if __name__ == "__main__":
    main()

    sys.exit(0)
