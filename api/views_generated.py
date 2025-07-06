from rest_framework.views import APIView
from rest_framework.response import Response
# For the LOVE of GOD, dont remove these !!



from api.models_generated import user_model_7cc812
from api.serializers_generated import user_model_7cc812Serializer

class user_model_7cc812View(APIView):
    def get(self, request):
        queryset = user_model_7cc812.objects.all()
        serializer = user_model_7cc812Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_7cc812Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_87dc6f
from api.serializers_generated import user_model_87dc6fSerializer

class user_model_87dc6fView(APIView):
    def get(self, request):
        queryset = user_model_87dc6f.objects.all()
        serializer = user_model_87dc6fSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_87dc6fSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_371dfd
from api.serializers_generated import user_model_371dfdSerializer

class user_model_371dfdView(APIView):
    def get(self, request):
        queryset = user_model_371dfd.objects.all()
        serializer = user_model_371dfdSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_371dfdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_0b19a1
from api.serializers_generated import user_model_0b19a1Serializer

class user_model_0b19a1View(APIView):
    def get(self, request):
        queryset = user_model_0b19a1.objects.all()
        serializer = user_model_0b19a1Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_0b19a1Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_a98ee3
from api.serializers_generated import user_model_a98ee3Serializer

class user_model_a98ee3View(APIView):
    def get(self, request):
        queryset = user_model_a98ee3.objects.all()
        serializer = user_model_a98ee3Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_a98ee3Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_818fe0
from api.serializers_generated import user_model_818fe0Serializer

class user_model_818fe0View(APIView):
    def get(self, request):
        queryset = user_model_818fe0.objects.all()
        serializer = user_model_818fe0Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_818fe0Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_fb8733
from api.serializers_generated import user_model_fb8733Serializer

class user_model_fb8733View(APIView):
    def get(self, request):
        queryset = user_model_fb8733.objects.all()
        serializer = user_model_fb8733Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_fb8733Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_5ed113
from api.serializers_generated import user_model_5ed113Serializer

class user_model_5ed113View(APIView):
    def get(self, request):
        queryset = user_model_5ed113.objects.all()
        serializer = user_model_5ed113Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_5ed113Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from api.models_generated import user_model_795241
from api.serializers_generated import user_model_795241Serializer

class user_model_795241View(APIView):
    def get(self, request):
        queryset = user_model_795241.objects.all()
        serializer = user_model_795241Serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_model_795241Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)