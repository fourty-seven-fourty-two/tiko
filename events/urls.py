from rest_framework import routers

from events import views as event_views


router = routers.SimpleRouter()
router.register(r"events", event_views.EventViewSet)

urlpatterns = router.urls
