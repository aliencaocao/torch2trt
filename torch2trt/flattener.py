import copy


def _make_schema_from_value(value, type, size=0):
    if isinstance(value, type):
        return size, size + 1
    elif isinstance(value, list) or isinstance(value, tuple):
        schema = []
        for child_value in value:
            child_schema, size = _make_schema_from_value(child_value, type, size)
            schema.append(child_schema)
        if isinstance(value, tuple):
            schema = tuple(schema)
        return schema, size
    elif isinstance(value, dict):
        schema = {}
        for child_key, child_value in value.items():
            child_schema, size = _make_schema_from_value(child_value, type, size)
            schema[child_key] = child_schema
        return schema, size
    else:
        return None, size


class Flattener(object):
    
    def __init__(self, schema, size):
        self._schema = schema
        self._size = size

    @staticmethod
    def from_value(value, type):
        return Flattener(*_make_schema_from_value(value, type))
    
    @staticmethod
    def from_dict(x):
        return Flattener.from_schema(x['schema'], x['size'])

    def dict(self):
        return {'schema': self.schema, 'size': self.size}

    @property
    def schema(self):
        return self._schema

    @property
    def size(self):
        return self._size

    def __len__(self):
        return self._size

    def _flatten(self, value, result):
        if isinstance(self._schema, int):
            result[self._schema] = value
        elif isinstance(self._schema, list) or isinstance(self._schema, tuple):
            for child_value, child_schema in zip(value, self._schema):
                Flattener(child_schema, self.size)._flatten(child_value, result)
        elif isinstance(self._schema, dict):
            for key in self._schema.keys():
                child_value = value[key]
                child_schema = self._schema[key]
                Flattener(child_schema, self.size)._flatten(child_value, result)

    def flatten(self, value):
        result = [None for i in range(self.size)]
        self._flatten(value, result)
        return result

    def unflatten(self, flattened):
        if isinstance(self._schema, int):
            return flattened[self._schema]
        elif isinstance(self._schema, list) or isinstance(self._schema, tuple):
            result = []
            for child_schema in self._schema:
                result.append(Flattener(child_schema, self.size).unflatten(flattened))
            if isinstance(self._schema, tuple):
                result = tuple(result)
            return result
        elif isinstance(self._schema, dict):
            result = {}
            for child_key, child_schema in self._schema.items():
                result[child_key] = Flattener(child_schema, self.size).unflatten(flattened)
            return result
        else:
            return None