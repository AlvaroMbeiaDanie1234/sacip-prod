from django.urls import path
from . import views

urlpatterns = [
    path('suspects/', views.SuspectListView.as_view(), name='suspect-list'),
    path('suspects/<int:pk>/', views.SuspectDetailView.as_view(), name='suspect-detail'),
    path('camera-feeds/', views.CameraFeedListView.as_view(), name='camera-feed-list'),
    path('camera-feeds/<int:pk>/', views.CameraFeedDetailView.as_view(), name='camera-feed-detail'),
    path('recognition-results/', views.RecognitionResultListView.as_view(), name='recognition-result-list'),
    path('recognition-results/<int:pk>/', views.RecognitionResultDetailView.as_view(), name='recognition-result-detail'),
    path('alerts/', views.AlertListView.as_view(), name='alert-list'),
    path('alerts/<int:pk>/', views.AlertDetailView.as_view(), name='alert-detail'),
    path('alerts/unread/', views.UnreadAlertsView.as_view(), name='unread-alerts'),
    path('process-frame/', views.process_frame, name='process-frame'),
]