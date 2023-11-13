import logging
from main.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import views, generics, permissions, status

logger = logging.getLogger(__name__)

# API endpoints that implement L-CRUD (list, create, retrieve, update, destory).
# See: https://www.django-rest-framework.org/api-guide/serializers/
# See: https://www.django-rest-framework.org/api-guide/views/
# See: https://www.django-rest-framework.org/api-guide/generic-views/
# See: https://www.django-rest-framework.org/api-guide/viewsets/


# This time we use DRF's abstractions for views (`GenericAPIView`) and permissions (`BasePermission`)
# since the requirement is simple enough (straightforward L-CRUD, staff writable, others readonly).

class IsAdmin(permissions.BasePermission):
  def has_permission(self, request: Request, view: views.APIView):
    return (isinstance(request.user, User) and request.user.admin)

class IsUser(permissions.BasePermission):
  def has_permission(self, request: Request, view: views.APIView):
    return isinstance(request.user, User)


# class IsAdminOrReadOnly(permissions.BasePermission):
#   def has_permission(self, request: Request, view: views.APIView):
#     return (isinstance(request.user, User) and request.user.admin) or request.method in permissions.SAFE_METHODS


# class IsAdminOrPostOnly(permissions.BasePermission):
#   def has_permission(self, request: Request, view: views.APIView):
#     return (isinstance(request.user, User) and request.user.admin) or request.method == 'POST'
