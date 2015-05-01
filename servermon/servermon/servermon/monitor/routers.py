from swampdragon import route_handler
from swampdragon.route_handler import BaseRouter, ModelRouter
from .system_info import broadcast_sys_info
from .serializers import RoomSerializer, RoomsSerializer
from .models import Room, Rooms

class SysInfoRouter(BaseRouter):
    route_name = 'sys'

    def get_subscription_channels(self, **kwargs):
        broadcast_sys_info()
        return ['sysinfo_sent', 'sysinfo_rec', 'sysinfo_cpu']

class RoomRouter(ModelRouter):
	route_name = 'room'
	serializer_class = RoomSerializer
	model = Room

	def get_object(self, **kwargs):
		return self.model.objects.get(pk=kwargs[id])

	def get_query_set(self, **kwargs):
		return self.model.objects.all()

class RoomsRouter(ModelRouter):
	route_name = 'rooms'
	serializer_class = RoomsSerializer
	model = Rooms

	def get_object(self, **kwargs):
		return self.model.objects.get(pk=kwargs[id])

	def get_query_set(self, **kwargs):
		return self.model.objects.all()

route_handler.register(SysInfoRouter)
route_handler.register(RoomRouter)
route_handler.register(RoomsRouter)
