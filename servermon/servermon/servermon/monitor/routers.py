from swampdragon import route_handler
from swampdragon.route_handler import BaseRouter
from .system_info import broadcast_sys_info


class SysInfoRouter(BaseRouter):
    route_name = 'sys'

    def get_subscription_channels(self, **kwargs):
        broadcast_sys_info()
        return ['sysinfo']


route_handler.register(SysInfoRouter)