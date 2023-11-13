from .permissions import *
from accounts.models import Privilege
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser
from .file_views import save_files_as_model
from main.mailer import notify_application_event
from main.fx import exchange


def has_access_to_application(user: User, application: Application) -> bool:
  # if not isinstance(user, User):
  #   return False
  # Admins can access all applications.
  if user.approval_level <= Privilege.PRESIDENT:
    return True
  # Commitees can access all applications from their department.
  if user.approval_level == Privilege.COMMITTEE:
    return user.department == application.user.department or user.department == application.department
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
  # Only members can post applications.
  return user.application_level <= Privilege.MEMBER


def update_application_budget(application: Application, action: int) -> None:
  budget = application.budget
  if budget:
    currency = Currency.labels[application.currency]
    amount = application.amount
    converted = exchange(amount, currency)
    if action == Action.CREATE:
      budget.spent += converted
      budget.spent_actual[currency] += amount
    elif action == Action.REJECT or action == Action.CANCEL:
      budget.spent -= converted
      budget.spent_actual[currency] -= amount
    budget.save()


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
      'budget': request.data.get('budget'),
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
      'files': save_files_as_model(user, request.data),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # Update budget.
    update_application_budget(application, Action.CREATE)
    # Email notifications.
    notify_application_event(serializer.instance, user.application_level)
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


class ApplicationFilesView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all files for current user and given application.
  def get(self, request: Request, pk: int) -> Response:
    application = get_object_or_404(Application, pk=pk)
    user = request.user
    if not has_access_to_application(user, application):
      self.permission_denied(request)
    pks = Event.objects.filter(application=application).exclude(**{'files': None}).values_list('files', flat=True)
    queryset = File.objects.filter(pk__in=pks)
    return Response(FileSerializer(queryset, many=True).data, status.HTTP_200_OK)
  

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
      'files': save_files_as_model(user, request.data)
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # Update application level.
    if action > Action.SUPPORT:
      application.level = result_application_level(user, action)
      application.save()
    # Update budget.
    update_application_budget(application, action)
    # Email notifications.
    notify_application_event(serializer.instance, application.level)
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
