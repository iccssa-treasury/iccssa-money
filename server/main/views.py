from datetime import datetime
import logging
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import views, generics, permissions, status
from .serializers import *
from accounts.models import Privilege
from .models import Level, Action

logger = logging.getLogger(__name__)


# API endpoints that implement L-CRUD (list, create, retrieve, update, destory).
# See: https://www.django-rest-framework.org/api-guide/serializers/
# See: https://www.django-rest-framework.org/api-guide/views/
# See: https://www.django-rest-framework.org/api-guide/generic-views/
# See: https://www.django-rest-framework.org/api-guide/viewsets/


# This time we use DRF's abstractions for views (`GenericAPIView`) and permissions (`BasePermission`)
# since the requirement is simple enough (straightforward L-CRUD, staff writable, others readonly).

class IsAdmin(permissions.BasePermission):
  def has_permission(self, request: Request, view: views.APIView):
    return (isinstance(request.user, User) and request.user.admin)


# class IsAdminOrReadOnly(permissions.BasePermission):
#   def has_permission(self, request: Request, view: views.APIView):
#     return (isinstance(request.user, User) and request.user.admin) or request.method in permissions.SAFE_METHODS


# class IsAdminOrPostOnly(permissions.BasePermission):
#   def has_permission(self, request: Request, view: views.APIView):
#     return (isinstance(request.user, User) and request.user.admin) or request.method == 'POST'


class DestinationsView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve all destinations.
  def get(self, request: Request) -> Response:
    if not isinstance(request.user, User):
      return Response([], status.HTTP_200_OK)
    queryset = Destination.objects.all()
    return Response(DestinationSerializer(queryset, many=True).data, status.HTTP_200_OK)


class UserDestinationsView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve all destinations for current user.
  def get(self, request: Request) -> Response:
    user = request.user
    if not isinstance(user, User):
      return Response([], status.HTTP_200_OK)
    queryset = Destination.objects.filter(user=user).order_by('-last_usage')
    return Response(DestinationSerializer(queryset, many=True).data, status.HTTP_200_OK)

  # Submit a new destination.
  def post(self, request: Request) -> Response:
    user = request.user
    if not isinstance(user, User):
      self.permission_denied(request)
    serializer = DestinationSerializer(data={
      'user': user.pk,
      'name': request.data.get('name'),
      'sort_code': request.data.get('sort_code'),
      'account_number': request.data.get('account_number'),
      'business': request.data.get('business'),
      'star': request.data.get('star'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class DestinationView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve a destination for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    destination = get_object_or_404(Destination, pk=pk)
    if not (isinstance(user, User) and user == destination.user):
      self.permission_denied(request)
    return Response(DestinationSerializer(destination).data, status.HTTP_200_OK)


def has_access_to_application(user: User, application: Application) -> bool:
  if not isinstance(user, User):
    return False
  # Admins can access all applications.
  if user.approval_level <= Privilege.PRESIDENT:
    return True
  # Commitees can access all applications from their department.
  if user.approval_level == Privilege.COMMITTEE:
    return user.department == application.department or user == application.user
  # Members can only access their own applications.
  return user == application.user


class ApplicationsView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve all applications that the current user can access.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    pks = [app.pk for app in Application.objects.all() if has_access_to_application(user, app)]
    queryset = Application.objects.filter(pk__in=pks).order_by('-timestamp')
    return Response(ApplicationSerializer(queryset, many=True).data, status.HTTP_200_OK)


class UserApplicationsView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve all applications created by current user.
  def get(self, request: Request) -> Response:
    user = request.user
    if not isinstance(user, User):
      return Response([], status.HTTP_200_OK)
    queryset = Application.objects.filter(user=user).order_by('-timestamp')
    return Response(ApplicationSerializer(queryset, many=True).data, status.HTTP_200_OK)


def can_post_application(user: User, department: str) -> bool:
  if not isinstance(user, User):
    return False
  if user.application_level >= Privilege.COMMITTEE:
    return True
  # Members can only submit applications for their own department.
  return user.department == department


class NewApplicationView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Submit a new application.
  def post(self, request: Request) -> Response:
    user = request.user
    department = request.data.get('department')
    if not can_post_application(user, department):
      self.permission_denied(request)
    serializer = ApplicationSerializer(data={
      'user': user.pk,
      'department': request.data.get('department'),
      'destination': request.data.get('destination'),
      'category': request.data.get('category'),
      'currency': request.data.get('currency'),
      'amount': request.data.get('amount'),
      'reason': request.data.get('reason'),
      'level': user.application_level + 1,
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class ApplicationView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve an application for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    application = get_object_or_404(Application, pk=pk)
    if not has_access_to_application(user, application):
      self.permission_denied(request)
    return Response(DestinationSerializer(application).data, status.HTTP_200_OK)


class EventsView(generics.ListCreateAPIView):
  queryset = Event.objects.all()
  serializer_class = EventSerializer
  permission_classes = [IsAdmin]


def can_post_event(user: User, application: Application, action: int) -> bool:
  if not has_access_to_application(user, application):
    return False
  if action == Action.SUPPORT:
    # Anyone can support any application.
    return True
  elif action == Action.APPROVE or action == Action.REJECT:
    # User can only approve or reject applications exactly one above their approval level.
    if user.approval_level != application.level - 1:
      return False
    # Commitees can only approve or reject applications from their own department.
    return user.approval_level <= Privilege.PRESIDENT or user.department == application.department
  elif action == Action.CREATE or action == Action.CANCEL:
    # User can only create or cancel their own incomplete applications.
    return user == application.user and application.level > Level.COMPLETED
  elif action == Action.COMPLETE:
    # Only admins can issue payments.
    return user.approval_level == Privilege.ADMIN and application.level == Level.ACCEPTED


def result_application_level(user: User, action: int) -> int:
  if action == Action.APPROVE:
    return user.approval_level
  elif action == Action.REJECT:
    return Level.DECLINED
  elif action == Action.CREATE:
    return user.application_level + 1
  elif action == Action.CANCEL:
    return Level.DECLINED
  elif action == Action.COMPLETE:
    return Level.COMPLETED


class ApplicationEventsView(generics.ListCreateAPIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve all events for current user and given application.
  def get(self, request: Request, pk: int) -> Response:
    application = get_object_or_404(Application, pk=pk)
    user = request.user
    if not has_access_to_application(user, application):
      return Response([], status.HTTP_200_OK)
    queryset = Event.objects.filter(user=user, application=application).order_by('-timestamp')
    return Response(EventSerializer(queryset, many=True).data, status.HTTP_200_OK)

  # Submit a new event for an applciation.
  def post(self, request: Request) -> Response:
    user = request.user
    application = get_object_or_404(Application, pk=request.data.get('application'))
    action = request.data.get('action')
    if not can_post_event(user, application, action):
      self.permission_denied(request)
    serializer = ApplicationSerializer(data={
      'user': user.pk,
      'application': application.pk,
      'action': action,
      'contents': request.data.get('contents'),
      'file': request.data.get('file'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # Update application level.
    application.level = result_application_level(user, action)
    application.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class EventView(views.APIView):
  permission_classes = [permissions.AllowAny]

  # Retrieve a message for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    message = get_object_or_404(Event, pk=pk)
    if not has_access_to_application(user, message.application):
      self.permission_denied(request)
    return Response(EventSerializer(message).data, status.HTTP_200_OK)
