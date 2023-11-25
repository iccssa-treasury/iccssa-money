import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

import logging
import threading
from accounts.models import User, Privilege, Notification
from .models import Event, Receipt, Action, display_amount
from django.db.models import Q
from config import settings

# See https://thepythoncode.com/article/use-gmail-api-in-python?utm_content=cmp-true
class MailerService:
  SCOPES = ['https://mail.google.com/']

  def __init__(self):
    self.service = self.gmail_authenticate()

  def gmail_authenticate(self):
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

class Mailer(threading.Thread):
  email = 'iccssa.treasury@gmail.com'

  def __init__(self, service, mails=[]):
    self.service = service
    self.mails = mails
    super(Mailer, self).__init__()
  
  def add(self, mail):
    self.mails.append(mail)

  def run(self):
    self.send_messages()
  
  def send_messages(self):
    for mail in self.mails:
      logger.info(f'Sending mail to {mail.destinations}')
      logger.info(f'Subject: {mail.obj}')
      logger.info(f'Body: {mail.body}')
      if not settings.DEBUG:
        self.service.users().messages().send(
          userId="me",
          body=self.build_message(mail.destinations, mail.obj, mail.body, mail.attachments)
        ).execute()
  
  def build_message(self, destinations, obj, body, attachments=[]):
    if not attachments: # no attachments given
        message = MIMEText(body)
        message['to'] = self.email
        message['bcc'] = ', '.join(destinations)
        message['from'] = self.email
        message['subject'] = obj
    else:
        message = MIMEMultipart()
        message['to'] = self.email
        message['bcc'] = ', '.join(destinations)
        message['from'] = self.email
        message['subject'] = obj
        message.attach(MIMEText(body))
        for filename in attachments:
          self.add_attachment(message, filename)
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

  def add_attachment(self, message, filename):
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(filename, 'rb')
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(filename, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(filename, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

class Mail:
  def __init__(self, destinations, event=None, receipt=None, attachments=[]):
    self.destinations = destinations
    self.obj = self.compose_application_subject(event) if event else self.compose_income_subject(receipt)
    self.body = self.compose_application_body(event) if event else self.compose_income_body(receipt)
    self.attachments = attachments
  
  def add_destination(self, destination):
    self.destinations.append(destination)

  def compose_application_subject(self, event: Event):
    name = event.application.user.name
    category = event.application.get_category_display()
    pk = event.application.pk
    return f'[帝国财务] {name}的{category}申请 #{pk}'
  
  def compose_income_subject(self, receipt: Receipt):
    reason = receipt.income.reason
    pk = receipt.income.pk
    return f'[帝国财务] {reason} #{pk}'

  def compose_application_body(self, event: Event):
    name = event.user.name
    action = event.get_action_display()
    category = event.application.get_category_display()
    suffix = f'：“{event.contents}”' if event.contents else ':'
    url = f'https://iccssa.money/application/{event.application.pk}/'
    return f'{name}{action}了{category}申请{suffix}\n{url}'
  
  def compose_income_body(self, receipt: Receipt):
    name = receipt.user.name
    action = receipt.get_action_display()
    amount = receipt.amount
    reason = f'确认收款{display_amount(receipt.get_currency_display(), amount)}' \
      if amount else f'{action}了收款合同'
    suffix = f'：“{receipt.contents}”' if receipt.contents else ':'
    url = f'https://iccssa.money/income/{receipt.income.pk}/'
    return f'{name}{reason}{suffix}\n{url}'

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
  Mailer(MailerService().service, [Mail(destinations=notified, event=event)]).start()

def notify_income_receipt(receipt: Receipt):
  critical = receipt.action == Action.CREATE or receipt.action == Action.COMPLETE
  notified = set()
  # notify representatives
  representatives = User.objects.filter(representative=True)
  for representative in representatives:
    level = representative.notification_settings.get('income')
    if level == Notification.ALL or (level == Notification.PARTIAL and critical):
      notified.add(representative.email)
  Mailer(MailerService().service, [Mail(destinations=notified, receipt=receipt)]).start()
