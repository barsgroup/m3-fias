Ext.namespace('Ext.m3.fias');

Ext.apply(Ext.m3.fias, {
    // Уровень точности адреса: населенный пункт.
    UI_LEVEL_PLACE: 1,
    // Уровень точности адреса: улица.
    UI_LEVEL_STREET: 2,
    // Уровень точности адреса: дом.
    UI_LEVEL_HOUSE: 3,
    // Уровень точности адреса: квартира.
    UI_LEVEL_FLAT: 4,

    // Уровень адресного объекта: Регион.
    FIAS_LEVEL_REGION: 1,
    // Уровень адресного объекта: Автономный округ.
    FIAS_LEVEL_AUTONOMUOS_DISTRICT: 2,
    // Уровень адресного объекта: Район.
    FIAS_LEVEL_DISTRICT: 3,
    // Уровень адресного объекта: Город.
    FIAS_LEVEL_CITY: 4,
    // Уровень адресного объекта: Внутригородская территория.
    FIAS_LEVEL_INTRACITY_TERRITORY: 5,
    // Уровень адресного объекта: Населенный пункт.
    FIAS_LEVEL_SETTLEMENT: 6,
    // Уровень адресного объекта: Планировочная структура.
    FIAS_LEVEL_PLANNING_STRUCTURE: 65,
    // Уровень адресного объекта: Улица.
    FIAS_LEVEL_STREET: 7,
    // Уровень адресного объекта: Земельный участок.
    FIAS_LEVEL_STEAD: 75,
    // Уровень адресного объекта: Здание, сооружение.
    FIAS_LEVEL_BUILDING: 8,
    // Уровень адресного объекта: Помещение в пределах здания, сооружения.
    FIAS_LEVEL_ROOM: 9,
    // Уровень адресного объекта: Дополнительная территория.
    FIAS_LEVEL_ADDITIONAL_TERRITORY: 90,
    // Уровень адресного объекта: Объект, подчиненный дополнительной территории.
    FIAS_LEVEL_ADDITIONAL_TERRITORY_OBJECT: 91
});


/**
 * Контейнер для полей редактирования составных элементов адреса.
 * Содержит всю логику работы полей ввода адресов, в т.ч. взаимодействие полей
 * между собой. Отображение полей реализуется в отдельных компонентах.
 */
