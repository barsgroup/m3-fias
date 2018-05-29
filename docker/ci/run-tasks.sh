#!/bin/bash
set +x
# -----------------------------------------------------------------------------
# Настройка pip.

if [ ! -d ~/.pip ]; then
mkdir ~/.pip
cat > ~/.pip/pip.conf <<FILE_CONTENT
[global]
extra-index-url = https://pypi.bars-open.ru/simple
cache-dir = /var/cache/pip
FILE_CONTENT
fi
# -----------------------------------------------------------------------------

SCRIPT_DIR=`dirname $BASH_SOURCE`

# Подготовка к запуску проверок.
nice -n 19 /bin/bash $SCRIPT_DIR/task0-prepare.sh

# Параллельный запуск проверок.
nice -n 19 /bin/bash $SCRIPT_DIR/task1-coding.sh &
nice -n 19 /bin/bash $SCRIPT_DIR/task2-isort.sh &
nice -n 19 /bin/bash $SCRIPT_DIR/task3-style.sh &
nice -n 19 /bin/bash $SCRIPT_DIR/task4-pylint.sh &
nice -n 19 /bin/bash $SCRIPT_DIR/task5-tox.sh &
# nice -n 19 /bin/bash $SCRIPT_DIR/task6-doc.sh &

# Ожидание завершения всех проверок.
for pid in `jobs -p`; do
    wait $pid
done

nice -n 19 /bin/bash $SCRIPT_DIR/task-done.sh
# -----------------------------------------------------------------------------
