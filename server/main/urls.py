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
  path('incomes/', views.IncomesView.as_view()),  # type: ignore
  path('incomes/new/', views.NewIncomeView.as_view()),  # type: ignore
  path('income/<int:pk>/', views.IncomeView.as_view()),  # type: ignore
  path('receipts/', views.ReceiptsView.as_view()),  # type: ignore
  path('income/<int:pk>/receipts/', views.IncomeReceiptsView.as_view()),  # type: ignore
  path('receipt/<int:pk>/', views.ReceiptView.as_view()),  # type: ignore
]
