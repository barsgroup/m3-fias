#!/bin/bash
source `dirname $BASH_SOURCE`/tasks-config.sh

find $PROJECT_DIR -name *.pyc -delete
find $PROJECT_DIR -name __pycache__ -delete
