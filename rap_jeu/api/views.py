from django.shortcuts import render
from rest_framework import generics, status
from .serializers import QuestionSerializer, CreateRoomSerializer, RoomSerializer
from .models import Questions, Room
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

class QuestionView(generics.CreateAPIView):
    queryset = Questions.objects.all()
    serializer_class = QuestionSerializer

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            equipeA = serializer.data.get('equipeA')
            equipeB = serializer.data.get('equipeB')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.equipeA = equipeA
                room.equipeB = equipeB
                room.pointA = 0
                room.pointB = 0
                room.nbQuestion = 0
                room.save(update_fields=['equipeA', 'equipeB', 'pointA', 'pointB', 'nbQuestion'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room(host=host, equipeA=equipeA,
                            equipeB=equipeB)
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

class ReprendrePartieView(APIView):
    def post(self, request, format=None):
        if self.request.session.exists(self.request.session.session_key):
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        else:
            return Response({'Bad Request': 'Aucune Partie en cours'}, status=status.HTTP_400_BAD_REQUEST)
    
        
class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)


