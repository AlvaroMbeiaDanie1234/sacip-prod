from rest_framework import serializers
from .models import Suspect, CameraFeed, RecognitionResult, Alert


class SuspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspect
        fields = '__all__'


class CameraFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraFeed
        fields = '__all__'


class RecognitionResultSerializer(serializers.ModelSerializer):
    suspect_name = serializers.CharField(source='suspect.full_name', read_only=True)
    suspect_nickname = serializers.CharField(source='suspect.nickname', read_only=True)
    camera_name = serializers.CharField(source='camera_feed.name', read_only=True)
    
    class Meta:
        model = RecognitionResult
        fields = '__all__'
        read_only_fields = ('suspect_name', 'suspect_nickname', 'camera_name')


class AlertSerializer(serializers.ModelSerializer):
    suspect_name = serializers.CharField(source='suspect.full_name', read_only=True)
    suspect_nickname = serializers.CharField(source='suspect.nickname', read_only=True)
    suspect_danger_level = serializers.CharField(source='suspect.dangerous_level', read_only=True)
    camera_name = serializers.CharField(source='camera_feed.name', read_only=True)
    camera_location = serializers.CharField(source='camera_feed.location', read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = (
            'timestamp', 
            'suspect_name', 
            'suspect_nickname', 
            'suspect_danger_level',
            'camera_name',
            'camera_location'
        )