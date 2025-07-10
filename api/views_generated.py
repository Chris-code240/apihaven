from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# For the LOVE of GOD, dont remove these !!


from api.models_generated import user1_4defb8
from api.serializers_generated import user1_4defb8Serializer

class user1_4defb8View(APIView):
    def get(self, request):
        queryset = user1_4defb8.objects.all()
        serializer = user1_4defb8Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user1_4defb8Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)