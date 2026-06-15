from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # TokenObtainPairView (с большой V)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CustomTokenObtainPairSerializer  # правильный импорт


class LoginView(TokenObtainPairView):  # TokenObtainPairView (исправлено: View с большой буквы, не view)
    serializer_class = CustomTokenObtainPairSerializer  # CustomTokenObtainPairSerializer (исправлено)
    permission_classes = [AllowAny]

class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()  # blacklist (исправлено: blaklist -> blacklist)
            return Response({'detail': 'Logged out'}, status=200)  # добавлен return и статус 200
        except Exception as e:  # лучше указывать конкретное исключение
            return Response({'detail': 'Invalid token'}, status=400)