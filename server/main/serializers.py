from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import *


class DestinationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Destination
    fields = [
      'pk', 'user', 'name', 'sort_code',
      'account_number', 'business', 'personal', 'last_usage',
    ]
    read_only_fields = ['pk']

class ApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Application
    fields = [
      'pk', 'user', 'department', 'destination',
      'category', 'currency', 'amount', 'reason',
      'level',
    ]
    read_only_fields = ['pk']

class EventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = [
      'pk', 'user', 'application', 'timestamp',
      'action', 'contents', 'file',
    ]
    read_only_fields = ['pk', 'timestamp']
    