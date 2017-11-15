Подключение к проекту
*********************

Для подключения приложения к проекту необходимо:

#. Добавить ``'m3_fias'`` в список приложений Django, указанный в
   :django:setting:`INSTALLED_APPS`:

   .. code-block:: python

      INSTALLED_APPS = [
          ...,
          'm3_fias',
          ...,
      ]

#. Добавить в конфигурацию проекта (``settings.py``) параметры ``m3-fias``:

   .. code-block:: python

      FIAS = {
          'BACKEND': 'backend package',
      }

   В параметре ``BACKEND`` должно быть указано полное имя пакета, содержащего
   используемый бэкенд. В ``m3-fias`` реализованы следующие бэкенды:

     * ``'m3_fias.backends.django_rest_fias.proxy'``.

   В зависимости от используемого бэкенда может понадобится указать
   дополнительные параметры ``m3-fias``.

#. Создать класс с конфигурацией ``m3-fias`` и сохранить его экземпляр в
   `m3_fias.config`.

   Например, для бэкенда ``'m3_fias.backends.django_rest_fias.proxy'`` класс
   конфигурации может выглядеть так:

   .. code-block:: python

      from django import apps

      class AppConfig(apps.AppConfig):

          def _init_m3_fias(self):
              import m3_fias

              class Config(m3_fias.Config):

                  @cached_property
                  def controller(self):
                      from extedu.controllers import main_controller
                      return main_controller

                  @cached_property
                  def backend(self):
                      backend_class = import_module(
                          settings.FIAS['BACKEND']
                      ).Backend
                      return backend_class()

              m3_fias.config = Config()

          def ready(self):
              super(AppConfig, self).ready()

              self._init_m3_dev_utils()

   Здесь помимо атрибута

#.
