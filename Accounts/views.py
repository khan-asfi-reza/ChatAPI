from django.contrib.auth import get_user_model
from idna import unicode
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from Accounts.models import Profile
from Accounts.permission import IsPostOrIsAuthenticated
from Accounts.serializer import AuthenticationSerializer, UserSerializer, ProfileCreateSerializer, \
    ProfileRetrieveSerializer

# Create your views here.

User = get_user_model()


class ProfilePagination(PageNumberPagination):
    page_size = 14
    page_size_query_param = 'page_size'
    max_page_size = 14


class CreateTokenView(APIView):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    # Returns Authorization Token for the user
    def post(self, request):
        # Serialize the data
        serializer = AuthenticationSerializer(data=request.data)
        if serializer.is_valid():
            # Gets the user
            user = serializer.validated_data['user']
            # Creates auth token
            token, created = Token.objects.get_or_create(user=user)
            # Serialize User Data
            serialized_user = UserSerializer(user)
            data = {'token': token.key, 'user': serialized_user.data}
            # Returns User Data and Token
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCRUDView(viewsets.ModelViewSet):
    # Changing permission class to Post or Authenticate, Allow Post request if user is not authenticated
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsPostOrIsAuthenticated]
    # user serializer
    serializer_class = UserSerializer
    # Query set of all user objects
    queryset = User.objects.all()
    # Query Object of user
    query_object = User.objects

    @action(methods=['delete'], detail=False)
    def destroy(self, request, *args, **kwargs):
        request.user.delete()
        return Response({'response': 'User Successfully Deleted'}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def create(self, request):
        # giving serializer the data from request data
        serializer = self.get_serializer(data=request.data)
        # checks if serializer is valid
        if serializer.is_valid():
            # saves user information
            user = serializer.save()
            # Return data
            token, created = Token.objects.get_or_create(user=user)
            data = {'token': token.key, 'user': serializer.data}

            # return new token
            return Response(data, status=status.HTTP_200_OK)

        # Otherwise it will return errors and a bad request
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, permission_classes=[False])
    def update(self, request):
        serializer = self.get_serializer(instance=request.user, data=request.data, partial=True)
        # If serializer is valid it will save
        if serializer.is_valid():
            user = serializer.save()
            oldToken = Token.objects.get(user=user)
            oldToken.delete()
            token, created = Token.objects.get_or_create(user=user)
            context = {'token': token.key, 'user': serializer.data}
            # return new token
            return Response(context, status=status.HTTP_200_OK)
        # Otherwise it will show error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True, )
    def retrieve(self, request, pk=None, ):
        # Getting instance
        instance = get_object_or_404(self.queryset, name=request.user.name)
        # Instance serializer
        serializer = self.get_serializer(instance=instance, many=False)
        # return serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileCreateListUpdateView(viewsets.ModelViewSet):
    serializer_class = ProfileRetrieveSerializer
    create_serializer_class = ProfileCreateSerializer
    queryset = Profile.objects.all()
    authentication_classes = [TokenAuthentication]
    model = Profile
    permission_classes = [IsAuthenticated]
    pagination_class = ProfilePagination

    # Returns Serializer that performs create
    def get_create_serializer(self, **kwargs):
        return self.create_serializer_class(context={'request': self.request}, **kwargs)

    # Post Method -> Creates User Profile
    @action(methods=['post'], detail=False)
    def create(self, request, *args, **kwargs):
        # Serializes data
        serializer = self.get_create_serializer(data=request.data)
        if serializer.is_valid():
            # Saves Serializer Data
            instance = serializer.save(user=request.user)
            retrieve_serializer = self.get_serializer(instance=instance)
            return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Put Method -> Updates User Profile
    @action(methods=['put'], detail=False)
    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(user=request.user)
        serializer = self.get_create_serializer(instance=instance, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileRetrieveView(viewsets.ModelViewSet):
    serializer_class = ProfileRetrieveSerializer
    create_serializer_class = ProfileCreateSerializer
    queryset = Profile.objects.all()
    authentication_classes = [TokenAuthentication]
    model = Profile
    permission_classes = [IsAuthenticated]


class UsernameAvailable(APIView):
    def post(self, request):
        name = request.data['username']
        user = User.objects.filter(name=name)
        if user.exists():
            return Response({'msg': 0})  # 0 means not available
        else:
            return Response({'msg': 1})  # 1 means available


class EmailAvailable(APIView):
    def post(self, request):
        email = request.data['email']
        if email == '':
            return Response({'msg': 1})
        user = User.objects.filter(email=email)
        if user.exists():
            return Response({'msg': 0})  # 0 means not available
        else:
            return Response({'msg': 1})  # 1 means available


