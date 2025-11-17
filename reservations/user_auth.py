from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

User = get_user_model()

# Handles registration validation + creation logic
class UserRegistrationSerializer(serializers.ModelSerializer):
    # Two password fields to confirm match
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},  # email must be provided
        }

    # Check both passwords match before creating
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    # Create user object
    def create(self, validated_data):
        validated_data.pop('password2')  # not needed anymore

        # Use Django's built-in create_user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']


# create user
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Anyone can register

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        # If valid, create user and return basic details
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED
            )

        # Send validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 #returns the logged-in user's info
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]  # Must be logged in

    def get(self, request):
        serializer = UserPublicSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
