#!/usr/bin/env bash

celery -A api.celery_tasks.tasks:celery worker -l info -B