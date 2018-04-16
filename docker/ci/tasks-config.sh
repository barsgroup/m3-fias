# -----------------------------------------------------------------------------
# Папка с репозиторием проекта.

PROJECT_DIR=/root/project
# -----------------------------------------------------------------------------
# Папка с логами сборки.

LOGS_DIR=/var/log/barsci/$HOSTNAME

if [ ! -d $LOGS_DIR ]; then
    mkdir -p $LOGS_DIR
fi
# -----------------------------------------------------------------------------

export PYTHON27_DIR=/usr/local/python/2.7
export PYTHON27_BIN=$PYTHON27_DIR/bin/python2.7

export PYTHON36_DIR=/usr/local/python/3.6
export PYTHON36_BIN=$PYTHON36_DIR/bin/python3.6

export PATH=$PYTHON36_DIR/bin:$PYTHON27_DIR/bin:$PATH

export PYTHONPATH=$PROJECT_DIR/src
export FABRIC_DISABLE_COLORS=1
# -----------------------------------------------------------------------------
