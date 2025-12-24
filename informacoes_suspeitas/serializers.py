from rest_framework import serializers
from .models import InformacaoSuspeita


class InformacaoSuspeitaSerializer(serializers.ModelSerializer):
    # Include suspect details in the serialization
    suspect_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = InformacaoSuspeita
        fields = '__all__'
        read_only_fields = ('data_criacao', 'data_atualizacao', 'criado_por')
    
    def get_suspect_details(self, obj):
        if obj.suspect:
            return {
                'id': obj.suspect.id,
                'full_name': obj.suspect.full_name,
                'nickname': obj.suspect.nickname,
                'dangerous_level': obj.suspect.dangerous_level,
                'dangerous_color': obj.suspect.dangerous_color,
            }
        return None