Ext.m3.fias.AddressFields = Ext.extend(Ext.Component, {

    suspend: function() {
        if (this.suspendLevel === 0) {
            this.suspendEvents();
        }
        this.suspendLevel += 1;
    },

    resume: function() {
        this.suspendLevel -= 1;
        if (this.suspendLevel === 0) {
            this.resumeEvents();
        }
    },

    constructor: function(config) {
        this.suspendLevel = 0;

        this.level = Ext.m3.fias.UI_LEVEL_FLAT;

        Ext.m3.fias.AddressFields.superclass.constructor.call(this, config);

        this.addEvents(
            /**
             * @event change
             * Срабатывает, когда изменяется содержимое одного из полей.
             */
            'change'
        );
    },

    initPlace: function() {
        this.mon(this.placeNameField, 'change', this.onPlaceChange, this);
        this.mon(this.placeNameField, 'select', this.onPlaceSelect, this);
        this.mon(this.placeNameField, 'beforequery', this.beforePlaceQuery, this);

        if (this.place) {
            // Загрузка значений в поле. Отложенная загрузка для того, чтобы
            // сработали обработчики событий в представлении.
            function setValue() {
                this.placeNameField.getStore().loadData({
                    total: 1,
                    rows: [this.place]
                });
                var record = this.placeNameField.getStore().getAt(0);
                this.placeNameField.selectedRecord = record;
                this.placeNameField.setValue(record.get('fullName'));
                if (this.place.postalCode) {
                    this.zipCodeField.setValue(this.place.postalCode);
                }
                if (!self.street) {
                    this.updateFullAddress();
                }
                this.placeNameField.un('render', setValue);
            }
            this.placeNameField.on('render', setValue, this);
        }
    },

    initZipCode: function() {
        this.mon(this.zipCodeField, 'change', this.onZipChange, this);
    },

    initStreet: function() {
        this.mon(this.streetNameField, 'change', this.onStreetChange, this);
        this.mon(this.streetNameField, 'select', this.onStreetSelect, this);
        this.mon(this.streetNameField, 'beforequery', this.beforeStreetQuery, this);

        if (this.street) {
            // Загрузка значений в поле. Отложенная загрузка для того, чтобы
            // сработали обработчики событий в представлении.
            function setValue() {
                this.streetNameField.getStore().loadData({
                    total: 1,
                    rows: [this.street]
                });
                var record = this.streetNameField.getStore().getAt(0);
                this.streetNameField.selectedRecord = record;
                this.streetNameField.setValue(record.get('name'));
                if (this.street.postalCode) {
                    this.zipCodeField.setValue(this.street.postalCode);
                }
                if (!self.house) {
                    this.updateFullAddress();
                }
                this.streetNameField.un('render', setValue);
            }
            this.streetNameField.on('render', setValue, this);
        }
    },

    initHouse: function() {
        this.mon(this.houseNumberField, 'change', this.onHouseChange, this);
        this.mon(this.houseNumberField, 'select', this.onHouseSelect, this);
        this.mon(this.houseNumberField, 'beforequery', this.beforeHouseQuery, this);

        this.mon(this.buildingNumberField, 'change', this.onBuildingChange, this);

        this.mon(this.structureNumberField, 'change', this.onStructureChange, this);

        if (this.house) {

            function setValue() {
                this.houseNumberField.getStore().loadData({
                    total: 1,
                    rows: [this.house]
                });
                var record = this.houseNumberField.getStore().getAt(0);
                this.houseNumberField.selectedRecord = record;
                this.updateHouse(record);
                if (this.house.postalCode) {
                    this.zipCodeField.setValue(this.house.postalCode);
                }

                this.updateFullAddress();

                this.houseNumberField.un('render', setValue);
            }
            this.houseNumberField.on('render', setValue, this);
        }
    },

    initFlat: function() {
        this.mon(this.flatNumberField, 'change', this.onFlatChange, this);
    },

    initFullAddress: function() {
    },

    initComponent: function () {
        Ext.m3.fias.AddressFields.superclass.initComponent.call(this);

        this.initPlace();
        this.initZipCode();

        if (this.hasStreetField()) {
            this.initStreet();
        }

        if (this.hasHouseField()) {
            this.initHouse();
        }

        if (this.hasFlatField()) {
            this.initFlat();
        }

        if (this.hasFullAddressField()) {
            this.initFullAddress();
        }

        this.switchFields();
    },

    hasStreetField: function() {
        return [
            Ext.m3.fias.UI_LEVEL_STREET,
            Ext.m3.fias.UI_LEVEL_HOUSE,
            Ext.m3.fias.UI_LEVEL_FLAT
        ].indexOf(this.level) != -1;
    },

    hasHouseField: function() {
        return [
            Ext.m3.fias.UI_LEVEL_HOUSE,
            Ext.m3.fias.UI_LEVEL_FLAT
        ].indexOf(this.level) != -1;
    },

    hasFlatField: function() {
        return this.level == Ext.m3.fias.UI_LEVEL_FLAT;
    },

    hasFullAddressField: function() {
        return this.withFullAddress;
    },

    /**
     * Возвращает все поля, которые отображаются в интерфейсе.
     */
    getUIFields: function() {
        var result = [
            this.placeNameField,
            this.zipCodeField
        ];

        if (this.hasStreetField()) {
            result.push(
                this.streetNameField
            );
        }

        if (this.hasHouseField()) {
            result.push(
                this.houseNumberField,
                this.buildingNumberField,
                this.structureNumberField
            );
        }

        if (this.hasFlatField()) {
            result.push(
                this.flatNumberField
            );
        }

        if (this.hasFullAddressField()) {
            result.push(
                this.fullAddressField
            );
        }

        return result
    },

    /**
     * Возвращает поля с GUID-ами объектов.
     */
    getGUIDFields: function() {
        var result = [
            this.placeGUIDField
        ];

        if (this.hasStreetField()) {
            result.push(
                this.streetGUIDField
            );
        }

        if (this.hasHouseField()) {
            result.push(
                this.houseGUIDField
            );
        }

        return result
    },

    /**
     * Возвращает все поля.
     */
    getAllFields: function() {
        return this.getUIFields().concat(this.getGUIDFields());
    },

    isPlaceEmpty: function() {
        if (this.fiasOnly) {
            return !this.placeGUIDField.getValue();
        } else {
            return (
                !this.placeNameField.getValue() &&
                !this.placeGUIDField.getValue()
            );
        }
    },

    isZipCodeEmpty: function() {
        return !this.zipCodeField.getValue();
    },

    isStreetEmpty: function() {
        if (this.fiasOnly) {
            return !this.streetGUIDField.getValue();
        } else {
            return (
                !this.streetNameField.getValue() &&
                !this.streetGUIDField.getValue()
            );
        }
    },

    isHouseEmpty: function() {
        if (this.fiasOnly) {
            return !this.houseGUIDField.getValue();
        } else {
            return (
                !this.houseNumberField.getValue() &&
                !this.buildingNumberField.getValue() &&
                !this.structureNumberField.getValue() &&
                !this.houseGUIDField.getValue()
            );
        }
    },

    isBuildingEmpty: function() {
        return !this.buildingNumberField.getValue();
    },

    isStructureEmpty: function() {
        return !this.structureNumberField.getValue();
    },

    isFlatEmpty: function() {
        return !this.flatNumberField.getValue();
    },

    isEmpty: function() {
        return this.getAllFields().every(function(field) {
            return !field.getValue();
        });
    },

    clearPlace: function() {
        this.suspend();

        this.placeNameField.clearValue();
        this.placeNameField.lastQuery = null;
        this.placeGUIDField.setValue();

        if (this.zipCodeField.valueSource == 'place') {
            this.clearZipCode();
        }

        if (this.hasStreetField()) {
            this.clearStreet();
        }

        this.resume();
        this.fireEvent('change', this);
    },

    clearZipCode: function() {
        this.suspend();

        this.zipCodeField.setValue();
        delete this.zipCodeField.valueSource;

        this.resume();
        this.fireEvent('change', this)
    },

    clearStreet: function() {
        this.suspend();

        this.streetNameField.clearValue();
        this.streetNameField.lastQuery = null;
        this.streetGUIDField.setValue();

        if (this.zipCodeField.valueSource == 'street') {
            this.clearZipCode();
        }

        if (this.hasHouseField()) {
            this.clearHouse();
        }

        this.resume();
        this.fireEvent('change', this)
    },

    clearHouse: function() {
        this.suspend();

        this.houseNumberField.clearValue();
        this.houseNumberField.lastQuery = null;
        this.houseGUIDField.setValue();

        if (this.zipCodeField.valueSource == 'house') {
            this.clearZipCode();
        }

        this.clearBuilding();
        this.clearStructure();

        if (this.hasFlatField()) {
            this.clearFlat();
        }

        this.resume();
        this.fireEvent('change', this)
    },

    clearBuilding: function() {
        this.suspend();

        this.buildingNumberField.setValue();

        if (this.hasFlatField()) {
            this.clearFlat();
        }

        this.resume();
        this.fireEvent('change', this)
    },

    clearStructure: function() {
        this.suspend();

        this.structureNumberField.setValue();

        if (this.hasFlatField()) {
            this.clearFlat();
        }

        this.resume();
        this.fireEvent('change', this)
    },

    clearFlat: function() {
        this.suspend();

        this.flatNumberField.setValue();

        this.resume();
        this.fireEvent('change', this)
    },

    clearAllFields: function() {
        this.clearPlace();
    },

    setReadOnly: function(readOnly) {
        this.placeNameField.setReadOnly(readOnly);

        if (!this.fiasOnly) {
            this.zipCodeField.setReadOnly(readOnly);
        }

        if (this.hasStreetField()) {
            this.streetNameField.setReadOnly(readOnly);
        }

        if (this.hasHouseField()) {
            this.houseNumberField.setReadOnly(readOnly);
            if (!this.fiasOnly) {
                this.buildingNumberField.setReadOnly(readOnly);
                this.structureNumberField.setReadOnly(readOnly);
            }
        }

        if (this.hasFlatField()) {
            this.flatNumberField.setReadOnly(readOnly);
        }

        if (this.hasFullAddressField() && !this.fiasOnly) {
            this.fullAddressField.setReadOnly(readOnly);
        }
    },

    /**
     * Деактивирует поля ввода в зависимости от заполненности данных.
     *
     * Например, если не указан населенный пункт, то не будет возможности
     * указать улицу, номер дома/корпуса/строения и номер квартиры.
     */
    switchFields: function() {
        if (this.hasStreetField()) {
            this.streetNameField.setDisabled(this.isPlaceEmpty());
        }

        if (this.hasHouseField()) {
            this.houseNumberField.setDisabled(
                this.isPlaceEmpty() && this.isStreetEmpty
            );
            if (!this.fiasOnly) {
                this.buildingNumberField.setDisabled(this.isHouseEmpty());
                this.structureNumberField.setDisabled(this.isHouseEmpty());
            }
        }

        if (this.hasFlatField()) {
            this.flatNumberField.setDisabled(this.isHouseEmpty());
        }
    },

    beforePlaceQuery: function(queryEvent) {
    },

    beforeStreetQuery: function(queryEvent) {
        var parentGUID = this.placeGUIDField.getValue();

        if (parentGUID) {
            this.streetNameField.getStore().baseParams.parent = parentGUID;
        } else {
            return false;
        }
    },

    beforeHouseQuery: function(queryEvent) {
        var parentGUID = (
            this.streetGUIDField.getValue() || this.placeGUIDField.getValue()
        );

        if (parentGUID) {
            this.houseNumberField.getStore().baseParams.parent = parentGUID;
        } else {
            return false;
        }
    },

    onPlaceChange: function(field, newValue, oldValue) {
        if (newValue != oldValue) {
            this.suspend();

            if (
                !this.fiasOnly && !this.placeNameField.valueWasSelected ||
                !newValue
            ) {
                // Значение поля было введено вручную, а не выбрано.
                delete this.placeNameField.selectedRecord;
                this.placeGUIDField.setValue();
                if (this.zipCodeField.valueSource == 'place' || !newValue) {
                    this.clearZipCode();
                }
            }

            if (this.hasStreetField()) {
                this.clearStreet();
            }

            this.updateFullAddress();
            this.switchFields();
            this.placeNameField.valueWasSelected = false;

            this.resume();
            this.fireEvent('change', this);
        }
    },
    onPlaceSelect: function(field, record, index) {
        this.suspend();

        this.placeNameField.valueWasSelected = true;
        this.placeNameField.selectedRecord = record;
        this.placeGUIDField.setValue(record.get('guid'));

        this.zipCodeField.setValue(record.get('postalCode'));
        this.zipCodeField.valueSource = 'place';

        if (this.hasStreetField()) {
            this.clearStreet();
        }

        this.updateFullAddress();
        this.switchFields();

        this.resume();
        this.fireEvent('change', this);
    },

    onZipCodeChange: function(field, newValue, oldValue) {
    },

    onStreetChange: function(field, newValue, oldValue) {
        if (newValue != oldValue) {
            this.suspend();

            if (
                !this.fiasOnly && !this.streetNameField.valueWasSelected ||
                !newValue
            ) {
                // Значение поля было введено вручную, а не выбрано.
                delete this.streetNameField.selectedRecord;
                this.streetGUIDField.setValue();
                if (this.zipCodeField.valueSource == 'street' || !newValue) {
                    this.clearZipCode();
                }
            }

            if (this.hasHouseField()) {
                this.clearHouse();
            }

            this.updateFullAddress();
            this.switchFields();
            this.streetNameField.valueWasSelected = false;

            this.resume();
            this.fireEvent('change', this);
        }
    },
    onStreetSelect: function(field, record, index) {
        this.suspend();

        this.streetNameField.valueWasSelected = true;
        this.streetNameField.selectedRecord = record;
        this.streetGUIDField.setValue(record.get('guid'));

        this.zipCodeField.setValue(record.get('postalCode'));
        this.zipCodeField.valueSource = 'street';

        if (this.hasHouseField()) {
            this.clearHouse();
        }

        this.updateFullAddress();
        this.switchFields();

        this.resume();
        this.fireEvent('change', this);
    },

    updateHouse: function(record) {
        this.suspend();

        this.houseGUIDField.setValue(record.get('guid'));

        this.houseNumberField.setValue(record.get('houseNumber'));
        this.buildingNumberField.setValue(record.get('buildingNumber'));
        this.structureNumberField.setValue(record.get('structureNumber'));

        this.resume();
        this.fireEvent('change', this);
    },
    onHouseChange: function(field, newValue, oldValue) {
        this.suspend();

        if (this.houseNumberField.valueWasSelected) {
            // Здание было выбрано из списка.
            this.updateHouse(this.houseNumberField.selectedRecord);
        } else {
            // Значение поля было введено вручную, а не выбрано из списка.
            // Соответственно, есть только номер дома, а привязки к объекту
            // ФИАС нет.
            this.houseGUIDField.setValue();
            this.houseNumberField.setValue(newValue);
            this.houseNumberField.lastSelectionText = newValue;
            if (this.zipCodeField.valueSource == 'house' || !newValue) {
                this.clearZipCode();
            }
        }

        this.updateFullAddress();
        this.switchFields();
        this.houseNumberField.valueWasSelected = false;

        this.resume();
        this.fireEvent('change', this);
    },
    onHouseSelect: function(field, record, index) {
        this.suspend();

        this.houseNumberField.valueWasSelected = true;
        this.houseNumberField.selectedRecord = record;

        this.updateHouse(record);

        this.zipCodeField.setValue(record.get('postalCode'));
        this.zipCodeField.valueSource = 'house';

        this.updateFullAddress();
        this.switchFields();

        this.resume();
        this.fireEvent('change', this);
    },

    onBuildingChange: function(field, newValue, oldValue) {
        this.suspend();

        if (newValue != oldValue) {
            if (!this.fiasOnly && !this.houseNumberField.selectedRecord) {
                // Значение поля было введено вручную, а не выбрано.
                this.houseGUIDField.setValue();
                if (this.zipCodeField.valueSource == 'house' || !newValue) {
                    this.clearZipCode();
                }
            }

            this.updateFullAddress();
            this.switchFields();
        }

        this.resume();
        this.fireEvent('change', this);
    },

    onStructureChange: function(field, newValue, oldValue) {
        this.suspend();

        if (newValue != oldValue) {
            this.updateFullAddress();
            this.switchFields();
        }

        this.resume();
        this.fireEvent('change', this);
    },

    onFlatChange: function(field, newValue, oldValue) {
        this.suspend();

        if (newValue != oldValue) {
            this.updateFullAddress();
            this.switchFields();
        }

        this.resume();
        this.fireEvent('change', this);
    },

    onFullAddressChange: function(field, newValue, oldValue) {
        this.fireEvent('change', this);
    },

    getFullAddress: function() {
        var addressParts = [];

        if (!this.isZipCodeEmpty()) {
            addressParts.push(this.zipCodeField.getValue());
        }

        if (!this.isPlaceEmpty()) {
            addressParts.push(this.placeNameField.getValue());

            if (this.hasStreetField() && !this.isStreetEmpty()) {
                addressParts.push(this.streetNameField.getValue());
            }
            // значение дома может быть выбрано без указания улицы
            if (this.hasHouseField() && !this.isHouseEmpty()) {
                addressParts.push(
                    'д.' + this.houseNumberField.getValue()
                );
            }

            if (this.hasHouseField() && !this.isBuildingEmpty()) {
                addressParts.push(
                    'корп.' + this.buildingNumberField.getValue()
                );
            }

            if (this.hasHouseField() && !this.isStructureEmpty()) {
                addressParts.push(
                    'стр.' + this.structureNumberField.getValue()
                );
            }

            if (this.hasFlatField() && !this.isFlatEmpty()) {
                addressParts.push(
                    'кв.' + this.flatNumberField.getValue()
                );
            }

        }

        return addressParts.join(', ');
    },

    updateFullAddress: function() {
        if (this.hasFullAddressField()) {
            this.fullAddressField.setValue(this.getFullAddress());

            this.fireEvent('change', this);
        }
    },

    /**
     * Копирует значения полей из другого контейнера адресных полей.
     */
    copyDataFrom: function(other) {
        function copyComboBox(src, dst) {
            if (src.selectedRecord) {
                dst.getStore().loadData({
                    total: 1,
                    rows: [src.selectedRecord.json]
                });
                var record = dst.getStore().getAt(0);
                dst.selectedRecord = record;
                // dst.setValue(record.get(dst.displayField));
            }
            dst.setValue(src.getValue());
        }

        copyComboBox(other.placeNameField, this.placeNameField);
        this.placeGUIDField.setValue(
            other.placeGUIDField.getValue()
        );

        this.zipCodeField.setValue(other.zipCodeField.getValue());

        if (this.hasStreetField() && other.hasStreetField()) {
            copyComboBox(other.streetNameField, this.streetNameField);
            this.streetGUIDField.setValue(
                other.streetGUIDField.getValue()
            );
        }

        if (this.hasHouseField() && other.hasHouseField()) {
            copyComboBox(other.houseNumberField, this.houseNumberField);
            this.houseGUIDField.setValue(
                    other.houseGUIDField.getValue()
                );
            this.buildingNumberField.setValue(
                other.buildingNumberField.getValue()
            );
            this.structureNumberField.setValue(
                other.structureNumberField.getValue()
            );
        }

        if (this.hasFlatField() && other.hasFlatField()) {
            this.flatNumberField.setValue(
                other.flatNumberField.getValue()
            );
        }

        if (this.hasFullAddressField() && other.hasFullAddressField()) {
            this.fullAddressField.setValue(
                other.fullAddressField.getValue()
            );
        }

        this.switchFields();
        this.getAllFields().forEach(function(field) {
            field.validate();
        });
    },

    /**
     * Очищает значения полей.
     */
    clear: function() {
        this.getAllFields().forEach(function(field) {
            field.setValue();
            field.validate();
        });
    },

    /**
     * Возвращает true, если адрес, указанный в другой панели, равен адресу в
     * данной панели.
     */
    equals: function(other) {
        if (this.level == other.level) {
            var thisFields = this.getAllFields();
            var otherFields = other.getAllFields();
            for (var i = 0; i < thisFields.length; i++) {
                if (thisFields[i].getValue() != otherFields[i].getValue()) {
                    return false;
                }
            }
            return true;
        } else {
            return false;
        }
    },

    /**
     * Синхронизирует поля данного контейнера с полями контейнера other.
     * Содержимое полей other будет скопировано при вызове метода, а также
     * при изменении данных в other.
     */
    syncWith: function(other, sync) {
        assert(other instanceof Ext.m3.fias.AddressFields);
        assert(this.level == other.level);

        if (sync) {
            // Включение синхронизации с другим контейнером.
            this.copyDataFrom(other);
            this.setReadOnly(true);

            var target = this;
            this.syncFunction = function() {
                target.copyDataFrom(other)
            }

            this.mon(other, 'change', this.syncFunction);
        } else if (this.syncFunction) {
            // Отключение синхронизации с другим контейнером.
            if (this.mun(other, 'change', this.syncFunction)) {
                this.clear();
                this.setReadOnly(false);
            }

            delete this.syncFunction;
        }
    },

    isSyncronizedWith: function(other) {
        assert(other instanceof Ext.m3.fias.AddressFields);

        var result = false;

        for (var i = 0; i < this.mons.length; i++){
            mon = this.mons[i];
            if (
                mon.item === other &&
                mon.ename == 'change' &&
                mon.fn == this.copyDataFrom &&
                mon.scope == this
            ) {
                result = true;
                break;
            }
        }

        return result;
    }

});


