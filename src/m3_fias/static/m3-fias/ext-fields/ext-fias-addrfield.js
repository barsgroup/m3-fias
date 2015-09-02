Ext.namespace('Ext.fias');

/**
 * Панель редактирования адреса
 */
Ext.fias.AddrField = Ext.extend(Ext.Container, {
    constructor: function (baseConfig, params) {
        var items = params.items || [];

        var place_store = new Ext.data.JsonStore({
            url: params.fias_api_url + '/search',
            idProperty: 'ao_guid',
            root: 'rows',
            totalProperty: 'total',
            fields: [
                {name: 'ao_guid'},
                {name: 'ao_level'},
                {name: 'address'},
                {name: 'shortname'},
                {name: 'postal_code'},
                {name: 'formal_name'},
                {name: 'name'},
                {name: 'place_address'}
            ],
        });
        place_store.baseParams['levels'] = [1, 4, 6];

        if (params.place_record != '' && params.place_record != undefined) {
            var rec = Ext.util.JSON.decode(params.place_record);
            place_store.loadData({
                total: 1,
                rows: [rec]
            });
        }

        if (params.read_only)
            var field_cls = 'm3-grey-field'
        else
            var field_cls = ''

        this.row_spacer = {
            xtype: 'spacer',
            height: 5
        };
        this.place = new Ext.form.ComboBox({
            name: params.place_field_name,
            fieldLabel: params.place_label,
            allowBlank: params.place_allow_blank,
            readOnly: params.read_only,
            cls: field_cls,
            hideTrigger: true,
            minChars: 2,
            emptyText: 'Введите населенный пункт...',
            queryParam: 'filter',
            store: place_store,
            resizable: true,
            displayField: 'name',
            valueField: 'ao_guid',
            mode: 'remote',
            hiddenName: params.place_field_name,
            valueNotFoundText: '',
            invalidClass: params.invalid_class
        });
        this.place.setValue(params.place_value);

        this.zipcode = new Ext.form.TextField({
            name: params.zipcode_field_name,
            value: params.zipcode_value,
            emptyText: 'индекс',
            readOnly: params.read_only,
            cls: field_cls,
            width: 55,
            maskRe: /[0-9]/
        });
        this.zipcode.param_label_width = params.zipcode_label_width;

        if (params.level > 1) {
            var street_store = new Ext.data.JsonStore({
                url: params.fias_api_url + '/search',
                idProperty: 'ao_guid',
                root: 'rows',
                totalProperty: 'total',
                fields: [
                    {name: 'ao_guid'},
                    {name: 'ao_level'},
                    {name: 'address'},
                    {name: 'shortname'},
                    {name: 'postal_code'},
                    {name: 'formal_name'},
                    {name: 'name'}
                ],
                sortInfo: {
                    field: 'name'
                }
            });

            street_store.baseParams['levels'] = 7;
            if (params.street_record != '' && params.street_record != undefined) {
                var rec = Ext.util.JSON.decode(params.street_record);
                street_store.loadData({
                    total: 1,
                    rows: [rec]
                });
            }
            this.street = new Ext.form.ComboBox({
                name: params.street_field_name,
                fieldLabel: params.street_label,
                allowBlank: params.street_allow_blank,
                readOnly: params.read_only,
                cls: field_cls,
                hideTrigger: true,
                minChars: 2,
                emptyText: 'Введите улицу...',
                queryParam: 'filter',
                store: street_store,
                resizable: true,
                displayField: 'name',
                valueField: 'ao_guid',
                mode: 'remote',
                hiddenName: params.street_field_name,
                valueNotFoundText: '',
                invalidClass: params.invalid_class
            });
            this.street.setValue(params.street_value);
            this.street.getStore().baseParams.boundary = this.place.value;
            this.street.param_label_width = params.street_label_width;

            if (params.level > 2) {
                var house_store = new Ext.data.JsonStore({
                    url: params.fias_api_url + '/list/houses',
                    idProperty: 'house_number',
                    root: 'rows',
                    totalProperty: 'total',
                    fields: [
                        {name: 'house_number'},
                        {name: 'postal_code'},
                        {name: 'houseguid'}
                    ],
                    sortInfo: {
                        field: 'house_number'
                    }
                });

                if(params.house_value != undefined){
                    house_store.loadData({
                        total: 1,
                        rows: [{
                            house_number: params.house_value,
                            houseguid: params.house_guid_value,
                            postal_code: ''
                        }]
                    });
                }

                this.house = new Ext.form.ComboBox({
                    name: params.house_field_name,
                    fieldLabel: params.house_label,
                    allowBlank: params.house_allow_blank,
                    readOnly: params.read_only,
                    cls: field_cls,
                    hideTrigger: true,
                    minChars: 0,
                    width: 40,
                    emptyText: '',
                    queryParam: 'part',
                    store: house_store,
                    resizable: true,
                    displayField: 'house_number',
                    valueField: 'house_number',
                    mode: 'remote',
                    hiddenName: params.house_field_name,
                    invalidClass: params.invalid_class
                });
                this.house.setValue(params.house_value);
                this.house.getStore().baseParams.street = this.street.value;
                this.house.getStore().baseParams.place = this.place.value;
                this.house.param_label_width = params.house_label_width;

                this.house_guid = new Ext.form.Hidden({
                    name: params.house_field_name + '_guid',
                    xtype: 'hiddenfield'
                });
                this.house_guid.setValue(params.house_guid_value);

                if (params.use_corps) {
                    this.corps = new Ext.form.TextField({
                        name: params.corps_field_name,
                        allowBlank: params.corps_allow_blank,
                        readOnly: params.read_only,
                        cls: field_cls,
                        fieldLabel: params.corps_label,
                        value: params.corps_value,
                        emptyText: '',
                        width: 40,
                        invalidClass: params.invalid_class
                    });
                    this.corps.param_label_width = params.corps_label_width;
                }
                if (params.level > 3) {
                    this.flat = new Ext.form.TextField({
                        name: params.flat_field_name,
                        fieldLabel: params.flat_label,
                        value: params.flat_value,
                        allowBlank: params.flat_allow_blank,
                        readOnly: params.read_only,
                        cls: field_cls,
                        emptyText: '',
                        width: 40,
                        invalidClass: params.invalid_class
                    });
                    this.flat.param_label_width = params.flat_label_width;
                }
            }
        }
        if (params.addr_visible) {
            this.addr = new Ext.form.TextArea({
                name: params.addr_field_name,
                anchor: '100%',
                width: '100%',
                fieldLabel: params.addr_label,
                value: params.addr_value,
                readOnly: true,
                cls: field_cls,
                height: 36
            });
        }

        function formed(item, flex, extraconf){

            item.anchor ='100%';

            conf = {
                xtype: 'container',
                layout: 'form',
                labelPad: 3,
                labelWidth: item.param_label_width || 100,
                items: [item],
                height: 22,
            };

            if(Ext.isNumber(flex)){
                conf.flex = flex;
            }else{
                // установка фиксированной ширины
                conf.width = conf.labelWidth + conf.labelPad +
                             (conf.items[0].width || 100);
            }

            return Ext.apply(conf, extraconf || {});
        }

        if (params.view_mode == 1) {
            var row_items;
            // В одну строку
            this.place.flex = 1;
            if (params.level > 2) {
                row_items = [this.place, this.zipcode];
            } else {
                row_items = [this.place];
            }

            if (params.level > 1) {
                row_items.push(formed(this.street, 1));

                if (params.level > 2) {
                    row_items.push(formed(this.house));
                    row_items.push(this.house_guid);
                    if (params.use_corps) {
                        row_items.push(formed(this.corps));
                    }

                    if (params.level > 3) {
                        row_items.push(formed(this.flat));
                    }
                }
            }

            var row = {
                xtype: 'compositefield',
                anchor: '100%',
                fieldLabel: params.place_label,
                items: row_items,
                invalidClass: params.invalid_composite_field_class
            };
            items.push(row, this.row_spacer);

        } else if (params.view_mode == 2) {
            // В две строки
            if (params.level > 2) {
                this.place.flex = 1;
                var row = {
                    xtype: 'compositefield',
                    anchor: '100%',
                    fieldLabel: params.place_label,
                    items: [this.place, formed(this.zipcode)],
                    invalidClass: params.invalid_composite_field_class
                };
                items.push(row, this.row_spacer);
            } else {
                this.place.anchor = '100%';
                items.push(this.place);
            }
            if (params.level > 1) {
                this.street.flex = 1;
                var row_items = [this.street];

                if (params.level > 2) {
                    row_items.push(formed(this.house));
                    row_items.push(this.house_guid);
                    if (params.use_corps) {
                        row_items.push(formed(this.corps));
                    }

                    if (params.level > 3) {
                        row_items.push(formed(this.flat));
                    }
                }

                var row = {
                    xtype: 'compositefield',
                    anchor: '100%',
                    fieldLabel: params.street_label,
                    items: row_items,
                    invalidClass: params.invalid_composite_field_class
                };
                items.push(row, this.row_spacer);
            }
        } else if (params.view_mode == 3) {

            // В три строки
            if (params.level > 2) {
                this.place.flex = 1;
                var row = {
                    xtype: 'compositefield',
                    anchor: '100%',
                    fieldLabel: params.place_label,
                    items: [this.place, this.zipcode],
                    invalidClass: params.invalid_composite_field_class
                };
                items.push(row, this.row_spacer);
            } else {
                this.place.anchor = '100%';
                items.push(this.place);
            }
            if (params.level > 1) {
                this.street.anchor ='100%';
                items.push(this.street, this.row_spacer);

                if (params.level > 2) {

                    this.house.flex = 1;
                    this.house.width = undefined;
                    var row_items = [this.house, this.house_guid];

                    if (params.use_corps) {
                        row_items.push(formed(this.corps, 1));
                    }

                    if (params.level > 3) {
                        row_items.push(formed(this.flat, 1));
                    }

                    var row = {
                        anchor: '100%',
                        xtype: 'compositefield',
                        fieldLabel: this.house.fieldLabel,
                        items: row_items,
                        style: {
                            overflow: 'hidden'
                        }
                    };
                    items.push(row);
                }
            }
        }

        if (params.addr_visible) {
            items.push(this.addr);
        }

        var config = Ext.applyIf({
            items: items,
            get_addr_url: params.get_addr_url,
            level: params.level,
            use_corps: params.use_corps,
            addr_visible: params.addr_visible,
            style: {
                overflow: 'hidden'
            }
        }, baseConfig);

        Ext.Container.superclass.constructor.call(this, config);
    },
    beforeStreetQuery: function (qe) {
        this.street.getStore().baseParams.boundary = this.place.value;
        this.fireEvent('before_query_street', this, qe);
    },
    clearStreet: function () {
        if (this.street !== undefined) {
            this.street.setValue('');
        }
    },
    clearHouse: function (){
        if(this.house !== undefined){
            this.house.setValue('');
            if (this.house_guid !== undefined){
                this.house_guid.setValue('');
            }
            if(this.corps !== undefined){
                this.corps.setValue('');
            }
        }
    },
    afterRenderAddr: function () {
        //вашем обработчик dbl click через DOM елемент
        if (this.addr_visible) {
            this.addr.getEl().on('dblclick', this.onDblClickAddr, this)
        }
    },

    initComponent: function () {
        Ext.fias.AddrField.superclass.initComponent.call(this);

        this.mon(this.place, 'change', this.onChangePlace, this);
        this.mon(this.place, 'select', this.onChangePlace, this);
        if (this.level > 1) {
            this.mon(this.street, 'change', this.onChangeStreet, this);
            this.mon(this.street, 'select', this.onChangeStreet, this);
            if (this.level > 2) {
                this.mon(this.house, 'change', this.onChangeHouse, this);
                this.mon(this.house, 'select', this.onChangeHouse, this);
                if (this.use_corps) {
                    this.mon(this.corps, 'change', this.onChangeCorps, this);
                }
                this.mon(this.zipcode, 'change', this.onChangeZipcode, this);
                if (this.level > 3) {
                    this.mon(this.flat, 'change', this.onChangeFlat, this);
                }
            }
        }
        this.mon(this.place, 'beforequery', this.beforePlaceQuery, this);
        if (this.level > 1) {
            this.mon(this.street, 'beforequery', this.beforeStreetQuery, this);
        }
        if (this.level > 2) {
            this.mon(this.house, 'beforequery', this.beforeHouseQuery, this);
        }
        if (this.addr_visible) {
            this.addr.on('afterrender', this.afterRenderAddr, this);
        }

        this.addEvents(
            /**
             * @event change
             * При изменении адресного поля целиком.
             */
            'change',
            /**
             * @event change_place
             * При изменении населенного пункта
             * @param {AddrField} this
             * @param {Place_code} Код нас. пункта по КЛАДР
             * @param {Store} Строка с информацией о данных КЛАДРа по выбранному пункту
             */
            'change_place',
            /**
             * @event change_street
             * При изменении улицы
             * @param {AddrField} this
             * @param {Street_code} Код улицы по КЛАДР
             * @param {Store} Строка с информацией о данных КЛАДРа по выбранной улице
             */
            'change_street',
            /**
             * @event change_house
             * При изменении дома
             * @param {AddrField} this
             * @param {House} Номер дома
             */
            'change_house',
            /**
             * @event change_corps
             * При изменении скорпуса
             * @param {AddrField} this
             * @param {Corps} Номер корпуса
             */
            'change_corps',
            /**
             * @event change_flat
             * При изменении квартиры
             * @param {AddrField} this
             * @param {Flat} Номер квартиры
             */
            'change_flat',
            /**
             * @event change_zipcode
             * При изменении индекса
             * @param {AddrField} this
             * @param {zipcode} индекс
             */
            'change_zipcode',
            /**
             * @event before_query_place
             * Перед запросом данных о населенном пункте
             * @param {AddrField} this
             * @param {Event} Событие
             */
            'before_query_place',
            /**
             * @event before_query_street
             * Перед запросом данных об улице
             * @param {AddrField} this
             * @param {Event} Событие
             */
            'before_query_street',
            /**
             * @event before_query_house
             * Перед запросом данных о доме
             * @param {AddrField} this
             * @param {Event} Событие
             */
            'before_query_house');
    },
    getNewAddr: function () {
        var place_id;
        if (this.place != undefined) {
            place_id = this.place.getValue();
        }
        var street_id;
        if (this.street != undefined) {
            street_id = this.street.getValue();
        }
        var house_num;
        if (this.house != undefined) {
            house_num = this.house.getValue();
        }
        var corps_num;
        if (this.corps != undefined) {
            corps_num = this.corps.getValue();
        }
        var flat_num;
        if (this.flat != undefined) {
            flat_num = this.flat.getValue();
        }
        var zipcode;
        if (this.zipcode != undefined) {
            zipcode = this.zipcode.getValue();
        }
        var place = null;
        var place_data = this.place.getStore().data.get(place_id);
        if (place_data != undefined) {
            place = place_data.data;
        }
        var street = null;
        if (this.street != undefined) {
            var street_data = this.street.getStore().data.get(street_id);
        };
        if (street_data != undefined) {
            street = street_data.data;
        }

        var new_addr = this.generateTextAddr(place, street, house_num, corps_num, flat_num, zipcode);
        if (this.addr != undefined) {
            this.addr.setValue(new_addr);
        }

        return new_addr;
    },
    generateTextAddr: function (place, street, house, corps, flat, zipcode) {
        /* Формирование текстового представления полного адреса */
        var addr_text = '';

        if(Ext.isObject(place)){
            addr_text = place.place_address;
        }

        if (Ext.isObject(street)){
            addr_text += ', ' + street.shortname + '. ' + street.formal_name;
        }

        // проставим индекс
        if(!Ext.isEmpty(zipcode)){
            addr_text = zipcode + ', ' + addr_text;
        }
        // обработаем и поставим дом с квартирой
        if (!Ext.isEmpty(house)) {
            addr_text = addr_text + ', ' + 'д. ' + house;
        }
        // обработаем и поставим дом с квартирой
        if (!Ext.isEmpty(corps)) {
            addr_text = addr_text + ', ' + 'корп. ' + corps;
        }
        if (!Ext.isEmpty(flat)) {
            addr_text = addr_text + ', ' + 'кв. ' + flat;
        }
        return addr_text;
    },
    setNewAddr: function (newAddr) {
        if (this.addr != undefined) {
            this.addr.value = newAddr;
        }
    },
    onChangePlace: function () {
        var val = this.place.getValue();
        var data = this.place.getStore().data.get(val);

        if (data != undefined) {
            data = data.data;
            if (data.postal_code) {
                this.zipcode.setValue(data.postal_code)
            }else{
                this.zipcode.setValue('');
            }
        } else {
            this.zipcode.setValue('');
            this.place.setValue('');
        }
        this.clearStreet();
        this.clearHouse();
        this.fireEvent('change_place', this, val, data);
        if (this.addr_visible) {
            this.getNewAddr();
        }

    },
    onChangeStreet: function () {
        var val = this.street.getValue();
        var data = this.street.getStore().data.get(val);
        if (data != undefined) {
            data = data.data;
            if (data.postal_code) {
                this.zipcode.setValue(data.postal_code);
            }else{
                this.zipcode.setValue('');
            }
            this.clearHouse();
        } else {
            this.zipcode.setValue('');
            this.clearStreet();
        }
        this.fireEvent('change_street', this, val, data);

        if (this.addr_visible) {
            this.getNewAddr();
        }
    },
    onChangeHouse: function () {
        var house_num = this.house.getValue(),
            addr_field = this,
            store = this.house.getStore(),
            house = store.data.get(house_num);

        this.fireEvent('change_house', this, house_num);

        if (!house) {
            store.baseParams.part = house_num;
            store.baseParams.street = this.street.getValue();
            store.baseParams.place = this.place.getValue();
            store.load({
                callback: function(records, options, success) {
                    if (success) {
                        for (var i = 0; i < records.length; i++) {
                            data = records[i].data
                            if (!data.postal_code)
                                continue;

                            addr_field.zipcode.setValue(data.postal_code);
                            addr_field.house_guid.setValue(data.house_guid);
                        }
                    }
                    if (addr_field.addr_visible)
                        addr_field.getNewAddr();
                },
            })
        } else {
            this.house_guid.setValue(house.data.houseguid);
            if (house.data.postal_code)
                this.zipcode.setValue(house.data.postal_code);
            if (this.addr_visible)
                this.getNewAddr();
        }
    },
    onChangeCorps: function () {
        this.fireEvent('change_corps', this, this.corps.getValue());
        if (this.addr_visible) {
            this.getNewAddr();
        }
    },
    onChangeFlat: function () {
        this.fireEvent('change_flat', this, this.flat.getValue());
        if (this.addr_visible) {
            this.getNewAddr();
        }
    },
    onChangeZipcode: function () {
        this.fireEvent('change_zipcode', this, this.zipcode.getValue());
        if (this.addr_visible) {
            this.getNewAddr();
        }
    },
    beforePlaceQuery: function (qe) {
        this.fireEvent('before_query_place', this, qe);
    },
    onDblClickAddr: function (qe) {
        if (this.addr_visible) {
            this.addr.setReadOnly(false);
        }
    },
    beforeHouseQuery: function (qe) {
        qe.combo.store.baseParams.street = this.street.getValue();
        qe.combo.store.baseParams.place = this.place.getValue();
        this.fireEvent('before_query_house', this, qe);
    },
});

Ext.reg('fias-addrfield', 'Ext.fias.AddrField');
