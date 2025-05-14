from rest_framework import serializers

class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()

class RouteRequestSerializer:
    def __init__(self, data):
        self.data = data
        self.validated_data = {}
        self.errors = {}

    def is_valid(self):
        for field in ['start', 'destination']:
            if field not in self.data:
                self.errors[field] = f"'{field}' is required"
        if not self.errors:
            self.validated_data = {
                'start': self.data['start'],
                'destination': self.data['destination']
            }
            return True
        return False


