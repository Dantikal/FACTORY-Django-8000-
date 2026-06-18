from django.urls import path
from .views import SyncInitialView

urlpatterns = [
    path('v1/initial', SyncInitialView.as_view(), name='sync-initial'),
]
