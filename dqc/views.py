from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

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
        return render(request, 'data_set_new.html', {"drivers": CONNECTION_DRIVER_CHOICES})
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
    tables = []
    datatables_names = [dt.name for dt in datatables]
    for (table_name) in get_table_list(dataset):
        if table_name not in datatables_names:
            tables += [(table_name)]
    return render(request, 'data_set_view.html',
                  {"dataset": dataset, "datatables": datatables, "tables": tables})


def datatable_new(request):
    if request.method == 'POST':
        datatable = DataTable(name=request.POST.get("table", ""),
                              description=request.POST.get("description", ""),
                              data_set=DataSet.objects.get(id=request.POST.get("dataset_id", "")))
        datatable.save()

        for (column_name, column_type) in get_column_list(datatable):

            datacolumn = DataColumn(name=column_name,
                                    description="",
                                    data_table=datatable,
                                    data_type=DataType.objects.get(name=column_type))
            datacolumn.save()


        messages.success(request, 'DataTable Inserted')
        return redirect('dataset_view', datatable.data_set.id)
    return redirect('index')


@csrf_exempt
def datatable_edit(request):
    response_data = {}
    if request.method == 'POST':
        datatable = DataTable.objects.get(id=request.POST.get("pk", ""))
        if request.POST.get("name", "") == 'description':
            datatable.description = request.POST.get("value", "")
        datatable.save()
        response_data['result'] = 'sucess'
    return JsonResponse(response_data)

def datatable_view(request, id):
    datatable = DataTable.objects.get(id=id)
    datacolumns = DataColumn.objects.filter(data_table=datatable).order_by('name')
    columns = []
    datacolumns_names = [dc.name for dc in datacolumns]
    for (column_name, column_type) in get_column_list(datatable):
        #print(column_name)
        if column_name not in datacolumns_names:
            columns += [(column_name, column_type)]
    return render(request, 'data_table_view.html',
                  {"datatable": datatable, "datacolumns": datacolumns, "columns": columns })


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

@csrf_exempt
def datacolumn_edit(request):
    response_data = {}
    if request.method == 'POST':
        datacolumn = DataColumn.objects.get(id=request.POST.get("pk", ""))
        if request.POST.get("name", "") == 'description':
            datacolumn.description = request.POST.get("value", "")
        datacolumn.save()
        response_data['result'] = 'sucess'
    return JsonResponse(response_data)


def dataconstraintsfromtype(request, id):
    constraints = DataValidationConstraint.objects.filter(data_type=DataType.objects.get(id=id))
    constraints_serialized = serializers.serialize('json', constraints, fields='name')
    return JsonResponse(constraints_serialized, safe=False)


def datacolumnconstraint_save(request):
    if request.method == 'POST':
        data_column_constraint_id = request.POST.get("datacolumnconstraint_id", "")
        if data_column_constraint_id:
            datacolumnconstraint = DataColumnConstraint.objects.get(id=data_column_constraint_id)
            datacolumnconstraint.data_column = DataColumn.objects.get(
                id=request.POST.get("column_id", ""))
            datacolumnconstraint.data_validation_constraint = DataValidationConstraint.objects.get(
                id=request.POST.get("validation_constraint_id", ""))
            datacolumnconstraint.argument = request.POST.get("argument", "")
            messages.success(request, 'DataColumnConstraint Updated')
        else:
            datacolumnconstraint = DataColumnConstraint(
                data_column=DataColumn.objects.get(id=request.POST.get("column_id", "")),
                data_validation_constraint=DataValidationConstraint.objects.get(
                    id=request.POST.get("validation_constraint_id", "")),
                argument=request.POST.get("argument", ""))
            messages.success(request, 'DataColumnConstraint Inserted')
        datacolumnconstraint.save()

        return redirect('datatable_view', datacolumnconstraint.data_column.data_table.id)
    return redirect('index')


def datacolumnconstraint_ajaxsave(request):
    response_data = {}
    if request.method == 'POST':
        data_column_constraint_id = request.POST.get("datacolumnconstraint_id", "")
        if data_column_constraint_id != '':
            datacolumnconstraint = DataColumnConstraint.objects.get(id=data_column_constraint_id)
            datacolumnconstraint.data_column = DataColumn.objects.get(
                id=request.POST.get("column_id", ""))
            datacolumnconstraint.data_validation_constraint = DataValidationConstraint.objects.get(
                id=request.POST.get("validation_constraint_id", ""))
            datacolumnconstraint.argument = request.POST.get("argument", "")
        else:
            datacolumnconstraint = DataColumnConstraint(
                data_column=DataColumn.objects.get(id=request.POST.get("column_id", "")),
                data_validation_constraint=DataValidationConstraint.objects.get(
                    id=request.POST.get("validation_constraint_id", "")),
                argument=request.POST.get("argument", ""))
            response_data['result'] = 'updated'
        datacolumnconstraint.save()
        response_data['result'] = 'saved'
        response_data['constraint_id'] = datacolumnconstraint.id
        response_data['constraint_argument'] = datacolumnconstraint.argument
        response_data['data_validation_constraint_id'] = datacolumnconstraint.data_validation_constraint.id
        response_data['data_validation_constraint_name'] = datacolumnconstraint.data_validation_constraint.name
        response_data['data_column_id'] = datacolumnconstraint.data_column.id
        response_data['data_column_name'] = datacolumnconstraint.data_column.name
        response_data['data_type_id'] = datacolumnconstraint.data_column.data_type.id
        response_data['data_type_name'] = datacolumnconstraint.data_column.data_type.name
    else:
        response_data['result'] = 'erro'
    return JsonResponse(response_data)


