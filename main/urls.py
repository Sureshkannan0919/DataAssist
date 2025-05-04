from django.urls import path
from . import views
from .views.signin import Login
from .views.signup import Signup
from .views.connection import ConnectionView
from .views.history import HistoryView
from .views.visualization import VisualizationView
from .views.how_to_use import HowToUseView
from .views.queryhelper import QueryHelper


urlpatterns = [
    path('',ConnectionView.connection,),
    path('home/', ConnectionView.connection, name='home'),
    path('queryhelper/',QueryHelper.query_helper,name='queryhelper'),
    path('history/',HistoryView.view_history,name='history'),
    path('save_history',HistoryView.save_history,name='save_history'),
    path('visualization/',VisualizationView.visualization,name='visualization'),
    path('how_to_use/',HowToUseView.how_to_use,name='how_to_use'),
    path('signup/',Signup.as_view(),name='signup'),
    path('signin/',Login.as_view(),name='signin'),
    path('logout/',Login.logout,name='logout'),
    path('process-url/',ConnectionView.process_url_view,name='url'),
    path('upload_file/',ConnectionView.upload_file,name='url'),
    path('get_databse/',ConnectionView.get_database,name="get_database"),
    path('process_selection/',ConnectionView.process_selection,name='process_selection'),
    path('get_tabel/',ConnectionView.get_tabel,name='get_tabel'),
    path('tb_selection/',ConnectionView.tb_selection,name='tb_selection'),
    path('get_sample/',ConnectionView.get_sample,name="get_sample"),
    path('get-dataframe/', QueryHelper.get_dataframe, name='get_dataframe'),
    path('query_response/',QueryHelper.query_response,name="query_response"),
    path('disconnect/',ConnectionView.disconnect,name='disconnect'),
    path('get_database_type/',ConnectionView.get_database_type,name='get_database_type'),
    path('get_connection_parameters/',ConnectionView.get_connection_parameters,name='get_connection_parameters'),
    path('pandas_sample/',ConnectionView.pandas_sample,name='pandas_sample'),
    path('generate_visualization/',VisualizationView.generate_visualization,name='generate_visualization'),
]