from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import MinLengthValidator
from accounts.models import User, Department

# Application category
class Category(models.IntegerChoices):
    REIMBURSEMENT = 0, '报销'
    PAYMENT = 1, '付款'
    ADVANCE = 2, '预支'

# Application approval level
class Level(models.IntegerChoices):
    DECLINED = -1, '已取消'
    COMPLETED = 0, '已完成'
    ACCEPTED = 1, '待付款'
    AWAIT_AUDIT = 2, '待财务审批'
    AWAIT_PRESIDENT = 3, '待主席审批'
    AWAIT_COMMITTEE = 4, '待部门审批'
    AWAIT_MEMBER = 5, '待成员审批'

# Application user action
class Action(models.IntegerChoices):
    SUPPORT = 0, '评论'
    APPROVE = 1, '批准'
    REJECT = 2, '驳回'
    CREATE = 3, '创建'
    CANCEL = 4, '撤销'
    COMPLETE = 5, '完成'

# Payment currency
class Currency(models.IntegerChoices):
    GBP = 0, '英镑'
    CNY = 1, '人民币'

def display_amount(currency_display: str, amount: int) -> str:
    return f'{format(amount/100, ".2f")} {currency_display}'

class Destination(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    sort_code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])
    account_number = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    business = models.BooleanField(default=False)

    public = models.BooleanField(default=True)
    star = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.sort_code} - {self.account_number}'

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    department = models.IntegerField(choices=Department.choices, default=Department.UNDEFINED)
    category = models.IntegerField(choices=Category.choices, default=Category.REIMBURSEMENT)

    name = models.CharField(max_length=100)
    sort_code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])
    account_number = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    business = models.BooleanField(default=False)

    currency = models.IntegerField(choices=Currency.choices, default=Currency.GBP)
    amount = models.IntegerField()
    reason = models.TextField()

    level = models.IntegerField(choices=Level.choices, default=Level.AWAIT_MEMBER)
    
    def __str__(self):
        return f'[{self.get_department_display()}] - {self.user} {self.get_category_display()} {display_amount(self.get_currency_display(), self.amount)}'

def user_directory_path(self: models.Model, filename: str) -> str:
    return 'accounts/user_{0}/{1}'.format(self.user.pk, filename)

def fileSizeValidator(file):
    if file.size > 10 * 1024 * 1024:
        raise ValidationError(f'File size exceeds 10MB limit.')

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.IntegerField(choices=Action.choices, default=Action.SUPPORT)
    contents = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']),
        fileSizeValidator
    ])

    def __str__(self):
        contents = f': "{self.contents[:20]}"' if self.contents else ''
        file = f' [{self.file}]' if self.file else ''
        return f'{self.user} [{self.get_action_display()}] {self.application}{file}{contents}'

def received_json_default():
    return {label: 0 for label in Currency.labels}

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    department = models.IntegerField(choices=Department.choices, default=Department.UNDEFINED)

    currency = models.IntegerField(choices=Currency.choices, default=Currency.GBP)
    amount = models.IntegerField()
    reason = models.TextField()

    received = models.JSONField(default=received_json_default)
    level = models.IntegerField(choices=Level.choices, default=Level.ACCEPTED)

    def __str__(self):
        return f'[{self.get_department_display()}] - {self.reason} {display_amount(self.get_currency_display(), self.amount)}'

class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income = models.ForeignKey(Income, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.IntegerField(choices=Action.choices, default=Action.SUPPORT)
    currency = models.IntegerField(choices=Currency.choices, default=Currency.GBP)
    amount = models.IntegerField()
    contents = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']),
        fileSizeValidator
    ])

    def __str__(self):
        contents = f': "{self.contents[:20]}"' if self.contents else ''
        file = f' [{self.file}]' if self.file else ''
        action = f'+{display_amount(self.get_currency_display(), self.amount)}' if self.amount else self.get_action_display()
        return f'{self.user} [{action}] {self.income}{file}{contents}'