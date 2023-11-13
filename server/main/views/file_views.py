from .permissions import *


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
