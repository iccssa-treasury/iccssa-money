from rest_framework import serializers
from .models import *


class DestinationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Destination
    fields = [
      'pk', 'user', 'name', 'sort_code',
      'account_number', 'business', 'active',
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

class MessageSerializer(serializers.ModelSerializer):
  class Meta:
    model = Message
    fields = [
      'pk', 'user', 'application', 'timestamp',
      'contents', 'file',
    ]
    read_only_fields = ['pk', 'timestamp']

class EventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = [
      'pk', 'user', 'application', 'timestamp',
      'action',
    ]
    read_only_fields = ['pk', 'timestamp']
    