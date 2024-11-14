from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import BlockedSite
from .serializers import BlockedSiteSerializer


class BlockedSiteViewSet(viewsets.ModelViewSet):
    queryset = BlockedSite.objects.all()
    serializer_class = BlockedSiteSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class BlockSiteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get('url')
        duration = request.data.get('duration')
        if url and duration:
            user = request.user
            blocked_site = BlockedSite.objects.create(user=user, url=url, duration=duration)
            return Response({'message': 'Site blocked successfully.'})
        else:
            return Response({'error': 'Invalid data.'}, status=400)

class UnblockSiteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get('url')
        if url:
            try:
                blocked_site = BlockedSite.objects.filter(url=url, user=request.user)
                blocked_site.delete()
                return Response({'message': 'Site unblocked successfully.'})
            except BlockedSite.DoesNotExist:
                return Response({'error': 'Site not found.'}, status=404)
        else:
            return Response({'error': 'Invalid data.'}, status=400)