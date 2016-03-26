from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from .models import *
from .util_classes.connection import *
from .util_classes.validation import *


def index(request):
    return redirect('dataset_list')


def dataset_try_connect(request):
    dataset = DataSet(name=request.POST.get("name", ""),
                      connection_driver=request.POST.get("driver", ""),
                      connection_server=request.POST.get("server", ""),
                      connection_port=request.POST.get("port", ""),
                      connection_database=request.POST.get("database", ""),
                      connection_user=request.POST.get("user", ""),
                      connection_password=request.POST.get("password", ""))
    return is_connecting(dataset)


def dataset_list(request):
    datasets = DataSet.objects.all()
    return render(request, 'data_set_list.html', {"datasets": datasets})


def dataset_new(request):
    if request.method == 'GET':
        return render(request, 'data_set_new.html')
    elif request.method == 'POST':
        dataset = DataSet(name=request.POST.get("name", ""),
                          description=request.POST.get("description", ""),
                          connection_driver=request.POST.get("driver", ""),
                          connection_server=request.POST.get("server", ""),
                          connection_port=request.POST.get("port", ""),
                          connection_database=request.POST.get("database", ""),
                          connection_user=request.POST.get("user", ""),
                          connection_password=request.POST.get("password", ""))
        dataset.save()
        messages.success(request, 'DataSet Inserted')
        return redirect('dataset_list')


def dataset_view(request, id):
    dataset = DataSet.objects.get(id=id)
    datatables = DataTable.objects.filter(data_set=dataset)
    return render(request, 'data_set_view.html',
                  {"dataset": dataset, "datatables": datatables, "tables": get_table_list(dataset)})


def datatable_new(request):
    if request.method == 'POST':
        datatable = DataTable(name=request.POST.get("table", ""),
                              description=request.POST.get("description", ""),
                              data_set=DataSet.objects.get(id=request.POST.get("dataset_id", "")))
        datatable.save()
        messages.success(request, 'DataTable Inserted')
        return redirect('dataset_view', datatable.data_set.id)
    return redirect('index')


def datatable_view(request, id):
    datatable = DataTable.objects.get(id=id)
    datacolumns = DataColumn.objects.filter(data_table=datatable)
    return render(request, 'data_table_view.html',
                  {"datatable": datatable, "datacolumns": datacolumns, "columns": get_column_list(datatable)})


def datacolumn_new(request):
    if request.method == 'POST':
        try:
            (name, type) = request.POST.get("column", "").split(" ")
        except:
            (name, type) = ("", "String")
        datacolumn = DataColumn(name=name,
                                description=request.POST.get("description", ""),
                                data_table=DataTable.objects.get(id=request.POST.get("datatable_id", "")),
                                data_type=DataType.objects.get(name=type))
        datacolumn.save()
        messages.success(request, 'DataColumn Inserted')
        return redirect('datatable_view', datacolumn.data_table.id)
    return redirect('index')


def dataconstraintsfromtype(request, id):
    constraints = DataValidationConstraint.objects.filter(data_type=DataType.objects.get(id=id))
    constraints_serialized = serializers.serialize('json', constraints, fields='name')
    return JsonResponse(constraints_serialized, safe=False)


def datacolumnconstraint_new(request):
    if request.method == 'POST':
        datacolumnconstraint = DataColumnConstraint(
            data_column=DataColumn.objects.get(id=request.POST.get("datacolumn_id", "")),
            data_validation_constraint=DataValidationConstraint.objects.get(
                id=request.POST.get("dataconstraint_id", "")),
            validation_schema=request.POST.get("schema", ""))
        datacolumnconstraint.save()
        messages.success(request, 'DataColumnConstraint Inserted')
        return redirect('datatable_view', datacolumnconstraint.data_column.data_table.id)
    return redirect('index')


def __register_evaluation_problem(evaluation, column_constraint, record, message):
    ev_problem = DataSetEvaluationProblem(data_set_evaluation=evaluation,
                                          data_column_constraint=column_constraint,
                                          data_record=record,
                                          message=message)
    ev_problem.save()


def __get_schema(column_constraint):
    constraint = column_constraint.data_validation_constraint.name
    column = column_constraint.data_column.name
    argument = column_constraint.arguments

    schema_json = ''
    if constraint == 'isNotNull':
        schema_json = '{"%s":{"required":true}}' % column
    elif constraint == 'in':
        schema_json = '{"%s":{"allowed": [] }}' % (column, argument)

    schema = json.loads(schema_json)
    return schema


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'): #handles both date and datetime objects
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


def evaluation_new(request, id):
    data_set = DataSet.objects.get(id=id)

    #cria o DataSetEvaluation
    ev = DataSetEvaluation(data_set=data_set, found_problems=0)
    ev.save()

    #Pega lista dos DataTables que serão avaliados
    datatables = DataTable.objects.filter(data_set=data_set)

    db = MyDB(data_set)


    for datatable in datatables:
        results = db.query('SELECT * FROM %s ;' % datatable.name)

        # lista com o nome de cada coluna da consulta
        cols = [x[0] for x in results.description]

        # lista com todos os registros encontrados
        rows = [x for x in results]

        col_constraints = []
        datacolumns = DataColumn.objects.filter(data_table=datatable)
        for datacolumn in datacolumns:
            datacolumnconstraints = DataColumnConstraint.objects.filter(data_column=datacolumn)
            for datacolumnconstraint in datacolumnconstraints:
                schema = __get_schema(datacolumnconstraint)
                col_constraints += [(datacolumnconstraint, schema)]

        for row in rows:
            # cria um dicionario para cada registro
            record_dict = {}
            for prop, val in zip(cols, row):
                record_dict[prop] = val

            record_json = json.dumps(record_dict, sort_keys=True, cls=JSONEncoder)
            record_object = DataRecord(data_table=datatable,
                                       record=record_json)

            for (col_constraint, schema) in col_constraints:
                # avalia cada registro
                if not is_valid(record_dict, schema):
                    ev.found_problems += 1
                    if not record_object.id:
                        record_object.save()
                    __register_evaluation_problem(ev, datacolumnconstraint, record_object, 'Problema Encontrado')

    ev.save()

    return redirect('dataset_list')
