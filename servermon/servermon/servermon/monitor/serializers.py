from swampdragon.serializers.model_serializer import ModelSerializer

class RoomSerializer(ModelSerializer):
    class Meta:
        model = 'Room'
        publish_fields = ('car_id', 'description')


class RoomsSerializer(ModelSerializer):
    class Meta:
        model = 'Rooms'
        publish_fields = ('description')
        update_fields = ('description')