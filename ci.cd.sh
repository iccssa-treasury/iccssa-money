#!/bin/bash

path="$HOME/cssa/"
vars="cssa_vars"
service="gunicorn"
run_git=false

for arg in "$@"; do
  case $arg in
    --dev)
      path="$HOME/dev/"
      vars="dev_vars"
      service="gunicorn_dev"
      ;;
    --git)
      run_git=true
      ;;
    *)
      ;;
  esac
done

if [ "$run_git" = true ]; then
  echo "Updating git repository..."
  cd $path && \
  git reset --hard HEAD
  git pull --rebase
  sed -i '6s#http://localhost:8000/#/#' client/src/api.ts
fi

echo "Building client..."
cd ${path}client/ && \
npm run build && \

echo "Collecting static files..."
cd ${path}server/ && \
source ~/env/bin/activate && \
source ~/env/bin/${vars} && \
python3 manage.py collectstatic --noinput && \

echo "Migrating database..."
python3 manage.py migrate && \
deactivate && \

echo "Restarting $service..." && \
sudo systemctl restart $service && \

cd $path && \
echo "All done!"