def __register_evaluation_problem(evaluation, column_constraint, record, message):
    ev_problem = DataSetEvaluationProblem(data_set_evaluation=evaluation,
                                          data_column_constraint=column_constraint,
                                          data_record=record,
                                          message=message)
    ev_problem.save()


def __get_schema(column_constraint):
    constraint = column_constraint.data_validation_constraint.method_to_call
    column = column_constraint.data_column.name
    type = column_constraint.data_column.data_type.name
    argument = column_constraint.argument

    schema_json = ''

    if constraint == 'isNull':
        schema_json = '{"%s":{"nullable":true, "allowed":[]}}' % column
    elif constraint == 'isNotNull':
        schema_json = '{"%s":{"required":true}}' % column

    #Booleans
    elif constraint == 'isTrue':
        schema_json = '{"%s":{"allowed":[true] }}' % column
    elif constraint == 'isFalse':
        schema_json = '{"%s":{"allowed":[false] }}' % column

    #Numbers
    elif constraint == 'isInteger':
        schema_json = '{"%s":{"type":"integer" }}' % column
    elif constraint == 'isFloat':
        schema_json = '{"%s":{"type":"float" }}' % column
    elif constraint == 'isGreaterOrEqualThan':
        schema_json = '{"%s":{"min":%f }}' % (column, float(argument))
    elif constraint == 'isLessOrEqualThan':
        schema_json = '{"%s":{"max":%f }}' % (column, float(argument))

    #DateTimes
    # TODO: testar essas validacoes de datas, e verificar necessidade de cast do argument
    elif constraint == 'isFuture':
        schema_json = '{"%s":{"type":"datetime", "min":"%s" }}' % (column, datetime.now())
    elif constraint == 'isPast':
        schema_json = '{"%s":{"type":"datetime", "max":"%s" }}' % (column, datetime.now())
    elif constraint == 'isBefore':
        schema_json = '{"%s":{"type":"datetime", "max":"%s" }}' % (column, argument)
    elif constraint == 'isAfter':
        schema_json = '{"%s":{"type":"datetime", "min":"%s" }}' % (column, argument)

    #Strings
    elif constraint == 'isEmpty':
        schema_json = '{"%s":{"type":"string", "allowed":[''] }}' % column
    elif constraint == 'isNotEmpty':
        schema_json = '{"%s":{"type":"string", "empty":"False"}}' % column
    elif constraint == 'length':
        schema_json = '{"%s":{"type":"string", "minlength":%d, "maxlength":%d}}' % (column, int(argument), int(argument))
    elif constraint == 'maxLength':
        schema_json = '{"%s":{"type":"string", "maxlength":%d}}' % (column, int(argument))
    elif constraint == 'minLength':
        schema_json = '{"%s":{"type":"string", "minlength":%d}}' % (column, int(argument))
    elif constraint == 'isUpperCase':
        schema_json = '{"%s":{"type":"string", "regex":"^[A-Z0-9\\\\s]*$"}}' % column
    elif constraint == 'isLowerCase':
        schema_json = '{"%s":{"type":"string", "regex":"^[a-z0-9\\\\s]*$"}}' % column
    elif constraint == 'beginsWith':
        schema_json = '{"%s":{"type":"string", "regex":"^%s.*"}}' % (column, argument)
    elif constraint == 'endsWith':
        schema_json = '{"%s":{"type":"string", "regex":"^.*%s"}}' % (column, argument)
    elif constraint == 'contains':
        schema_json = '{"%s":{"type":"string", "regex":"^.*%s.*"}}' % (column, argument)
    elif constraint == 'notContains':
        schema_json = '{"%s":{"type":"string", "regex":"^((?!%s).)*$"}}' % (column, argument)
    elif constraint == 'matchWithRegex':
        schema_json = '{"%s":{"type":"string", "regex":"%s"}}' % (column, argument)
    elif constraint == 'isNumeric':
        schema_json = '{"%s":{"type":"string", "regex":"^[0-9]+$"}}' % column
    elif constraint == 'isEmail':
        schema_json = '{"%s":{"type":"string", "regex":"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+\\\\.[a-zA-Z.]{2,6}$"}}' % column
    elif constraint == 'isURL':
        schema_json = '{"%s":{"type":"string", "regex":"^(https?:\\\\/\\\\/)?([a-z0-9.-]+)\\\\.([a-z.]{2,6})([\\\\/\\\\w \\\\.-]*)*\\\\/?$"}}' % column
    elif constraint == 'isPhone':
        schema_json = '{"%s":{"type":"string", "regex":"^[0-9\\\\-\\\\+() ]{9,15}$"}}' % column
    elif constraint == 'isCEP':
        schema_json = '{"%s":{"type":"string", "regex":"^[0-9]{2}[.]?[0-9]{3}[-]?[0-9]{3}$"}}' % column
    elif constraint == 'isCPF':
        schema_json = '{"%s":{"type":"string", "regex":"^[0-9]{3}[.]?[0-9]{3}[.]?[0-9]{3}[-]?[0-9]{2}$"}}' % column
    elif constraint == 'isCNPJ':
        schema_json = '{"%s":{"type":"string", "regex":"^[0-9]{2}[.]?[0-9]{3}[.]?[0-9]{3}[\\\\/]?[0-9]{4}[-]?[0-9]{2}$"}}' % column

    elif constraint == 'isEqual':
        if type == 'String':
            schema_json = '{"%s":{"type":"string", "regex":"^%s$"}}' % (column, argument)
        elif type == 'Number':
            schema_json = '{"%s":{"min":%f, "max":%f}}' % (column, float(argument), float(argument))

    elif constraint == 'isNotEqual':
        if type == 'String':
            schema_json = '{"%s":{"type":"string", "regex":"^(?!%s$).*$"}}' % (column, argument)
        elif type == 'Number':
            schema_json = '{"%s":{"type":"float", "forbidden":[%d] }}' % (column, float(argument))

    elif constraint == 'in':
        if type == 'String':
            schema_json = '{"%s":{"type":"string", "allowed":[%s] }}' % (column, argument)
        elif type == 'Number':
            schema_json = '{"%s":{"type":"float", "allowed":[%s] }}' % (column, argument)

    elif constraint == 'notIn':
        if type == 'String':
            schema_json = '{"%s":{"type":"string", "forbidden":[%s] }}' % (column, argument)
        elif type == 'Number':
            schema_json = '{"%s":{"type":"float", "forbidden":[%s] }}' % (column, argument)
    schema = json.loads(schema_json)
    return schema


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):  # handles both date and datetime objects
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


