from .permissions import *

class DestinationsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all public destinations.
  def get(self, request: Request) -> Response:
    queryset = Destination.objects.filter(public=True)
    return Response(DestinationSerializer(queryset, many=True).data, status.HTTP_200_OK)


class UserDestinationsView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve all destinations for current user.
  def get(self, request: Request) -> Response:
    user = request.user
    queryset = Destination.objects.filter(user=user)
    return Response(DestinationSerializer(queryset, many=True).data, status.HTTP_200_OK)

  # Submit a new destination.
  def post(self, request: Request) -> Response:
    user = request.user
    serializer = DestinationSerializer(data={
      'user': user.pk,
      'platform': request.data.get('platform'),
      'name': request.data.get('name'),
      'sort_code': request.data.get('sort_code'),
      'account_number': request.data.get('account_number'),
      'business': request.data.get('business'),
      'card_number': request.data.get('card_number'),
      'bank_name': request.data.get('bank_name'),
      'public': request.data.get('public'),
      'star': request.data.get('star'),
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status.HTTP_201_CREATED)


class DestinationView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve a destination for current user.
  def get(self, request: Request, pk: int) -> Response:
    user = request.user
    destination = get_object_or_404(Destination, pk=pk)
    if not destination.public and user != destination.user:
      self.permission_denied(request)
    return Response(DestinationSerializer(destination).data, status.HTTP_200_OK)
