from rest_framework import serializers
from .models import User, Role, OrganizationalUnit, MenuPermission


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class MenuPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuPermission
        fields = '__all__'


class OrganizationalUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationalUnit
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    menu_permissions = MenuPermissionSerializer(many=True, read_only=True)
    organizational_unit = OrganizationalUnitSerializer(read_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'roles', 'menu_permissions', 'organizational_unit', 'first_name', 'last_name', 'is_active')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)
    menu_permissions = serializers.PrimaryKeyRelatedField(queryset=MenuPermission.objects.all(), many=True, required=False)
    organizational_unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationalUnit.objects.all())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'roles', 'menu_permissions', 'organizational_unit', 'first_name', 'last_name')
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        roles = validated_data.pop('roles')
        menu_permissions = validated_data.pop('menu_permissions', [])
        organizational_unit = validated_data.pop('organizational_unit')
        user = User.objects.create(organizational_unit=organizational_unit, **validated_data)
        user.set_password(password)
        user.save()
        user.roles.set(roles)
        user.menu_permissions.set(menu_permissions)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()