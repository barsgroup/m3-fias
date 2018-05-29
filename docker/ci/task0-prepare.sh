#!/bin/bash
source `dirname $BASH_SOURCE`/tasks-config.sh

LOGS_DIR=$LOGS_DIR/prepare
if [ ! -d $LOGS_DIR ]; then
    mkdir -p $LOGS_DIR
fi

exec >$LOGS_DIR/out.log 2>&1
# -----------------------------------------------------------------------------
echo 'Установка зависимостей проекта...'

cd $PROJECT_DIR

$PYTHON27_DIR/bin/fab req.dev
$PYTHON36_DIR/bin/fab req.dev
# -----------------------------------------------------------------------------
echo 'Создание папок...'

if [ ! -d $LOGS_DIR ]; then
    mkdir -p $LOGS_DIR
fi

WORK_DIR=/tmp/m3-d15n
if [ ! -d $WORK_DIR ]; then
    mkdir $WORK_DIR
fi
if [ ! -d $LOGS_DIR/app/logs ]; then
    mkdir -p $LOGS_DIR/app/logs
    ln -s $LOGS_DIR/app/logs $WORK_DIR/logs
fi
if [ ! -d $WORK_DIR/static ]; then
    mkdir -p $WORK_DIR/static
fi
if [ ! -d $WORK_DIR/media ]; then
    mkdir -p $WORK_DIR/media
fi
# -----------------------------------------------------------------------------

echo $? > $LOGS_DIR/rc
echo '/out.log' > $LOGS_DIR/url
