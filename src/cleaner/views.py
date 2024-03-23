import os

from rest_framework import views, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from .serializers import CleanerSerializer, CsvFileInferenceUpdateSerializer, CsvFileInferenceSerializer
from .inferencer import DataFrameTypeInferencer
from .entities import ColumnInference, InferenceResult
from .models import CsvFileInference


def get_file_path(file_name):
    return os.path.join(settings.CSV_FILES_DIR, file_name)


def api_documentation(request):
    return render(request, 'csv_cleaner/api_documentation.html')


import os

from rest_framework import views, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.http import FileResponse
from django.urls import reverse
from django.http import JsonResponse

from .serializers import CleanerSerializer, CsvFileInferenceUpdateSerializer, CsvFileInferenceSerializer
from .inferencer import DataFrameTypeInferencer
from .entities import ColumnInference, InferenceResult
from .models import CsvFileInference


def get_file_path(file_name):
    return os.path.join(settings.CSV_FILES_DIR, file_name)


def api_documentation(request):
    return render(request, 'csv_cleaner/api_documentation.html')


class FetchFileMetadataView(views.APIView):
    def get(self, request, file_name):
        # Check if the file metadata exists in the database
        try:
            file_metadata = CsvFileInference.objects.get(file_name=file_name)
        except CsvFileInference.DoesNotExist:
            return Response({"error": "File metadata not found."}, status=404)

        file_path = os.path.join(settings.CSV_FILES_DIR, file_name)

        if not os.path.exists(file_path):
            return Response({"error": "File not found."}, status=404)

        # Instead of sending the file content, send a URL to download the file
        download_url = request.build_absolute_uri(reverse('fetch-file-content', args=[file_name]))

        # Retrieve and send metadata
        metadata = file_metadata.get_columns_data()

        # Construct response data with download URL and metadata
        response_data = {
            "download_url": download_url,
            "metadata": metadata
        }

        return JsonResponse(response_data)


class FetchFileContentView(views.APIView):
    def get(self, request, file_name):
        file_path = os.path.join(settings.CSV_FILES_DIR, file_name)

        if not os.path.exists(file_path):
            return Response({"error": "File not found."}, status=404)

        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()

        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ListCsvFilesView(views.APIView):
    def get(self, request):
        print(request)

        # Query all CsvFileInference instances
        csv_files = CsvFileInference.objects.all()

        print(csv_files)

        # Serialize the query results
        serializer = CsvFileInferenceSerializer(csv_files, many=True)
        # Return the serialized data
        return Response(serializer.data)


class UpdateColumnDtypeView(views.APIView):
    def post(self, request):
        serializer = CsvFileInferenceUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                csv_file_inference = CsvFileInference.objects.get(file_name=serializer.validated_data['file_name'])
                serializer.update_columns_data(csv_file_inference, serializer.validated_data)

                return Response(status=status.HTTP_204_NO_CONTENT)
            except CsvFileInference.DoesNotExist:
                return Response({"message": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CsvTypeInferView(views.APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request: Request) -> Response:
        print("Request Content-Type:", request.content_type)

        serializer = CleanerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract file from request
        file = request.FILES['document']
        config = {
            'chunk_size': serializer.validated_data['chunk_size'],
            'sample_size_per_chunk': serializer.validated_data['sample_size_per_chunk'],
            'random_state': serializer.validated_data['random_state'],
            'valid_threshold': serializer.validated_data['valid_threshold'],
            'category_threshold': serializer.validated_data['category_threshold'],
        }

        # Save the uploaded file temporarily
        temp_file_path = default_storage.save("temp_files/" + file.name, ContentFile(file.read()))

        # Ensure CSV_FILES_DIR exists
        os.makedirs(settings.CSV_FILES_DIR, exist_ok=True)

        # Define file path
        file_path = os.path.join(settings.CSV_FILES_DIR, file.name)

        # Save the uploaded file, overriding if it exists
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            # Initialize DataFrameTypeInferencer with the file path
            inference = DataFrameTypeInferencer(file_path=default_storage.path(temp_file_path), **config)
            inference_result = inference.infer_and_convert()

            # Mapping of pandas data types to friendly names
            dtype_to_friendly_name = {
                'int8': 'integer', 'int16': 'integer', 'int32': 'integer', 'int64': 'integer',
                'float16': 'float', 'float32': 'float', 'float64': 'float',
                'complex64': 'complex', 'complex128': 'complex',
                'object': 'text', 'bool': 'boolean',
                'category': 'category', 'datetime64[ns]': 'datetime', 'timedelta[ns]': 'timedelta'
            }

            # Prepare response data by iterating over DataFrame columns and their data types
            response_data = {
                "columns": [
                    {
                        "name": col,
                        "pandas_type": str(inference_result[col].dtype),
                        "friendly_name": dtype_to_friendly_name.get(str(inference_result[col].dtype).lower(), 'unknown')
                    }
                    for col in inference_result.columns
                ]
            }

            obj, created = CsvFileInference.objects.get_or_create(file_name=file.name)
            obj.set_columns_data(response_data['columns'])
            obj.save()

        finally:
            # Clean up: delete the temporary file
            default_storage.delete(temp_file_path)

        return Response(data=response_data, status=status.HTTP_202_ACCEPTED)
