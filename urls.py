"""
imports...
"""


router_v1_0 = routers.DefaultRouter()

router_v1_0.register('home_meetings', views.MeetingViewSet)

urlpatterns = [
    path('', include(router_v1_0.urls)),
]
