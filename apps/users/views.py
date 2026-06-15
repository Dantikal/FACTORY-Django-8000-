from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_siplejwt.views import TokenObtainPairview, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CastomTokenObtianPairSerializer


class LoginView(TokenObtainPairview):
    serializer_class = CastomTokenObtianPairSerializer
    permission_classes = [AllowAny]

class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blaklist({'detail': 'Logged out'})

        except:
            return Response({'detail': 'Invalid token'}, status=400)