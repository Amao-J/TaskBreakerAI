from rest_framework import serializers
from api.models import BlockedSite


class BlockedSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedSite
        fields = ['id', 'url','duration']
