from rest_framework import serializers
from .models import *


class DestinationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Destination
    fields = [
      'pk', 'user', 'name', 'sort_code',
      'account_number', 'business', 'personal', 'last_active',
    ]
    read_only_fields = ['pk']

class ApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Application
    fields = [
      'pk', 'user', 'destination', 'department',
      'category', 'currency', 'amount', 'reason',
      'approval',
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
    