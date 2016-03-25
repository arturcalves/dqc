import json
from cerberus import Validator


def is_valid(record, schema):
     v = Validator(allow_unknown=True)
     return v.validate(record, schema)
