from rest_framework import serializers
from api.models import BlockedSite

class BlockedSiteSerializer(serializers.ModelSerializer):
    expiration = serializers.SerializerMethodField()

    class Meta:
        model = BlockedSite
        fields = ['id', 'url', 'duration', 'blocked_at', 'expiration']

    def get_expiration(self, obj):
        return int(obj.expiration.timestamp() * 1000)  # Convert to milliseconds
