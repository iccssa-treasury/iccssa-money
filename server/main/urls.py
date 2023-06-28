from django.urls import path
from . import views

app_name = 'main'  # Namespace for URLs
urlpatterns = [
  path('destinations/', views.DestinationsView.as_view()),  # type: ignore
  path('destination/<int:pk>/', views.DestinationView.as_view()),  # type: ignore
]
