from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):  # Исправлено: Custom (было Castom), Obtain (было Obtian)
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['warehouse_id'] = str(user.warehouse_id) if user.warehouse_id else None
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'role': self.user.role,
            'full_name': self.user.full_name,
        }
        return data