from rest_framework import serializers
from .models import CsvFileInference


class CleanerSerializer(serializers.Serializer):
    document = serializers.FileField()
    chunk_size = serializers.IntegerField(default=1000000)
    sample_size_per_chunk = serializers.IntegerField(default=1000000)
    random_state = serializers.IntegerField(default=0)
    valid_threshold = serializers.FloatField(default=0.5)
    category_threshold = serializers.FloatField(default=0.5)


class ColumnUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    new_dtype = serializers.CharField(max_length=50)


class CsvFileInferenceUpdateSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    columns = ColumnUpdateSerializer(many=True)

    def update_columns_data(self, instance, validated_data):
        columns_data = instance.get_columns_data()

        for update in validated_data['columns']:
            for column_data in columns_data:
                if column_data['name'] == update['name']:
                    column_data['user_defined_type'] = update['new_dtype']
                    break

        instance.set_columns_data(columns_data)
        instance.save()
        return instance


class CsvFileInferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvFileInference
        fields = ['file_name', 'columns_data']
