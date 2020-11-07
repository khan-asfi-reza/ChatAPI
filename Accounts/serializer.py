from django.contrib.auth import get_user_model, authenticate
from rest_framework.serializers import Serializer, ModelSerializer, ValidationError, CharField

from Accounts.models import Profile

User = get_user_model()


class UserSerializer(ModelSerializer):
    password = CharField(required=True,
                         style={'input_type': 'password'},
                         trim_whitespace=False, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'gender', 'name', 'email', ]
        read_only_fields = ['id', ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(username=self.validated_data['username'],
                                   email=self.validated_data['email'],
                                   gender=self.validated_data['gender'],
                                   name=self.validated_data['name']
                                   )
        user.set_password(self.validated_data['password'])
        user.save()
        return user

class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'gender']
        read_only_fields = ['id', ]


class AuthenticationSerializer(Serializer):
    username = CharField(required=True, trim_whitespace=True)
    password = CharField(required=True,
                         style={'input_type': 'password'},
                         trim_whitespace=False)

    def validate(self, attrs):
        # Validate and authenticate
        username = attrs.get('username')
        password = attrs.get('password')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError({'error': 'Account does not exist'}, code='authentication')
        user = authenticate(request=self.context.get('request'),
                            username=username,
                            password=password)
        if not user:
            msg = "Incorrect password"
            raise ValidationError({'error': msg}, code='authentication')

        attrs['user'] = user
        return attrs


class ProfileCreateSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'profile_picture', 'online', 'last_online', ]
        read_only_fields = ['id']


class ProfileRetrieveSerializer(ModelSerializer):
    user = UserRetrieveSerializer(many=False)

    class Meta:
        model = Profile
        fields = ['user', 'profile_picture', 'online', 'last_online', ]
        read_only_fields = ['id']
