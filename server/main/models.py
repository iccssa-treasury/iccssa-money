from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Department

User = get_user_model()

# Application category
class Category(models.IntegerChoices):
    REIMBURSEMENT = 0, '报销'
    PAYMENT = 1, '付款'
    ADVANCE = 2, '预支'

# Application approval level
class Level(models.IntegerChoices):
        DECLINED = -1, '已取消'
        ACCEPTED = 0, '已通过'
        AWAIT_ADMIN = 1, '待财务审批'
        AWAIT_PRESIDENT = 2, '待主席审批'
        AWAIT_COMMITTEE = 3, '待部门审批'
        AWAIT_MEMBER = 4, '待成员审批'

# Application user action
class Action(models.IntegerChoices):
    SUPPORT = 0, '备注'
    APPROVE = 1, '批准'
    REJECT = 2, '驳回'
    CREATE = 3, '创建'
    CANCEL = 4, '撤销'
    COMPLETE = 5, '完成'

# Payment currency
class Currency(models.IntegerChoices):
    GBP = 0, '英镑'
    CNY = 1, '人民币'

class Destination(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    name = models.CharField(max_length=100)
    sort_code = models.CharField(max_length=6)
    account_number = models.CharField(max_length=8)

    personal = models.BooleanField(default=False)
    business = models.BooleanField(default=False)
    
    last_usage = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.sort_code}'

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)

    department = models.IntegerField(choices=Department.choices, default=Department.GENERAL)
    category = models.IntegerField(choices=Category.choices, default=Category.REIMBURSEMENT)

    currency = models.IntegerField(choices=Currency.choices, default=Currency.GBP)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()

    level = models.IntegerField(choices=Level.choices, default=Level.AWAIT_MEMBER)

    def status(self):
        # TODO: Implement this
        return 'Pending'

    def __str__(self):
        return f'[{self.get_department_display()}] - {self.user} {self.get_category_display()} {self.amount} {self.get_currency_display()}'

def user_directory_path(self: models.Model, filename: str) -> str:
  return 'accounts/user_{0}/{1}'.format(self.pk, filename)

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)

    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.IntegerField(choices=Action.choices, default=Action.SUPPORT)
    contents = models.TextField(max_length=20, null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    def __str__(self):
        contents = f': "{self.contents[:20]}"' if self.contents else ''
        file = f' [{self.file}]' if self.file else ''
        return f'{self.user} [{self.get_action_display()}] {self.application}{file}{contents}'
