from djcat.attrs import ChoiceAttribute, catalog_attribute


@catalog_attribute(name='building_type', verbose_name='Тип строения', key='rbt')
class BuildingTypeAttribute(ChoiceAttribute):
    attr_choices = (
        (1, 'Кирпичный', 'kirpichnuy'),
        (2, 'Панельный', 'panelnuy'),
        (3, 'Блочный', 'blochnuy'),
        (4, 'Монолитный', 'monolitnuy'),
        (5, 'Деревянный', 'derevyanuy'),
    )
