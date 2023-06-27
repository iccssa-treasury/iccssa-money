from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Destination(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    name = models.CharField(max_length=100)
    sort_code = models.CharField(max_length=6)
    account_number = models.CharField(max_length=8)
    business = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.sort_code}'

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)

    class Department(models.IntegerChoices):
        PRESIDENT = 0, '主席团'
        SECRETARY = 1, '秘书处'
        TREASURER = 2, '财务处'
        CAREERS = 3, '事业部'
        MEDIA = 4, '媒体部'
        SPONSORSHIP = 5, '赞助部'
        ARTS = 6, '文艺部'
        CULTURE = 7, '文化部'
        ENTERTAINMENT = 8, '外联部'
        SPORTS = 9, '体育部'
        GENERAL = 10, '未分配'
    department = models.IntegerField(choices=Department.choices, default=Department.GENERAL)

    class Category(models.IntegerChoices):
        REIMBURSEMENT = 0, '报销'
        PAYMENT = 1, '付款'
        ADVANCE = 2, '预支'
    category = models.IntegerField(choices=Category.choices, default=Category.REIMBURSEMENT)

    class Currency(models.IntegerChoices):
        GBP = 0, '英镑'
        CNY = 1, '人民币'
    currency = models.IntegerField(choices=Currency.choices, default=Currency.GBP)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()

    class Level(models.IntegerChoices):
        DECLINED = -1, '已取消'
        ACCEPTED = 0, '已通过'
        AWAIT_ADMIN = 1, '待财务审批'
        AWAIT_PRESIDENT = 2, '待主席审批'
        AWAIT_COMMITTEE = 3, '待部门审批'
        AWAIT_MEMBER = 4, '待成员审批'
    level = models.IntegerField(choices=Level.choices, default=Level.AWAIT_MEMBER)

    def status(self):
        # TODO: Implement this
        return 'Pending'

    def __str__(self):
        return f'[{self.get_department_display()}] - {self.user} {self.get_category_display()} {self.amount} {self.get_currency_display()}'

def user_directory_path(self: models.Model, filename: str) -> str:
  return 'accounts/user_{0}/{1}'.format(self.pk, filename)

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)

    timestamp = models.DateTimeField(auto_now_add=True)
    contents = models.TextField(max_length=20, null=True, blank=True)
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

    def __str__(self):
        return f'{self.user} - "{self.contents[:20]}" [{self.file}]'

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)

    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Action(models.IntegerChoices):
        CREATE = 0, '创建'
        APPROVE = 1, '批准'
        HOLD = 2, '待办'
        REJECT = 3, '驳回'
        CANCEL = 4, '取消'
        COMPLETE = 5, '完成'
    action = models.IntegerField(choices=Action.choices, default=Action.CREATE)

    def __str__(self):
        return f'{self.user} - [{self.get_action_display()}] {self.application}'
