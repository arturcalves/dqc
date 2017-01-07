"""dqc_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from dqc import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dataset/$', views.dataset_list, name="dataset_list"),
    url(r'^dataset/new$', views.dataset_new, name="dataset_new"),
    url(r'^dataset/(?P<id>\d+)/$', views.dataset_view, name="dataset_view"),
    url(r'^datatable/new$', views.datatable_new, name="datatable_new"),
    url(r'^datatable/edit$', views.datatable_edit, name="datatable_edit"),
    url(r'^datatable/(?P<id>\d+)/$', views.datatable_view, name="datatable_view"),

    url(r'^datacolumn/new$', views.datacolumn_new, name="datacolumn_new"),
    url(r'^datacolumn/edit$', views.datacolumn_edit, name="datacolumn_edit"),

    url(r'^datacolumnconstraint/save$', views.datacolumnconstraint_save, name="datacolumnconstraint_save"),
    url(r'^datacolumnconstraint/ajaxsave$', views.datacolumnconstraint_ajaxsave, name="datacolumnconstraint_ajaxsave"),

    url(r'^dataconstraintsfromtype/(?P<id>\d+)/$', views.dataconstraintsfromtype, name="dataconstraintsfromtype"),

    url(r'^dataset/(?P<id>\d+)/evaluation/new$', views.evaluation_new, name="evaluation_new"),
    url(r'^dataset/(?P<id>\d+)/evaluation/$', views.evaluation_list, name="evaluation_list"),
    url(r'^dataset/(?P<id>\d+)/evaluation/(?P<id_evaluation>\d+)$', views.evaluation_view, name="evaluation_view"),

    url(r'^admin/', admin.site.urls)
]
