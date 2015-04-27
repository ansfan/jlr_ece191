from tornado.ioloop import PeriodicCallback
from swampdragon.pubsub_providers.data_publisher import publish_data
import psutil


pcb = None

def broadcast_sys_info():
    global pcb

    if pcb is None:
        pcb = PeriodicCallback(broadcast_sys_info, 500)
        pcb.start()

    cpu = psutil.cpu_percent()
    net = psutil.net_io_counters()
    bytes_sent = '{0:.2f} kb'.format(net.bytes_recv / 1024)
    bytes_rcvd = '{0:.2f} kb'.format(net.bytes_sent / 1024)

    publish_data('sysinfo', {
        'cpu': cpu,
        'kb_received': bytes_sent,
        'kb_sent': bytes_rcvd,
    })