from .permissions import *
from main.doc import get_sections


# Handle file uploads from the File model.
def save_files_as_model(user, data):
  key = 0
  files = []
  while f'files[{key}][filename]' in data:
    if f'files[{key}][file]' in data:
      serializer = FileSerializer(data={
        'user': user.pk,
        'file': data[f'files[{key}][file]'],
        'filename': data[f'files[{key}][filename]']
      })
      serializer.is_valid(raise_exception=True)
      files.append(serializer.save().pk)
    key += 1
  return files


class DocumentationView(views.APIView):
  permission_classes = [IsUser]

  # Retrieve the documentation file for current user.
  def get(self, request: Request, section: str) -> Response:
    sections = get_sections()
    if section not in sections:
      return Response({'detail': 'Section not found.'}, status.HTTP_404_NOT_FOUND)
    return Response({'content': sections[section]}, status.HTTP_200_OK)