def evaluation_list(request, id):
    data_set = DataSet.objects.get(id=id)
    evaluations = data_set.datasetevaluation_set.order_by('-finished_at')[:10:-1]
    problems_per_quality_dimension = []
    problems_per_table = []
    problems_per_column = []
    if len(evaluations):
        last_evaluation = data_set.datasetevaluation_set.latest('finished_at')
        for dqd in DataQualityDimension.objects.all().order_by('name'):
            problems_per_quality_dimension += [[dqd.name,
                                               DataSetEvaluationProblem.objects.filter(
                                                   data_set_evaluation_id=last_evaluation.id,
                                                   data_column_constraint__data_validation_constraint__data_quality_dimension=dqd.id).count()]]

        for dt in DataTable.objects.filter(data_set=data_set).order_by('name'):
            problems_per_table += [[dt.name,
                                    DataSetEvaluationProblem.objects.filter(
                                                   data_set_evaluation_id=last_evaluation.id,
                                                   data_column_constraint__data_column__data_table=dt.id).count()]]
            if problems_per_table[-1][1] !=0 :
                for dc in DataColumn.objects.filter(data_table=dt).order_by('name'):
                    problems = DataSetEvaluationProblem.objects.filter(
                                                  data_set_evaluation_id=last_evaluation.id,
                                                  data_column_constraint__data_column=dc.id).count()
                    if problems:
                        problems_per_column += [[dt.name, dc.description or dc.name, problems]]


    return render(request, 'data_evaluation_list.html', {"dataset": data_set, "evaluations": evaluations,
                                                         "problems_per_quality_dimension": problems_per_quality_dimension,
                                                         "problems_per_table": problems_per_table,
                                                         "problems_per_column": problems_per_column})


def evaluation_new(request, id):
    data_set = DataSet.objects.get(id=id)

    # cria o DataSetEvaluation
    ev = DataSetEvaluation(data_set=data_set, found_problems=0)
    ev.save()

    # Pega lista dos DataTables que serão avaliados
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
                (is_valid, errors) = check_is_valid(record_dict, schema)
                if not is_valid:
                    ev.found_problems += 1
                    if not record_object.id:
                        record_object.save()
                    __register_evaluation_problem(ev, col_constraint, record_object, errors)

    ev.save()

    return redirect('evaluation_list', id)

def evaluation_view(request, id, id_evaluation):
    dataset = DataSet.objects.get(id=id)
    evaluation = DataSetEvaluation.objects.get(id=id_evaluation)
    datatables = DataTable.objects.filter(data_set=dataset)

    evaluation_problems = DataSetEvaluationProblem.objects.filter(data_set_evaluation=evaluation)

    datarecord_per_table = []
    for dt in datatables:
        datarecord_per_table += [(dt.name, DataRecord.objects.filter(data_table=dt, datasetevaluationproblem__data_set_evaluation=evaluation))]

    return render(request, 'data_evaluation_view.html',
                  {"dataset":dataset, "evaluation": evaluation, "datatables": datatables, 'datarecord_per_table': datarecord_per_table, 'problems':evaluation_problems})


