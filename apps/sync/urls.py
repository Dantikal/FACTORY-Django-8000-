from django.urls import path
from .views import SyncInitialView, SyncPullView, SyncPushView, SyncStatusView

urlpatterns = [
    path('initial', SyncInitialView.as_view(), name='sync-initial-no-slash'),
    path('initial/', SyncInitialView.as_view(), name='sync-initial'),
    path('pull', SyncPullView.as_view(), name='sync-pull-no-slash'),
    path('pull/', SyncPullView.as_view(), name='sync-pull'),
    path('push', SyncPushView.as_view(), name='sync-push-no-slash'),
    path('push/', SyncPushView.as_view(), name='sync-push'),
    path('status', SyncStatusView.as_view(), name='sync-status-no-slash'),
    path('status/', SyncStatusView.as_view(), name='sync-status'),
]
