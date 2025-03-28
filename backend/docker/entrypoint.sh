#!/bin/bash

set -e  # if any command fails, exit

case "${MODE}" in
  worker)
    echo "[INFO] Starting Celery Worker..."
    exec celery -A app.main.celery worker --loglevel info -Q ${CELERY_QUEUES:-mail,workflow}
    ;;

  beat)
    echo "[INFO] Starting Celery Beat..."
    exec celery -A app.main.celery beat --loglevel info
    ;;

  web)
    echo "[INFO] Starting FastAPI..."
    exec python app.py
    ;;

  *)
    echo "[ERROR] Invalid MODE: '${MODE}'. Supported modes are: web, worker, beat."
    exit 1
    ;;
esac
