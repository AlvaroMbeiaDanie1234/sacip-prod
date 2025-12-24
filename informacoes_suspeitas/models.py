from django.db import models
from users.models import User
from facial_recognition.models import Suspect


class InformacaoSuspeita(models.Model):
    """
    Model representing suspicious information in the system.
    """
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    fonte = models.CharField(max_length=100)
    nivel_confianca = models.IntegerField(default=1)  # 1-10 scale
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='informacoes_suspeitas')
    ativo = models.BooleanField(default=True)
    suspect = models.ForeignKey(Suspect, on_delete=models.SET_NULL, null=True, blank=True, related_name='suspect_informations')
    
    class Meta:
        verbose_name = "Informação Suspeita"
        verbose_name_plural = "Informações Suspeitas"
    
    def __str__(self):
        if self.suspect:
            return f"{self.titulo} - {self.suspect.full_name}"
        return self.titulo