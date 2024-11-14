from django.urls import path, include
from rest_framework import routers
from .views import BlockedSiteViewSet, BlockSiteView, UnblockSiteView

router = routers.DefaultRouter()
router.register(r'blocked_sites', BlockedSiteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('block/', BlockSiteView.as_view(), name='block_site'),
    path('unblock/', UnblockSiteView.as_view(), name='unblock_site'),
]