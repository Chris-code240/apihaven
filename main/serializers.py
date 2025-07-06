import rest_framework.serializers as serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model 

User = get_user_model()
class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
        