from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode

from rest_framework.generics import GenericAPIView
from rest_framework import status

from escrow_app.authentications import serializers
from escrow_app import utils, tasks, models, permissions

class Register(GenericAPIView):
    '''
    A class that registers a new Admin User
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.RegisterSerializer

    def post(self, request):
        data = request.data
        serializers = self.serializer_class(data=data)
        
        # use atomicity to roll back transactions if unsucessful
        with transaction.atomic():
            if serializers.is_valid(raise_exception=True):
                serializers.save()
                # send email notificaion for password reset
                domain_name = get_current_site(request).domain
                tasks.send_password_reset_link.delay(serializers.data,domain_name)
                return utils.CustomResponse.Success('Registered Sucessfully', status=status.HTTP_201_CREATED)
            return utils.CustomResponse.Failure(serializers.data, status=status.HTTP_201_CREATED)

class LoginView(GenericAPIView):
    '''
    A view that authenticates a user and returns a token
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.LoginSerializer
    
    def post(self, request):
        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid(raise_exception=True):
            return utils.CustomResponse.Success(serializer_data.data, status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequest(GenericAPIView):
    '''
    Password Reset Request View
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordResetRequestSerializer

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            domain_name = get_current_site(request).domain
            tasks.send_password_reset_link.delay(serialized_data.validated_data, domain_name)
            return utils.CustomResponse.Success("A Password Reset Link has been sent to your Email", status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirm(GenericAPIView):
    '''
    Password Reset Request View Confirmation
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordResetRequestSerializer
    
    def get(self, request, uidb64, token):
        # decode user token and check if valid
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user,token):
                return utils.CustomResponse.Failure("Verification Token is Invalid or Expired", status=status.HTTP_401_UNAUTHORIZED)
            
            payload = {
                'uidb64': uidb64,
                'token': token
            } 
            return utils.CustomResponse.Success(payload, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as e:
            return utils.CustomResponse.Failure("Token not Valid", status=status.HTTP_400_BAD_REQUEST)

class PasswordChange(GenericAPIView):
    '''
    A view that updates users password if token is valid
    '''
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordChangeSerializer 
    
    def patch(self, request):
        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid(raise_exception=True):
            return utils.CustomResponse.Success("Password Reset Successful", status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(GenericAPIView):
    '''
    A view that logs out a user and blacklist its token
    '''
    serializer_class = serializers.LogoutSerializer
    permission_classes = [permissions.IsActiveVerifiedAuthenticated]
    
    def post(self, request):
        data = request.data 
        serializer_data = self.serializer_class(data=data)
        if serializer_data.is_valid(raise_exception=True):
            serializer_data.save()
            return utils.CustomResponse.Success("Logged Successfully", status=status.HTTP_204_NO_CONTENT)
        return utils.CustomResponse.Failure(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)