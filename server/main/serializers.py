from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import *


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

class ApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Application
    fields = [
      'pk', 'user', 'department', 'category', 'platform', 
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
      'action', 'contents', 'file',
    ]
    read_only_fields = ['pk', 'timestamp']

class IncomeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Income
    fields = [
      'pk', 'user', 'department',
      'currency', 'amount', 'reason',
      'received', 'level',
    ]
    read_only_fields = ['pk']

class ReceiptSerializer(serializers.ModelSerializer):
  class Meta:
    model = Receipt
    fields = [
      'pk', 'user', 'income', 'timestamp',
      'currency', 'amount', 
      'action', 'contents', 'file',
    ]
    read_only_fields = ['pk', 'timestamp']
