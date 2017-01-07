from django import template
register = template.Library()

@register.filter
def record_column_value(record, column):
    return record.get_value(column)