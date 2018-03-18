class TypeRegistry(object):

    def __init__(self):
        self.data = {}

    def registry(self, model_cls, record_type):
        self.data[model_cls] = record_type

    def __iter__(self):
        return self.data.items().__iter__()

    def __getitem__(self, item):
        return self.data[item]

    def get_type(self, obj):
        return self.data[obj.__class__]

    def __contains__(self, item):
        return item in self.data

record_type_registry = TypeRegistry()
