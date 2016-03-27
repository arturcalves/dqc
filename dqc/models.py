from django.db import models
from .util_classes.connection import *


class DataQualityDimension(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name


class DataType(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name


class DataValidationConstraint(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    data_quality_dimension = models.ManyToManyField(DataQualityDimension)
    data_type = models.ManyToManyField(DataType)
    method_to_call = models.CharField(max_length=200)
    arguments_number = models.IntegerField()
    arguments_type = models.ForeignKey(DataType, null=True, related_name='argument_type')

    def __str__(self):
        return self.name


class DataSet(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    connection_driver = models.CharField(max_length=200, choices=CONNECTION_DRIVER_CHOICES)
    connection_server = models.CharField(max_length=200)
    connection_port = models.CharField(max_length=200)
    connection_database = models.CharField(max_length=200)
    connection_user = models.CharField(max_length=200)
    connection_password = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def connection_string(self):
        return '{'+self.connection_driver+'}:'+\
               self.connection_server+':'+\
               self.connection_port+'/'+\
               self.connection_database+\
               ';user=\''+self.connection_user+'\''+\
               ';password=\''+self.connection_password+'\''

    def count_tables(self):
        return self.datatable_set.all().count()

    def count_columns(self):
        count = 0
        for c in self.datatable_set.all():
            count += c.count_columns()
        return count

    def count_constraints(self):
        count = 0
        for c in self.datatable_set.all():
            count += c.count_constraints()
        return count

    def __str__(self):
        return self.name


class DataTable(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    data_set = models.ForeignKey(DataSet)
    created_at = models.DateTimeField(auto_now_add=True)

    def count_columns(self):
        return self.datacolumn_set.all().count()

    def count_constraints(self):
        count = 0
        for c in self.datacolumn_set.all():
            count += c.count_constraints()
        return count


    def __str__(self):
        return self.name


class DataColumn(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    data_table = models.ForeignKey(DataTable)
    data_type = models.ForeignKey(DataType)
    created_at = models.DateTimeField(auto_now_add=True)

    def count_constraints(self):
        return self.datacolumnconstraint_set.all().count()

    def __str__(self):
        return self.name


class DataColumnConstraint(models.Model):
    data_column = models.ForeignKey(DataColumn)
    data_validation_constraint = models.ForeignKey(DataValidationConstraint)
    created_at = models.DateTimeField(auto_now_add=True)
    argument = models.TextField()

    def __str__(self):
        return self.data_column+'-'+self.data_validation_constraint


class DataRecord(models.Model):
    data_table = models.ForeignKey(DataTable)
    record = models.TextField()

    def __str__(self):
        return self.data_table+'('+self.id+')'


class DataSetEvaluation(models.Model):
    data_set = models.ForeignKey(DataSet)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(auto_now=True)
    found_problems = models.IntegerField(default=0)

    def __str__(self):
        return 'Evaluation '+self.id+'('+self.data_set+')'


class DataSetEvaluationProblem(models.Model):
    data_set_evaluation = models.ForeignKey(DataSetEvaluation)
    data_column_constraint = models.ForeignKey(DataColumnConstraint)
    data_record = models.ForeignKey(DataRecord, null=True)
    message = models.TextField()

    def __str__(self):
        return 'Problem '+self.id
