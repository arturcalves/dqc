import json
from cerberus import Validator


def check_is_valid(record, schema):
    v = Validator(allow_unknown=True, ignore_none_values=True)
    valid = v.validate(record, schema)
    errors = v.errors
    return (valid,errors)