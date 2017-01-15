class CategoryInheritanceError(Exception):
    def __init__(self, invalid_category):
        self.invalid_category = invalid_category

    def __repr__(self):
        return "Category {} can't be parent because it's endpoint.".format(self.invalid_category)

    def __str__(self):
        return "Category {} can't be parent because it's endpoint.".format(self.invalid_category)
