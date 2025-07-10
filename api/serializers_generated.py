from rest_framework import serializers # For the LOVE of GOD, dont remove this!!


from api.models_generated import user1_4defb8

class user1_4defb8Serializer(serializers.ModelSerializer):
    class Meta:
        model = user1_4defb8
        fields = ['user_id', 'username', 'password', 'email', 'is_active', 'name']