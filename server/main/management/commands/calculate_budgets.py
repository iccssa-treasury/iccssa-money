from django.core.management.base import BaseCommand
from main.models import Budget, Currency, Action, Event, Receipt, received_json_default
from main.fx import exchange

class Command(BaseCommand):
  help = "Reset and calculates all budgets from current applications and incomes."

  def handle(self, *args, **options):
    for budget in Budget.objects.all():
      budget.spent = 0
      budget.spent_actual = received_json_default()
      budget.received = 0
      budget.received_actual = received_json_default()
      budget.save()
    for event in Event.objects.all():
      application = event.application
      budget = application.budget
      if budget:
        action = event.action
        currency = Currency.labels[application.currency]
        amount = application.amount
        converted = exchange(amount, currency, event.timestamp.date())
        if action == Action.CREATE:
          budget.spent += converted
          budget.spent_actual[currency] += amount
        elif action == Action.REJECT or action == Action.CANCEL:
          budget.spent -= converted
          budget.spent_actual[currency] -= amount
        budget.save()
    for receipt in Receipt.objects.all():
      budget = receipt.income.budget
      if budget:
        action = receipt.action
        currency = Currency.labels[receipt.currency]
        amount = receipt.amount
        converted = exchange(amount, currency, receipt.timestamp.date())
        if action == Action.SUPPORT and amount > 0:
          budget.received += converted
          budget.received_actual[currency] += amount
        budget.save()

