from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view

from .serializers import GroupSerializer


@api_view()
def hello_view(request: Request) -> Response:
    return Response({"message": "Hello!"})


class GroupListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer