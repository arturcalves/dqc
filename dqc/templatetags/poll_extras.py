from django import template
register = template.Library()

@register.filter
def record_column_value(record, column):
    return record.get_value(column)

@register.filter
def problem_message(problem):
    return problem.data_column_constraint.data_validation_constraint.description + ' ' + problem.data_column_constraint.argument