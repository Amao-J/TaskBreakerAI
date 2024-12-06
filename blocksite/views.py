from datetime import timedelta
from django.utils import timezone
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

    def get(self, request):
        user = request.user
        now = timezone.now()

       
        blocked_sites = BlockedSite.objects.filter(user=user)

       
        expired_sites = []
        active_sites = []

        for site in blocked_sites:
            expiration_time = site.blocked_at + timedelta(minutes=site.duration)
            if expiration_time <= now:
                expired_sites.append(site)
            else:
                active_sites.append(site)

       
        BlockedSite.objects.filter(id__in=[site.id for site in expired_sites]).delete()

       
        data = BlockedSiteSerializer(active_sites, many=True).data

        return Response({
            'serverTime': now,
            'data': data
        })


    def post(self, request):
      
        url = request.data.get('url')
        duration = request.data.get('duration')
        user = request.user
        now=timezone.now()

       
        if not url or not duration:
            return Response({'error': 'URL and duration are required.'}, status=400)

        try:
            duration = int(duration)
            if duration <= 0 > 1440 :
                raise ValueError()
        except ValueError:
            return Response({'error': 'Duration must be a positive integer.'}, status=400)

        existing_site = BlockedSite.objects.filter(user=user, url=url).first()
        if existing_site:
            return Response({'error': 'This site is already blocked.'}, status=400)

        blocked_site = BlockedSite.objects.create(user=user, url=url, duration=duration)
        data = BlockedSiteSerializer(blocked_site).data
        response_data = {
            'ServerTime':now,
            'data': data,
            'message': 'Site blocked successfully.'
        }
        return Response(response_data, status=201)


class UnblockSiteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get('url')

        if not url:
            return Response({'error': 'URL is required.'}, status=400)

        blocked_sites = BlockedSite.objects.filter(url=url, user=request.user)

        if blocked_sites.exists():
            try:
                data = BlockedSiteSerializer(blocked_sites, many=True).data
                blocked_sites.delete()
                return Response({
                    'serverTime': timezone.now(),
                    'data': data,
                    'message': 'All matching sites unblocked successfully.'
                })
            except Exception as e:
                return Response({'error': f'Failed to unblock site: {str(e)}'}, status=500)
        else:
            return Response({'error': 'Site not found.'}, status=404)
