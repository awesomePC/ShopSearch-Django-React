from rest_framework import serializers
from .models import Items, SearchHistory

class ItemsSerializer(serializers.ModelSerializer):
    # Image = serializers.FileField(max_length=100000,
    #     allow_empty_file=False,
    #     use_url=True )
    class Meta:
        model = Items
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'