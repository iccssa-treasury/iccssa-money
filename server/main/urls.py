from django.urls import path
from . import views

app_name = 'main'  # Namespace for URLs
urlpatterns = [
  path('destinations/', views.DestinationsView.as_view()),  # type: ignore
  path('me/destinations/', views.UserDestinationsView.as_view()),  # type: ignore
  path('destination/<int:pk>/', views.DestinationView.as_view()),  # type: ignore
  path('applications/', views.ApplicationsView.as_view()),  # type: ignore
  path('me/applications/', views.UserApplicationsView.as_view()),  # type: ignore
  path('applications/new/', views.NewApplicationView.as_view()),  # type: ignore'
  path('application/<int:pk>/', views.ApplicationView.as_view()),  # type: ignore
  path('events/', views.EventsView.as_view()),  # type: ignore
  path('application/<int:pk>/events/', views.ApplicationEventsView.as_view()),  # type: ignore
  path('event/<int:pk>', views.EventView.as_view()),  # type: ignore
]
