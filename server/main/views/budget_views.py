from .permissions import *
from accounts.models import Privilege


def has_access_to_budget(user: User, budget: Budget) -> bool:
  # Budgeteers can access all budgets.
  if user.budgeteer:
    return True
  # Commitees can access all budgets from their department.
  if user.approval_level <= Privilege.COMMITTEE:
    return user.department == budget.department or user == budget.user
  # Members cannot access budgets.
  return False


class BudgetsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all budgets that the current user can access.
  def get(self, request: Request) -> Response:
    queryset = Budget.objects.all().order_by('department')
    return Response(BudgetBasicSerializer(queryset, many=True).data, status.HTTP_200_OK)


class BudgetView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve a budget for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    budget = get_object_or_404(Budget, pk=pk)
    if not has_access_to_budget(user, budget):
      self.permission_denied(request)
    return Response(BudgetManagerSerializer(budget).data, status.HTTP_200_OK)
  

class BudgetPlanView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve the budget plan file for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    budget = get_object_or_404(Budget, pk=pk)
    if not has_access_to_budget(user, budget) or not budget.plan:
      self.permission_denied(request)
    return Response(FileSerializer(budget.plan).data, status.HTTP_200_OK)
  

class BudgetApplicationsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all applications for given budget.
  def get(self, request: Request, pk: int) -> Response:
    budget = get_object_or_404(Budget, pk=pk)
    user = request.user
    if not has_access_to_budget(user, budget):
      return Response([], status.HTTP_200_OK)
    queryset = Application.objects.filter(budget=budget).order_by('-level')
    return Response(ApplicationSerializer(queryset, many=True).data, status.HTTP_200_OK)


class BudgetIncomesView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all incomes for given budget.
  def get(self, request: Request, pk: int) -> Response:
    budget = get_object_or_404(Budget, pk=pk)
    user = request.user
    if not has_access_to_budget(user, budget):
      return Response([], status.HTTP_200_OK)
    queryset = Income.objects.filter(budget=budget).order_by('-level')
    return Response(IncomeSerializer(queryset, many=True).data, status.HTTP_200_OK)
