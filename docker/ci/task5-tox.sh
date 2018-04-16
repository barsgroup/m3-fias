#!/bin/bash
# Запуск тестов.
# -----------------------------------------------------------------------------
source `dirname $BASH_SOURCE`/tasks-config.sh

LOGS_DIR=$LOGS_DIR/tox
if [ ! -d $LOGS_DIR ]; then
    mkdir -p $LOGS_DIR
fi

exec >$LOGS_DIR/out.log 2>&1
# -----------------------------------------------------------------------------
echo 'Запуск тестов...'

cd $PROJECT_DIR

$PYTHON27_DIR/bin/fab req.test

tox --workdir /tmp/tox-work-dir

echo $? > $LOGS_DIR/rc
echo '/' > $LOGS_DIR/url
# -----------------------------------------------------------------------------
