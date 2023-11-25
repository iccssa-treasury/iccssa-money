from .permissions import *
from accounts.models import Privilege
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser
from .file_views import save_files_as_model
from main.mailer import notify_income_receipt
from main.fx import exchange


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


def update_income_budget(income: Income, currency: int, amount: int, action: int) -> None:
  budget = income.budget
  if budget:
    currency = Currency.labels[currency]
    converted = exchange(amount, currency)  
    if action == Action.SUPPORT and amount > 0:
      budget.received += converted
      budget.received_actual[currency] += amount
    budget.save()


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
      'category': request.data.get('category'),
      'budget': request.data.get('budget'),
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
      'files': save_files_as_model(user, request.data),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # Update budget (does not do anything for now).
    update_income_budget(income, income.currency, income.amount, Action.CREATE)
    # Email notifications.
    notify_income_receipt(serializer.instance)
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


class IncomeFilesView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all files for current user and given income.
  def get(self, request: Request, pk: int) -> Response:
    income = get_object_or_404(Income, pk=pk)
    user = request.user
    if not has_access_to_income(user, income):
      self.permission_denied(request)
    pks = Receipt.objects.filter(income=income).exclude(**{'files': None}).values_list('files', flat=True)
    queryset = File.objects.filter(pk__in=pks)
    return Response(FileSerializer(queryset, many=True).data, status.HTTP_200_OK)


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
    # User can only create or cancel their own incomes without any receipts.
    return user == income.user and all(amount == 0 for amount in income.received.values())
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
      'files': save_files_as_model(user, request.data),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # Update income amount and level.
    if action == Action.SUPPORT:
      income.received[Currency.labels[currency]] += amount
    else:
      income.level = result_income_level(user, action)
    income.save()
    # Update budget.
    update_income_budget(income, currency, amount, action)
    # Email notifications.
    notify_income_receipt(serializer.instance)
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
