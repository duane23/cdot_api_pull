# netapp-collectd-plugin - netapp_info.py

import collectd
import socket
import string

import sys


sys.path.append("/opt/collectd/lib/collectd/plugins/python")
from qos_report import QoS_info

# Verbose logging on/off. Override in config by specifying 'Verbose'.
VERBOSE_LOGGING = False

def configure_callback(conf):
    """Receive configuration block"""
    global REDIS_HOST, REDIS_PORT, VERBOSE_LOGGING
    for node in conf.children:
        if node.key == 'Host':
            REDIS_HOST = node.values[0]
        elif node.key == 'Port':
            REDIS_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        else:
            collectd.warning('netapp_info plugin: Unknown config key: %s.'
                             % node.key)
    log_verbose('Configured with host=%s, port=%s' % (REDIS_HOST, REDIS_PORT))

def dispatch_value(info, key, type, type_instance=None):
    """Read a key from info response data and dispatch a value"""
    if key not in info:
        collectd.warning('netapp_info plugin: Info key not found: %s' % key)
        return
    if not type_instance:
        type_instance = key

    if (type == 'disk_ops'):

	log_verbose("key: %s" % key)
	v1 = collectd.Values(plugin=key)
	#v1 = collectd.Values(type='disk_ops')
	v1.type = 'disk_ops'
	key2 = string.join(string.split(key, '.'),'_').encode('ascii','ignore')
	key3 = string.join(string.split(key2, '-'),'_').encode('ascii','ignore')

	#key3 = u"brisvegas_vs1-pauls_rootvol_total_ops%s" % key2

	fields = []
	fields = string.split(key, '.')
	f_cn = fields[0].encode('ascii','ignore')
	f_vs = fields[1].encode('ascii','ignore')
	f_vl = fields[2].encode('ascii','ignore')
	f_mt = fields[3].encode('ascii','ignore')

	key4 = "%s_%s_%s_%s" % (f_cn, f_vs, f_vl, f_mt)

	#log_verbose("type(key2): %s" % type(key2))
	#key2 = "brisvegas_vs1-taits_vs1taits_root_total_ops"
	#log_verbose("type(key2): %s" % type(key2))
	v1.plugin = key3
	log_verbose("key3: %s" % key3)
	value = int(info[key])
	v1.dispatch(values=[value, value])
	#log_verbose("dispatched key: %s" % string.join(string.split(key, '.'), '_'))
 



#	log_verbose('Sending value: %s=%s, type is %s' % (type_instance, value, type))
#	val = collectd.Values(type='disk_ops')
#	val.plugin = type_instance
#	#val.type = type
#	val.type_instance = type_instance
#	val.values = [value, value]
#	log_verbose("val.type: %s" % type)
#	log_verbose("val.type_instance: %s" % type_instance)
#	log_verbose("values: %f,%f" % ( value, value))
#	#log_verbose("dir(val) %s" % ( dir(val)))
#	val.dispatch()
    else:
	value = int(info[key])
	log_verbose('Sending value: %s=%s, type is %s' % (type_instance, value, type))
	val = collectd.Values(plugin='netapp_info')
	val.type = type
	val.type_instance = type_instance
	val.values = [value]
	val.dispatch()

def read_callback():
    log_verbose('Read callback called')
    z = QoS_info('brisvegas', '10.128.153.60','BNELAB\\duanes','D3m0open', "1.21")
    for l in z.get_qos_stats():
	for entry in l.keys():
	    dispatch_value(l, entry, 'gauge')
    for v in z.get_vol_stats():
	for et in v.keys():
	    dispatch_value(v, et, 'disk_ops')

def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('netapp plugin [verbose]: %s' % msg)

def log_callback(sev, msg):
    fp = open("/var/tmp/netapp_info.log", "a")
    fp.write('netapp plugin [verbose-%s]: %s\n' % (sev, msg))
    fp.close()

# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback, 60)
collectd.register_log(log_callback)
