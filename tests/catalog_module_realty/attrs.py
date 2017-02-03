# from djcat.attrs import ChoiceAttribute, catalog_attribute, ChoiceQuery
from djcat.attrs import ChoiceAttribute, catalog_attribute


class BuildingTypeAttribute(ChoiceAttribute):
    attr_name = 'building_type'
    attr_verbose_name = 'Тип строения'
    attr_key = 'rbt'
    attr_choices = (
        (1, 'Кирпичный', 'kirpichnyi'),
        (2, 'Панельный', 'panelnuy'),
        (3, 'Блочный', 'blochnuy'),
        (4, 'Монолитный', 'monolitnuy'),
        (5, 'Деревянный', 'derevyanuy'),
    )


@catalog_attribute(name='room', verbose_name='Количество комнат', key='rr')
class RoomAttribute(ChoiceAttribute):
    attr_choices = (
        (1, 'Студия', 'studio'),
        (2, '1 комнатная', '1komnatnye'),
        (3, '2 комнатная', '2komnatnye'),
        (4, '3 комнатная', '3komnatnye'),
        (5, '4 комнатная', '4komnatnye'),
        (6, '5 комнатная', '5komnatnye'),
        (7, '6 комнатная', '6komnatnye'),
        (8, '7 комнатная', '7komnatnye'),
        (9, '8 комнатная', '8komnatnye'),
        (10, '9 комнатная', '9komnatnye'),
        (11, '10 и больше комнат', 'bolshe9komnat'),    )
