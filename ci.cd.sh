#!/bin/bash

if [[ "$*" != *"--no-git"* ]]; then
  echo "Updating git repository..."
  cd ~/cssa
  git stash
  git pull --rebase
  git stash pop
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
