Подключение к проекту
*********************

Для подключения приложения к проекту необходимо:

#. Добавить ``'m3_fias'`` в список приложений Django, указанный в
   :django:setting:`INSTALLED_APPS`.
#. Создать класс с конфигурацией ``m3-fias`` и сохранить его экземпляр в
   `m3_fias.config`:

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
                  def observer(self):
                      from extedu.controllers import core_observer
                      return core_observer

              m3_fias.config = Config()

          def ready(self):
              super(AppConfig, self).ready()

              self._init_m3_dev_utils()

#.
