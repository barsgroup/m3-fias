# coding: utf-8


# -----------------------------------------------------------------------------
#: Уровень точности адреса: населенный пункт.
UI_LEVEL_PLACE = 1

#: Уровень точности адреса: улица.
UI_LEVEL_STREET = 2

#: Уровень точности адреса: дом.
UI_LEVEL_HOUSE = 3

#: Уровень точности адреса: квартира.
UI_LEVEL_FLAT = 4

#: Уровни точности адреса
UI_LEVELS = (
    UI_LEVEL_PLACE,
    UI_LEVEL_STREET,
    UI_LEVEL_HOUSE,
    UI_LEVEL_FLAT,
)
# -----------------------------------------------------------------------------
# Уровни адресных объектов ФИАС.

#: Уровень адресного объекта: Регион.
FIAS_LEVEL_REGION = 1

#: Уровень адресного объекта: Автономный округ.
FIAS_LEVEL_AUTONOMUOS_DISTRICT = 2

#: Уровень адресного объекта: Район.
FIAS_LEVEL_DISTRICT = 3

#: Уровень адресного объекта: Город.
FIAS_LEVEL_CITY = 4

#: Уровень адресного объекта: Внутригородская территория.
FIAS_LEVEL_INTRACITY_TERRITORY = 5

#: Уровень адресного объекта: Населенный пункт.
FIAS_LEVEL_SETTLEMENT = 6

#: Уровень адресного объекта: Планировочная структура.
FIAS_LEVEL_PLANNING_STRUCTURE = 65

#: Уровень адресного объекта: Улица.
FIAS_LEVEL_STREET = 7

#: Уровень адресного объекта: Земельный участок.
FIAS_LEVEL_STEAD = 75

#: Уровень адресного объекта: Здание, сооружение.
FIAS_LEVEL_BUILDING = 8

#: Уровень адресного объекта: Помещение в пределах здания, сооружения.
FIAS_LEVEL_ROOM = 9

#: Уровень адресного объекта: Дополнительная территория.
FIAS_LEVEL_ADDITIONAL_TERRITORY = 90

#: Уровень адресного объекта: Объект, подчиненный дополнительной территории.
FIAS_LEVEL_ADDITIONAL_TERRITORY_OBJECT = 91

#: Уровни адресных объектов.
FIAS_LEVELS = (
    FIAS_LEVEL_REGION,
    FIAS_LEVEL_AUTONOMUOS_DISTRICT,
    FIAS_LEVEL_DISTRICT,
    FIAS_LEVEL_CITY,
    FIAS_LEVEL_INTRACITY_TERRITORY,
    FIAS_LEVEL_SETTLEMENT,
    FIAS_LEVEL_PLANNING_STRUCTURE,
    FIAS_LEVEL_STREET,
    FIAS_LEVEL_STEAD,
    FIAS_LEVEL_BUILDING,
    FIAS_LEVEL_ROOM,
    FIAS_LEVEL_ADDITIONAL_TERRITORY,
    FIAS_LEVEL_ADDITIONAL_TERRITORY_OBJECT,
)

#: Уровни адресных объектов, относящихся к населенным пунктам.
FIAS_LEVELS_PLACE = (
    FIAS_LEVEL_REGION,
    FIAS_LEVEL_AUTONOMUOS_DISTRICT,
    FIAS_LEVEL_DISTRICT,
    FIAS_LEVEL_CITY,
    FIAS_LEVEL_INTRACITY_TERRITORY,
    FIAS_LEVEL_SETTLEMENT,
    FIAS_LEVEL_PLANNING_STRUCTURE,
    FIAS_LEVEL_ADDITIONAL_TERRITORY,
)

# Уровни адресных объектов, относящимся к улицам.
FIAS_LEVELS_STREET = (
    FIAS_LEVEL_STREET,
    FIAS_LEVEL_ADDITIONAL_TERRITORY_OBJECT,
)
# -----------------------------------------------------------------------------
