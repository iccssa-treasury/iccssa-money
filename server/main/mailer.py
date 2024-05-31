import logging
import threading
import mailtrap as mt
from accounts.models import User, Privilege, Notification
from .models import Event, Receipt, Action, display_amount
from django.db.models import Q
from config import settings

class Mailer(threading.Thread):
  primary = "iccssa.treasury@gmail.com"
  sender = "treasurer@iccssa.money"

  def __init__(self, mails=[]):
    self.mails = mails
    super(Mailer, self).__init__()
  
  def add(self, mail):
    self.mails.append(mail)

  def run(self):
    self.send_messages()
  
  def send_messages(self):
    client = mt.MailtrapClient(token=settings.MAIL_API_KEY)
    for mail in self.mails:
      bcc = mail.destinations
      client.send(mail.compose(sender=self.sender, to=self.primary, bcc=bcc))
      logger.info(f'Mail sent to {mail.destinations}')

class Mail:
  def __init__(self, destinations, event=None, receipt=None):
    self.destinations = destinations
    self.template = self.compose_application_template(event) if event else self.compose_income_template(receipt)

  def level_status(self, level):
    return 'negative' if level == -1 else 'positive' if level == 0 else 'warning'
  
  def level_icon(self, level):
    return 'times' if level == -1 else 'check' if level == 0 else 'comment dollar' if level == 1 else 'clock'

  def compose(self, sender, to, bcc):
    return mt.MailFromTemplate(
      sender=mt.Address(email=sender, name="ICCSSA Treasurer"),
      to=[mt.Address(email=to)],
      bcc=[mt.Address(email=email) for email in bcc],
      template_uuid=settings.MAIL_TEMPLATE_UUID,
      template_variables=self.template
    )

  def compose_application_template(self, event: Event):
    name = event.application.user.name
    category = event.application.get_category_display()
    action = "" if event.action == Action.SUPPORT else f'{event.get_action_display()}了{category}申请'
    return {
      "Title": f'{name}的{category}申请',
      "Pk": event.application.pk,
      "Name": event.user.name,
      "Action": action,
      "Date": event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
      "Contents": event.contents,
      "Url": f'https://iccssa.money/application/{event.application.pk}/',
      "Department": event.application.budget.get_department_display(),
      "Field": "申请事由",
      "Reason": event.application.reason,
      "Status_type": self.level_status(event.application.level),
      "Status_Icon": self.level_icon(event.application.level),
      "Status_Message": event.application.get_level_display()
    }

  def compose_income_template(self, receipt: Receipt):
    action = "" if receipt.amount == 0 and receipt.action == Action.SUPPORT else \
      f'确认收款 {display_amount(receipt.get_currency_display(), receipt.amount)}' \
        if receipt.amount else f'{receipt.get_action_display()}了收款合同'
    return {
      "Title": receipt.income.reason,
      "Pk": receipt.income.pk,
      "Name": receipt.user.name,
      "Action": action,
      "Date": receipt.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
      "Contents": receipt.contents,
      "Url": f'https://iccssa.money/income/{receipt.income.pk}/',
      "Department": receipt.income.budget.get_department_display(),
      "Field": "负责人",
      "Reason": receipt.income.user.name,
      "Status_type": self.level_status(receipt.income.level),
      "Status_Icon": self.level_icon(receipt.income.level),
      "Status_Message": receipt.income.get_level_display()
    }

logger = logging.getLogger(__name__)

def notify_application_event(event: Event, application_level: int):
  critical = event.action == Action.REJECT or event.action == Action.COMPLETE
  application = event.application
  notified = set()
  # notify owner
  owner = application.user
  level = owner.notification_settings.get('application')
  if level == Notification.ALL or (level == Notification.PARTIAL and critical):
    notified.add(owner.email)
  # notify approvers
  level_access = Q(approval_level=application_level-1)
  department_access = Q(department=application.budget.department) | Q(approval_level__lte=Privilege.PRESIDENT)
  approvers = User.objects.filter(level_access & department_access)
  for approver in approvers:
    if approver.notification_settings.get('approval') and approver not in notified:
      notified.add(approver.email)
  # notify watchers
  watchers = {event.user for event in Event.objects.filter(application=application)}
  for watcher in watchers:
    if watcher.notification_settings.get('approval') == Notification.ALL and watcher not in notified:
      notified.add(watcher.email)
  Mailer([Mail(destinations=notified, event=event)]).start()

def notify_income_receipt(receipt: Receipt):
  critical = receipt.action == Action.CREATE or receipt.action == Action.COMPLETE
  notified = set()
  # notify representatives
  representatives = User.objects.filter(representative=True)
  for representative in representatives:
    level = representative.notification_settings.get('income')
    if level == Notification.ALL or (level == Notification.PARTIAL and critical):
      notified.add(representative.email)
  Mailer([Mail(destinations=notified, receipt=receipt)]).start()
