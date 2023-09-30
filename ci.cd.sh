#!/bin/bash

if [[ "$*" != *"--no-git"* ]]; then
  echo "Updating git repository..."
  cd ~/cssa
  git reset --hard HEAD
  git pull --rebase
  sed -i '6s#http://localhost:8000/#/#' client/src/api.ts
fi

echo "Building client..."
cd ~/cssa/client && \
npm run build && \

echo "Collecting static files..."
cd ~/cssa/server && \
source ~/env/bin/activate && \
python3 manage.py collectstatic --noinput && \

echo "Migrating database..."
python3 manage.py migrate && \
deactivate && \

echo "Restarting gunicorn..." && \
sudo systemctl restart gunicorn && \

cd ~/cssa
echo "All done!"
