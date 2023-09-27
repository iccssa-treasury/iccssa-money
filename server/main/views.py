from datetime import datetime
import logging
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import views, generics, permissions, status
from rest_framework.parsers import MultiPartParser
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

class IsUser(permissions.BasePermission):
  def has_permission(self, request: Request, view: views.APIView):
    return isinstance(request.user, User)


# class IsAdminOrReadOnly(permissions.BasePermission):
#   def has_permission(self, request: Request, view: views.APIView):
#     return (isinstance(request.user, User) and request.user.admin) or request.method in permissions.SAFE_METHODS


# class IsAdminOrPostOnly(permissions.BasePermission):
#   def has_permission(self, request: Request, view: views.APIView):
#     return (isinstance(request.user, User) and request.user.admin) or request.method == 'POST'


class DestinationsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all public destinations.
  def get(self, request: Request) -> Response:
    queryset = Destination.objects.filter(public=True)
    return Response(DestinationSerializer(queryset, many=True).data, status.HTTP_200_OK)


class UserDestinationsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all destinations for current user.
  def get(self, request: Request) -> Response:
    user = request.user
    queryset = Destination.objects.filter(user=user)
    return Response(DestinationSerializer(queryset, many=True).data, status.HTTP_200_OK)

  # Submit a new destination.
  def post(self, request: Request) -> Response:
    user = request.user
    serializer = DestinationSerializer(data={
      'user': user.pk,
      'platform': request.data.get('platform'),
      'name': request.data.get('name'),
      'sort_code': request.data.get('sort_code'),
      'account_number': request.data.get('account_number'),
      'business': request.data.get('business'),
      'card_number': request.data.get('card_number'),
      'bank_name': request.data.get('bank_name'),
      'public': request.data.get('public'),
      'star': request.data.get('star'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class DestinationView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve a destination for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    destination = get_object_or_404(Destination, pk=pk)
    if not destination.public and user != destination.user:
      self.permission_denied(request)
    return Response(DestinationSerializer(destination).data, status.HTTP_200_OK)


def has_access_to_application(user: User, application: Application) -> bool:
  # if not isinstance(user, User):
  #   return False
  # Admins can access all applications.
  if user.approval_level <= Privilege.PRESIDENT:
    return True
  # Commitees can access all applications from their department.
  if user.approval_level == Privilege.COMMITTEE:
    return user.department == application.department or user == application.user
  # Members can only access their own applications.
  return user == application.user


class ApplicationsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all applications that the current user can access.
  def get(self, request: Request) -> Response:
    user = request.user
    pks = [app.pk for app in Application.objects.all() if has_access_to_application(user, app)]
    queryset = Application.objects.filter(pk__in=pks).order_by('-level')
    return Response(ApplicationSerializer(queryset, many=True).data, status.HTTP_200_OK)


class UserApplicationsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all applications created by current user.
  def get(self, request: Request) -> Response:
    user = request.user
    queryset = Application.objects.filter(user=user).order_by('-level')
    return Response(ApplicationSerializer(queryset, many=True).data, status.HTTP_200_OK)


def can_post_application(user: User, department: int) -> bool:
  # if not isinstance(user, User):
  #   return False
  if user.application_level <= Privilege.COMMITTEE:
    return True
  # Members can only submit applications for their own department.
  return user.department == department


class NewApplicationView(views.APIView):
  parser_classes = [MultiPartParser]
  permission_classes = [IsUser]

  # Submit a new application.
  @method_decorator(transaction.atomic)
  def post(self, request: Request) -> Response:
    user = request.user
    department = request.data.get('department')
    if not can_post_application(user, int(department)):
      self.permission_denied(request)
    serializer = ApplicationSerializer(data={
      'user': user.pk,
      'department': department,
      'category': request.data.get('category'),
      'platform': request.data.get('platform'),
      'name': request.data.get('name'),
      'sort_code': request.data.get('sort_code'),
      'account_number': request.data.get('account_number'),
      'business': request.data.get('business'),
      'card_number': request.data.get('card_number'),
      'bank_name': request.data.get('bank_name'),
      'currency': request.data.get('currency'),
      'amount': request.data.get('amount'),
      'reason': request.data.get('reason'),
      'level': user.application_level,
    })
    serializer.is_valid(raise_exception=True)
    application = serializer.save()
    # Post CREATE event.
    serializer = EventSerializer(data={
      'user': user.pk,
      'application': application.pk,
      'action': Action.CREATE,
      'contents': request.data.get('contents'),
      'file': request.data.get('file'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class ApplicationView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve an application for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    application = get_object_or_404(Application, pk=pk)
    if not has_access_to_application(user, application):
      self.permission_denied(request)
    return Response(ApplicationSerializer(application).data, status.HTTP_200_OK)


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
    return user.approval_level == Privilege.AUDIT and application.level == Level.ACCEPTED


def result_application_level(user: User, action: int) -> int:
  if action == Action.APPROVE:
    return user.approval_level
  elif action == Action.REJECT:
    return Level.DECLINED
  elif action == Action.CREATE:
    return user.application_level
  elif action == Action.CANCEL:
    return Level.DECLINED
  elif action == Action.COMPLETE:
    return Level.COMPLETED


class ApplicationEventsView(generics.ListCreateAPIView):
  parser_classes = [MultiPartParser]
  permission_classes = [IsUser]

  # Retrieve all events for current user and given application.
  def get(self, request: Request, pk: int) -> Response:
    application = get_object_or_404(Application, pk=pk)
    user = request.user
    if not has_access_to_application(user, application):
      return Response([], status.HTTP_200_OK)
    queryset = Event.objects.filter(application=application).order_by('-timestamp')
    return Response(EventSerializer(queryset, many=True).data, status.HTTP_200_OK)

  # Submit a new event for an application.
  @method_decorator(transaction.atomic)
  def post(self, request: Request, pk: int) -> Response:
    user = request.user
    application = get_object_or_404(Application, pk=pk)
    action = int(request.data.get('action'))
    if not can_post_event(user, application, action):
      self.permission_denied(request)
    serializer = EventSerializer(data={
      'user': user.pk,
      'application': application.pk,
      'action': action,
      'contents': request.data.get('contents'),
      'file': request.data.get('file'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # Update application level.
    if action > Action.SUPPORT:
      application.level = result_application_level(user, action)
      application.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class EventView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve a message for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    message = get_object_or_404(Event, pk=pk)
    if not has_access_to_application(user, message.application):
      self.permission_denied(request)
    return Response(EventSerializer(message).data, status.HTTP_200_OK)


def has_access_to_income(user: User, income: Income) -> bool:
  # if not isinstance(user, User):
  #   return False
  # Only representatives can access incomes.
  return user.representative or user == income.user


class IncomesView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all incomes that the current user can access.
  def get(self, request: Request) -> Response:
    user = request.user
    pks = [inc.pk for inc in Income.objects.all() if has_access_to_income(user, inc)]
    queryset = Income.objects.filter(pk__in=pks).order_by('-level')
    return Response(IncomeSerializer(queryset, many=True).data, status.HTTP_200_OK)


def can_post_income(user: User) -> bool:
  # if not isinstance(user, User):
  #   return False
  # Only representatives can post incomes.
  return user.representative


class NewIncomeView(views.APIView):
  parser_classes = [MultiPartParser]
  permission_classes = [IsUser]

  # Submit a new income.
  @method_decorator(transaction.atomic)
  def post(self, request: Request) -> Response:
    user = request.user
    if not can_post_income(user):
      self.permission_denied(request)
    serializer = IncomeSerializer(data={
      'user': user.pk,
      'department': request.data.get('department'),
      'currency': request.data.get('currency'),
      'amount': request.data.get('amount'),
      'reason': request.data.get('reason'),
    })
    serializer.is_valid(raise_exception=True)
    income = serializer.save()
    # Post CREATE receipt.
    serializer = ReceiptSerializer(data={
      'user': user.pk,
      'income': income.pk,
      'action': Action.CREATE,
      'currency': request.data.get('currency'),
      'amount': 0,
      'contents': request.data.get('contents'),
      'file': request.data.get('file'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class IncomeView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve an income for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    income = get_object_or_404(Income, pk=pk)
    if not has_access_to_income(user, income):
      self.permission_denied(request)
    return Response(IncomeSerializer(income).data, status.HTTP_200_OK)


class ReceiptsView(generics.ListCreateAPIView):
  queryset = Receipt.objects.all()
  serializer_class = ReceiptSerializer
  permission_classes = [IsAdmin]


def can_post_receipt(user: User, income: Income, action: int, amount: int) -> bool:
  if not has_access_to_income(user, income):
    return False
  if action == Action.SUPPORT:
    # Only admins can receive payments.
    if amount > 0:
      return user.approval_level == Privilege.AUDIT and income.level > Level.COMPLETED
    # Anyone can support any income.
    return True
  elif amount > 0:
    # Payments can only be received through SUPPORT action.
    return False
  elif action == Action.APPROVE or action == Action.REJECT:
    # Not yet implemented.
    return False
  elif action == Action.CREATE or action == Action.CANCEL:
    # User can only create or cancel their own incomplete incomes.
    return user == income.user and income.level > Level.COMPLETED
  elif action == Action.COMPLETE:
    # Only admins can receive full payments.
    return user.approval_level == Privilege.AUDIT and income.level == Level.ACCEPTED


def result_income_level(user: User, action: int) -> int:
  if action == Action.APPROVE:
    return Level.ACCEPTED
  elif action == Action.REJECT:
    return Level.DECLINED
  elif action == Action.CREATE:
    return Level.ACCEPTED
  elif action == Action.CANCEL:
    return Level.DECLINED
  elif action == Action.COMPLETE:
    return Level.COMPLETED


class IncomeReceiptsView(generics.ListCreateAPIView):
  parser_classes = [MultiPartParser]
  permission_classes = [IsUser]

  # Retrieve all receipts for current user and given income.
  def get(self, request: Request, pk: int) -> Response:
    income = get_object_or_404(Income, pk=pk)
    user = request.user
    if not has_access_to_income(user, income):
      return Response([], status.HTTP_200_OK)
    queryset = Receipt.objects.filter(income=income).order_by('-timestamp')
    return Response(ReceiptSerializer(queryset, many=True).data, status.HTTP_200_OK)

  # Submit a new receipt for an income.
  @method_decorator(transaction.atomic)
  def post(self, request: Request, pk: int) -> Response:
    user = request.user
    income = get_object_or_404(Income, pk=pk)
    action = int(request.data.get('action'))
    currency = int(request.data.get('currency'))
    amount = int(request.data.get('amount'))
    if not can_post_receipt(user, income, action, amount):
      self.permission_denied(request)
    serializer = ReceiptSerializer(data={
      'user': user.pk,
      'income': income.pk,
      'action': action,
      'currency': currency,
      'amount': amount,
      'contents': request.data.get('contents'),
      'file': request.data.get('file'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # Update income amount and level.
    if action == Action.SUPPORT:
      income.received[Currency.labels[currency]] += amount
    else:
      income.level = result_income_level(user, action)
    income.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class ReceiptView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve a message for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    message = get_object_or_404(Receipt, pk=pk)
    if not has_access_to_income(user, message.income):
      self.permission_denied(request)
    return Response(ReceiptSerializer(message).data, status.HTTP_200_OK)
