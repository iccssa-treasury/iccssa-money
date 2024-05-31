from django.core.management.base import BaseCommand
from main.models import *
import xlsxwriter

class Command(BaseCommand):
  help = "Writes all data to a xlsx file."

  def handle(self, *args, **options):
    Writer('data.xlsx').write()


class Writer:
  def __init__(self, filename):
    self.workbook = xlsxwriter.Workbook(filename)
    self.main = self.workbook.add_worksheet('汇总表')
    # self.budgets = self.workbook.add_worksheet('活动预算')
    self.applications = self.workbook.add_worksheet('支出记录')
    self.incomes = self.workbook.add_worksheet('收入记录')
  
  def write(self):
    # self.write_budgets()
    self.write_applications()
    self.write_incomes()
    self.write_main()
    self.workbook.close()

  def write_applications(self):
    headers = [
      '序号', '类目', '申请人', '部门', '预算案', '事由', '金额(£)', '金额(¥)', '转账方式', '账户', '状态', '创建时间', '完成时间'
    ]
    self.applications.write_row(0, 0, headers, self.workbook.add_format({'bold': True}))

    pk_row_map = {}
    for i, application in enumerate(Application.objects.all()):
      row = [
        application.pk,
        Category(application.category).label,
        application.user.name,
        Department(application.budget.department).label,
        application.budget.reason,
        application.reason,
        application.amount / 100 if application.currency == Currency.GBP else "",
        application.amount / 100 if application.currency == Currency.CNY else "",
        Platform(application.platform).label,
        f'{application.name} - ' + (f'{application.sort_code} - {application.account_number}' if application.platform == Platform.BANK_GBP else f'{application.card_number}{f" [{application.bank_name}]" if application.platform == Platform.BANK_CNY else ""}'),
        Level(application.level).label,
      ]
      self.applications.write_row(i + 1, 0, row)
      if application.level != Level.COMPLETED:
        self.applications.set_row(i + 1, options={'hidden': True})
      pk_row_map[application.pk] = i + 1

    for event in Event.objects.all():
      if event.action == Action.CREATE:
        self.applications.write(pk_row_map[event.application.pk], 11, event.timestamp.strftime('%Y-%m-%d'))
      elif event.action == Action.COMPLETE:
        self.applications.write(pk_row_map[event.application.pk], 12, event.timestamp.strftime('%Y-%m-%d'))
    
    self.applications.autofilter(0, 0, Application.objects.count(), len(headers) - 1)
    self.applications.filter_column_list('K', ['已完成'])

  def write_incomes(self):
    headers = [
      '序号', '类目', '负责人', '部门', '预算案', '事由', '应收金额', '实收金额(£)', '实收金额(¥)', '状态', '创建时间', '完成时间'
    ]
    self.incomes.write_row(0, 0, headers, self.workbook.add_format({'bold': True}))

    pk_row_map = {}
    for i, income in enumerate(Income.objects.all()):
      row = [
        income.pk,
        Source(income.category).label,
        income.user.name,
        Department(income.budget.department).label,
        income.budget.reason,
        income.reason,
        f"{'£' if income.currency == Currency.GBP else '¥'}{income.amount / 100}",
        income.received['英镑'] / 100 if income.received['英镑'] else "",
        income.received['人民币'] / 100 if income.received['人民币'] else "",
        Level(income.level).label,
      ]
      self.incomes.write_row(i + 1, 0, row)
      if income.level != Level.COMPLETED and income.level != Level.ACCEPTED:
        self.incomes.set_row(i + 1, options={'hidden': True})
      pk_row_map[income.pk] = i + 1
    
    for receipt in Receipt.objects.all():
      if receipt.action == Action.CREATE:
        self.incomes.write(pk_row_map[receipt.income.pk], 10, receipt.timestamp.strftime('%Y-%m-%d'))
      elif receipt.action == Action.COMPLETE:
        self.incomes.write(pk_row_map[receipt.income.pk], 11, receipt.timestamp.strftime('%Y-%m-%d'))
    
    self.incomes.autofilter(0, 0, Income.objects.count(), len(headers) - 1)
    self.incomes.filter_column_list('J', ['已完成', '待付款'])

  def write_main(self):
    col_headers = ['', '金额(£)', '金额(¥)']
    self.main.write_row(0, 0, col_headers, self.workbook.add_format({'bold': True}))
    self.main.write_row(1, 0, [
      '总支出',
      f'=-SUMIF({self.applications.name}!K:K, "已完成", {self.applications.name}!G:G)',
      f'=-SUMIF({self.applications.name}!K:K, "已完成", {self.applications.name}!H:H)',
    ])
    self.main.write_row(2, 0, [
      '总收入',
      f'=SUM({self.incomes.name}!H:H)',
      f'=SUM({self.incomes.name}!I:I)',
    ])
    self.main.write_row(3, 0, [
      '净资产',
      '=B2+B3',
      '=C2+C3',
    ])
