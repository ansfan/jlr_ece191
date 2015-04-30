from swampdragon import route_handler
from swampdragon.route_handler import BaseRouter
from .system_info import broadcast_sys_info
from .platform import platform_broadcast

class SysInfoRouter(BaseRouter):
    route_name = 'sys'

    def get_subscription_channels(self, **kwargs):
        broadcast_sys_info()
        return ['sysinfo_sent', 'sysinfo_rec', 'sysinfo_cpu']

route_handler.register(SysInfoRouter)