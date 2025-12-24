from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """
    Model representing user roles in the system.
    """
    ROLE_CHOICES = [
        ('operador', 'Operador'),
        ('chefe', 'Chefe'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    ]
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()


class MenuPermission(models.Model):
    """
    Model representing menu permissions for users.
    """
    MENU_CHOICES = [
        ('consulta_documentos', 'Consulta de Documentos'),
        ('alvos_investigacao', 'Alvos Sob Investigação'),
        ('informacoes_suspeitas', 'Informações Suspeitas'),
        ('cruzamento_dados', 'Cruzamento de Dados'),
        ('i2_analysis', 'i2 Analysis Notebook'),
        ('analise_media_osint', 'Análise de Média e OSINT'),
        ('monitoramento_redes_sociais', 'Monitoramento de Redes Sociais'),
        ('monitoramento_viaturas', 'Monitoramento de Viaturas'),
        ('facecheck', 'Facecheck'),
        ('vigilancia', 'Vigilância'),
        ('alertas_sos', 'Alertas SOS'),
        ('relatorios', 'Relatórios'),
        ('power_bi', 'Power BI'),
        ('utilizadores', 'Utilizadores'),
    ]
    
    name = models.CharField(max_length=50, choices=MENU_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()


class OrganizationalUnit(models.Model):
    """
    Model representing organizational units/services in the system.
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    core_service_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=50)
    description = models.TextField()
    active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom user model with role-based permissions.
    """
    email = models.EmailField(unique=True)
    roles = models.ManyToManyField(Role, related_name='users')
    menu_permissions = models.ManyToManyField(MenuPermission, related_name='users', blank=True)
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter(name=role_name).exists()
    
    def has_menu_permission(self, menu_name):
        """Check if user has a specific menu permission."""
        return self.menu_permissions.filter(name=menu_name).exists()
    
    def is_operador(self):
        return self.has_role('operador')
    
    def is_chefe(self):
        return self.has_role('chefe')
    
    def is_admin(self):
        return self.has_role('admin')
    
    def is_superadmin(self):
        return self.has_role('superadmin')