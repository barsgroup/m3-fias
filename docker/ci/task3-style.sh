#!/bin/bash
# Запуск проверки соблюдения правил стилевого оформления кода Python.
source `dirname $BASH_SOURCE`/tasks-config.sh

LOGS_DIR=$LOGS_DIR/style
if [ ! -d $LOGS_DIR ]; then
    mkdir -p $LOGS_DIR
fi

exec >$LOGS_DIR/out.log 2>&1

fab -f $PROJECT_DIR/fabfile src.style

echo $? > $LOGS_DIR/rc
echo '/out.log' > $LOGS_DIR/url
