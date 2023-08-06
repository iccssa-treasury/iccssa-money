#!/bin/bash

cd ~/cssa && \
git stash && \
git pull --rebase && \
git stash pop && \
cd ~/cssa/client && \
npm run build && \
cd ~/cssa/server && \
source ~/env/bin/activate && \
python3 manage.py collectstatic --noinput && \
python3 manage.py migrate && \
deactivate && \
sudo systemctl restart gunicorn && \
cd ~/cssa
