from django.urls import path

from cleaner import views
from .views import api_documentation


urlpatterns = [
    path(r"type-infer/", views.CsvTypeInferView.as_view(), name="cleaner-type-infer"),
    path(r"update-dtype/", views.UpdateColumnDtypeView.as_view(), name="update-column-dtype"),
    path(r"documentation/", api_documentation, name='api_documentation'),
    path(r"list-csv-files/", views.ListCsvFilesView.as_view(), name='list-csv-files'),
    path(r"fetch-file-content/<str:file_name>/", views.FetchFileContentView.as_view(), name='fetch-file-content'),
    path(r"fetch-file-metadata/<str:file_name>/", views.FetchFileMetadataView.as_view(), name='fetch-file-metadata'),
]
