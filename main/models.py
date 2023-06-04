from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    department = models.CharField(max_length=10)
    category = models.CharField(max_length=1)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    reason = models.TextField()
    
    name = models.CharField(max_length=100)
    sort_code = models.CharField(max_length=6)
    account_number = models.CharField(max_length=8)
    account_type = models.CharField(max_length=1)

    def status(self):
        approvals = Approval.objects.filter(application=self)
        if len(approvals) < 2:
            return 'Pending'
        else:
            for approval in approvals:
                if not approval.approval:
                    return 'Rejected'
            return 'Approved'

    def __str__(self):
        return f'{self.department} - {self.amount} {self.currency}'

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    description = models.CharField(max_length=20)
    file = models.FileField(upload_to='uploads/')
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.time} - {self.description}'

class Approval(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    approval = models.BooleanField()
    comment = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.time} - {self.approval}'
