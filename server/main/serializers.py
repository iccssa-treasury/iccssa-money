from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import *


class FileSerializer(serializers.ModelSerializer):
  class Meta:
    model = File
    fields = ['pk', 'user', 'file', 'filename']
    read_only_fields = ['pk']

class DestinationValidator:
  def __call__(self, attrs):
    platform = attrs['platform']
    if platform == Platform.BANK_GBP:
      if not attrs['sort_code']:
        raise ValidationError({'sort_code': 'This field is required.'})
      if not attrs['account_number']:
        raise ValidationError({'account_number': 'This field is required.'})
    else:
      if not attrs['card_number']:
        raise ValidationError({'card_number': 'This field is required.'})
      if platform == Platform.BANK_CNY:
        if not attrs['bank_name']:
          raise ValidationError({'bank_name': 'This field is required.'})

class DestinationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Destination
    fields = [
      'pk', 'user', 'platform', 'name', 
      'sort_code', 'account_number', 'business', 
      'card_number', 'bank_name',
      'public', 'star',
    ]
    read_only_fields = ['pk']

  def validate(self, attrs):
    DestinationValidator()(attrs)
    return attrs

class BudgetBasicSerializer(serializers.ModelSerializer):
  class Meta:
    model = Budget
    fields = [
      'pk', 'user', 'department', 'level', 'reason', 'amount', 'spent',
    ]
    read_only_fields = [
      'pk', 'user', 'department', 'level', 'reason', 'amount', 'spent',
    ]

class BudgetManagerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Budget
    fields = [
      'pk', 'user', 'department', 'level', 'reason', 'description',
      'plan', 'amount', 'profit', 'spent', 'spent_actual',
      'received', 'received_actual',
    ]
    read_only_fields = ['pk']

class ApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Application
    fields = [
      'pk', 'user', 'department', 'category', 'budget', 'platform', 
      'name', 'sort_code', 'account_number', 'business',
      'card_number', 'bank_name', 'currency', 
      'amount', 'reason', 'level',
    ]
    read_only_fields = ['pk']

  def validate(self, attrs):
    DestinationValidator()(attrs)
    return attrs

class EventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = [
      'pk', 'user', 'application', 'timestamp',
      'action', 'contents', 'files',
    ]
    read_only_fields = ['pk', 'timestamp']

class IncomeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Income
    fields = [
      'pk', 'user', 'department', 'category', 
      'budget', 'currency', 'amount', 'reason',
      'received', 'level',
    ]
    read_only_fields = ['pk']

class ReceiptSerializer(serializers.ModelSerializer):
  class Meta:
    model = Receipt
    fields = [
      'pk', 'user', 'income', 'timestamp',
      'currency', 'amount', 
      'action', 'contents', 'files',
    ]
    read_only_fields = ['pk', 'timestamp']