Ext.m3.fias.AddressViewBase = Ext.extend(Ext.Container, {

    /**
     * Шаблон для отображения зданий в выпадающем списке поля "Дом".
     */
    houseTpl: [
        '<tpl for=".">',
            '<div class="x-combo-list-item">',
                '<tpl if="houseNumber">',
                    'д.{houseNumber}',
                '</tpl>',
                '<tpl if="buildingNumber">',
                    ' корп.{buildingNumber}',
                '</tpl>',
                '<tpl if="structureNumber">',
                    ' стр.{structureNumber}</span>',
                '</tpl>',
            '</div>',
        '</tpl>'
    ].join(''),

    initComponent: function() {
        Ext.m3.fias.AddressViewBase.superclass.initComponent.call(this);

        this.fields = this.items.removeAt(0);

        if (this.fields.hasHouseField()) {
            this.fields.houseNumberField.tpl = this.houseTpl;
        }
    },

    formed: function(field, labelWidth, config) {
        field.anchor = '100%';

        return new Ext.Container(Ext.applyIf({
            labelWidth: labelWidth,
            layout: 'form',
            items: [
                field
            ]
        }, config));
    }

});


/**
 * Компактное представление панели для ввода адресов.
 *
 * Поля располагаются максимум на 3-х строках:
 *
 *     1. Населенный пункт, Индекс
 *     2. Улица, Дом, Корпус, Строение, Квартира
 *     3. Полный адрес
 */
