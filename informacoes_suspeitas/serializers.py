from rest_framework import serializers
from .models import InformacaoSuspeita
from facial_recognition.models import Suspect


class InformacaoSuspeitaSerializer(serializers.ModelSerializer):
    # Include suspect details in the serialization
    suspect_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = InformacaoSuspeita
        fields = '__all__'
        read_only_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    
    def get_suspect_details(self, obj):
        if obj.suspect:
            suspect = obj.suspect
            photo_urls = []
            if suspect.photo_paths:
                try:
                    import json
                    photo_paths = json.loads(suspect.photo_paths)
                    # Get the backend URL from settings
                    from django.conf import settings
                    backend_url = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'http://localhost:8000'
                    if backend_url == '*':
                        backend_url = 'http://localhost:8000'  # Default for development
                    photo_urls = [f"{backend_url}/media/{path}" for path in photo_paths if path]
                except Exception:
                    pass
            
            return {
                'id': suspect.id,
                'full_name': suspect.full_name,
                'nickname': suspect.nickname,
                'dangerous_level': suspect.dangerous_level,
                'dangerous_color': suspect.dangerous_color,
                'photo_urls': photo_urls,
            }
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add the photo URL from the InformacaoSuspeita model if it exists
        if instance.photo:
            from django.conf import settings
            backend_url = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'http://localhost:8000'
            if backend_url == '*':
                backend_url = 'http://localhost:8000'  # Default for development
            data['photo_url'] = f"{backend_url}/media/{instance.photo}"
        return data