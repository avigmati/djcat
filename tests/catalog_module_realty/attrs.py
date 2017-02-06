from djcat.attrs import ChoiceAttribute


class BuildingTypeAttribute(ChoiceAttribute):
    attr_name = 'building_type'
    attr_verbose_name = 'Building type'
    attr_key = 'rbt'
    attr_choices = (
        (1, 'Brick', 'brick'),
        (2, 'Panel', 'panel'),
        (3, 'Block', 'block'),
        (4, 'Monolith', 'monolith'),
        (5, 'Wood', 'wood'),
    )


class RoomsAttribute(ChoiceAttribute):
    attr_name = 'rooms'
    attr_verbose_name = 'Number of rooms'
    attr_key = 'rnr'
    attr_choices = (
        (1, 'Studio', 'studio'),
        (2, '1 roomed', '1roomed'),
        (3, '2 roomed', '2roomed'),
        (4, '3 roomed', '3roomed'),
        (5, '4 roomed', '4roomed'),
        (6, '5 roomed', '5roomed'),
        (7, '6 roomed', '6roomed'),
        (8, '7 roomed', '7roomed'),
        (9, '8 roomed', '8roomed'),
        (10, '9 roomed', '9roomed'),
        (11, '10 or more rooms', 'more9rooms'),
    )

