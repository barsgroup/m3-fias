Сборка образа
-------------

::

  docker build -t m3-d15n -f docker/ci/Dockerfile .

Создание томов
--------------

* ``barsci-cache``

  Том используется для кешей различных подсистем, например ``pip``.

  ::

    docker volume create barsci-cache

* ``barsci-logs``

  Том будет использоваться для сохранения логов работы заданий в контейнере.
  Структура папок будет следующей:

  <Container ID> --> <Task ID> --> ...

  ::

    docker volume create barsci-logs

Запуск тестов в контейнере
--------------------------

::

  docker run \
    -v barsci-cache:/var/cache \
    -v <path-to-extedu-repo>:/root/project \
    -v barsci-logs:/var/log/barsci \
    -v /var/run/docker.sock:/var/run/docker.sock \
    m3-fias

Перед запуском контейнеров необходимо создать тома ``barsci-cache`` и
``barsci-logs``.
