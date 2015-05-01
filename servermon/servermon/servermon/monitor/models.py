from django.db import models
from swampdragon.models import SelfPublishModel
from .serializers import RoomSerializer, RoomsSerializer

class Rooms(SelfPublishModel, models.Model):
	serializer_class = RoomsSerializer
	description = models.TextField()

class Room(SelfPublishModel, models.Model):
	serializer_class = RoomSerializer
	rooms = models.ForeignKey(Rooms)
	car_id = models.CharField(max_length=50)
	description = models.TextField()