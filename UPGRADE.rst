Инструкции по обновлению пакета
-------------------------------

0.2 → 1.0
+++++++++

#. В HTML-коде заменить подключение JavaScript-кода с

   .. code-block:: html

      <script src="{{ STATIC_URL }}m3-fias/ext-fields/ext-fias-addrfield.js"></script>

   на

   .. code-block:: html

      <script src="{{ STATIC_URL }}m3/js/fias/AddressPanel.js"></script>

#. Заменить вызовы ``FiasAddressObject.create`` на ``get_address_object``.

#. Обращение к атрибуту ``address`` экземпляров ``FiasAddressObject`` заменить
   на вызов функции ``get_full_name``.

#. Заменить имена атрибутов ``FiasAddressObject`` в соответствии с картой,
   приведенной в ``AddressObjectMapper.fields_map`` (находится в модуле
   ``m3_fias.backends.django_rest_fias.proxy.utils``). Ключ словаря --
   старое имя атрибута, значение ключа -- новое имя.

#. Заменить константы ``FiasAddressObject.LEVEL_*`` на соответствующие из
   ``m3_fias.constants``:

   ================================  ==========================================
   Константа в m3-fias 0.2.x         Константа в m3-fias 1.0.x
   --------------------------------  ------------------------------------------
   ``LEVEL_REGION``                  ``FIAS_LEVEL_REGION``
   ``LEVEL_AUTONOMOUS_DISTRICT``     ``FIAS_LEVEL_AUTONOMUOS_DISTRICT``
   ``LEVEL_DISTRICT``                ``FIAS_LEVEL_DISTRICT``
   ``LEVEL_CITY``                    ``FIAS_LEVEL_CITY``
   ``LEVEL_CITY_TERRITORY``          ``FIAS_LEVEL_INTRACITY_TERRITORY``
   ``LEVEL_PLACE``                   ``FIAS_LEVEL_SETTLEMENT``
   ``LEVEL_STREET``                  ``FIAS_LEVEL_STREET``
   ``LEVEL_ADDITIONAL_TERRITORY``    ``FIAS_LEVEL_ADDITIONAL_TERRITORY``
   ``LEVEL_AT_SUBORDINATED_OBJECT``  ``FIAS_LEVEL_ADDITIONAL_TERRITORY_OBJECT``
   ================================  ==========================================

#. Заменить ``m3_fias.addrfield.ExtFiasAddrComponent`` на
   ``m3_fias.ui.RowsAddressView`` с экземпляром ``m3_fias.ui.AddressFields``.

#. Если в клиентском коде осуществлялась работа с компонентом
   ``Ext.fias.AddrField``, то следует учесть следующие изменения:

   - атрибуты, хранящие адресные поля, переименованы в соответствии с таблицей:

     ==============  =============================================================
     ``place``       ``placeNameField`` (название населенного пункта) и
                     ``placeGUIDField`` (GUID населенного пункта)
     ``zipcode``     ``zipCodeField``
     ``street``      ``streetNameField`` (название улицы) и ``streetGUIDField``
                     (GUID улицы)
     ``house``       ``houseNumberField``
     ``house_guid``  ``houseGUIDField``
     ``corps``       ``buildingNumberField``
     нет аналога     ``structureNumberField``
     ``flat``        ``flatNumberField``
     ``addr``        ``fullAddressField``
     ==============  =============================================================

   - также, как и ранее, наличие тех или иных полей определяется значением
     атрибута ``level``, но поле ``fullAddressField`` присутствует в контейнере
     только если значение атрибута ``withFullAddress`` истинно.

   - атрибут ``can_edit_addr`` отсутствует, а его функционал (возможность
     редактирования полного адреса) в т.ч. определяется значением атрибута
     ``fiasOnly``. В режиме *Только ФИАС* доступен только поиск и выбор из
     найденных объектов ФИАС.
