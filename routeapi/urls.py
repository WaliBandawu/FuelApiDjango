from django.urls import path
from .views import OptimizeRouteView,route_map_view

urlpatterns = [
    path('optimize-route/', OptimizeRouteView.as_view(), name='optimize-route'),
    path('map/', route_map_view, name='route-map'),
]
