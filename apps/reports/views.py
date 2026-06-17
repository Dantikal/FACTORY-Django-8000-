from rest_framework.views import APIView
from rest_framework.response import Response
from shared.permissions import IsManager, IsAccountant, IsAdmin

class ReportListView(APIView):
    permission_classes = [IsManager | IsAccountant | IsAdmin]
    def get(self, request):
        return Response({"message": "Reports list"})
 Broadway: class ReportListView(APIView):
    permission_classes = [IsManager | IsAccountant | IsAdmin]
