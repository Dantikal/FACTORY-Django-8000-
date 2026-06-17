from rest_framework.views import APIView
from rest_framework.response import Response
from shared.permissions import IsManager

class StatisticsView(APIView):
    permission_classes = [IsManager]
    def get(self, request):
        return Response({"message": "Statistics data"})