Ext.m3.fias.RowsAddressView = Ext.extend(Ext.m3.fias.AddressViewBase, {

    setPaddings: function(rowItems) {
        for (var i = 1; i < rowItems.length; i++) {
            if (rowItems[i] instanceof Ext.Container) {
                var container = rowItems[i];
                container.style = Ext.apply(container.style || {}, {
                    'padding': '0 0 0 5px'
                });
            }
        }
    },

    addPlaceField: function(rowItems) {
        this.placeFieldContainer = this.formed(
            this.fields.placeNameField,
            this.labelsWidth.place,
            {
                'flex': 1
            }
        );
        rowItems.push(
            this.placeFieldContainer,
            this.fields.placeGUIDField
        );
    },

    addZipField: function(rowItems) {
        this.zipFieldContainer = this.formed(
            this.fields.zipCodeField,
            this.labelsWidth.zipCode,
            {
                flex: 0
            }
        );
        rowItems.push(
            this.zipFieldContainer
        );
    },

    initRow1: function() {
        var rowItems = [];

        this.addPlaceField(rowItems);
        this.addZipField(rowItems);

        this.setPaddings(rowItems);

        this.row1 = new Ext.Container({
            items: rowItems,
            layout: 'hbox',
            layoutConfig: {
                'align': 'middle'
            }
        });
        this.add(this.row1);
    },

    addStreetField: function(rowItems) {
        this.streetFieldContainer = this.formed(
            this.fields.streetNameField,
            this.labelsWidth.street,
            {
                'flex': 1
            }
        );
        rowItems.push(
            this.streetFieldContainer,
            this.fields.streetGUIDField
        );
    },

    addHouseField: function(rowItems) {
        this.houseFieldContainer = this.formed(
            this.fields.houseNumberField,
            this.labelsWidth.house,
            {
                'flex': 0
            }
        );
        this.buildingFieldContainer = this.formed(
            this.fields.buildingNumberField,
            this.labelsWidth.building,
            {
                'flex': 0
            }
        );
        this.structureFieldContainer = this.formed(
            this.fields.structureNumberField,
            this.labelsWidth.structure,
            {
                'flex': 0
            }
        );
        rowItems.push(
            this.houseFieldContainer,
            this.buildingFieldContainer,
            this.structureFieldContainer,
            this.fields.houseGUIDField
        );
    },

    addFlatField: function(rowItems) {
        this.flatFieldContainer = this.formed(
            this.fields.flatNumberField,
            this.labelsWidth.flat,
            {
                'flex': 0
            }
        );
        rowItems.push(
            this.flatFieldContainer
        );
    },

    initRow2: function() {
        var rowItems = [];

        if (this.fields.streetNameField) {
            this.addStreetField(rowItems);
        }
        if (this.fields.houseNumberField) {
            this.addHouseField(rowItems);
        }
        if (this.fields.flatNumberField) {
            this.addFlatField(rowItems);
        }

        if (rowItems.length > 0) {
            this.setPaddings(rowItems);

            this.row2 = new Ext.Container({
                items: rowItems,
                layout: 'hbox',
                layoutConfig: {
                    'align': 'middle'
                }
            });
            this.add(this.row2);
        }
    },

    addFullAddressField: function(rowItems) {
        if (this.fields.fullAddressField) {
            this.fullAddressFieldContainer = this.formed(
                this.fields.fullAddressField,
                this.labelsWidth.fullAddress,
                {
                    'flex': 1
                }
            );
            rowItems.push(
                this.fullAddressFieldContainer
            );
        }
    },

    initRow3: function() {
        var rowItems = [];

        this.addFullAddressField(rowItems);

        if (rowItems.length > 0) {
            this.row3 = new Ext.Container({
                items: rowItems,
                layout: 'hbox'
            });
            this.add(this.row3);
        }
    },

    initComponent: function() {
        Ext.m3.fias.RowsAddressView.superclass.initComponent.call(this);

        this.initRow1();
        this.initRow2();
        this.initRow3();

        if (this.fields.hasStreetField()) {
            this.mon(
                this.fields.streetNameField.getStore(),
                'load',
                this.onStreetLoad,
                this
            )
        }
    },

    onStreetLoad: function(store, records, options) {
        records.forEach(function(record) {
            record.set(
                'name',
                record.get('shortName') + '. ' + record.get('formalName')
            );
        });
    }

});
