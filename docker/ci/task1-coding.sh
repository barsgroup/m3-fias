#!/bin/bash
# Запуск проверки правильности определения кодировки файлов.
source `dirname $BASH_SOURCE`/tasks-config.sh

LOGS_DIR=$LOGS_DIR/coding
if [ ! -d $LOGS_DIR ]; then
    mkdir -p $LOGS_DIR
fi

exec >$LOGS_DIR/out.log 2>&1

fab -f $PROJECT_DIR/fabfile src.coding:check_only=yes

echo $? > $LOGS_DIR/rc
echo '/out.log' > $LOGS_DIR/url
