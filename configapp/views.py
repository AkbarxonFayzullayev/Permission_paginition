from django.db import transaction
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from configapp.models.model_student import Student
from configapp.models.model_teacher import Teacher
from configapp.serializers import TeacherSerializers, StudentPostSerializer, StudentSerializer, TeacherPostSerializer, \
    LoginSerializer, ChangePasswordSerializer, UserSerializer, VerifySMSSerializer

import random
import permission

from .make_token import get_tokens_for_user
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import make_password
from rest_framework import status, permissions
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from .models import User
from .serializers import SMSSerializer
from drf_yasg.utils import swagger_auto_schema


def send_otp():
    otp = str(random.randint(1001, 9999))
    print(otp, "==============================")
    return otp


class PhoneSendOTP(APIView):
    @swagger_auto_schema(request_body=SMSSerializer)
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({
                'status': False,
            }, status=status.HTTP_400_BAD_REQUEST)

        phone = str(phone_number)
        user = User.objects.filter(phone_number__iexact=phone)
        if user.exists():
            return Response({
                'status': False,
                'detail': 'Bu telefon raqami allaqachon ro‘yxatdan o‘tgan'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            key = send_otp()
            if key:
                cache.set(phone, key, 600)
                return Response({
                    "status": True,
                    "message": "SMS muvaffaqiyatli yuborildi"
                }, status=status.HTTP_200_OK)
            return Response({
                "status": False,
                "message": "SMS yuborishda xatolik yuz berdi"
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifySMS(APIView):
    @swagger_auto_schema(request_body=VerifySMSSerializer)
    def post(self, request):
        serializer = VerifySMSSerializer(data=request.data)

        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            verification_code = serializer.validated_data['verification_code']
            cached_code = str(cache.get(phone_number))

            if verification_code == cached_code:
                return Response({
                    'status': True,
                    'detail': 'OTP mos tushdi. Ro‘yxatdan o‘tishni davom ettiring.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': False,
                    'detail': 'Noto‘g‘ri tasdiqlash kodi.'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserApi(APIView):
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = serializer.validated_data.get('password')
            serializer.validated_data['password'] = make_password(password)
            serializer.save()
            return Response({
                "status": True,
                'datail': 'account create'
            })

    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def get(self, request):
        users = User.objects.all().order_by("-id")
        serializer = UserSerializer(users, many=True)
        return Response(data=serializer.data)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        serializer = ChangePasswordSerializer(instance=self.request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApi(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user")
        token = get_tokens_for_user(user)
        token["salom"] = "hi"
        token["is_admin"] = user.is_superuser
        return Response(data=token, status=status.HTTP_200_OK)

class TeacherAPI(APIView):
    permission_classes = [IsAdminUser, ]
    def get(self, request):
        teachers = Teacher.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # sahifadagi elementlar soni
        result_page = paginator.paginate_queryset(teachers, request)
        serializer = TeacherSerializers(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    def post(self,request):
        serializers = TeacherSerializers(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(data=serializers.data)
        return Response(data=serializers.errors)

    def put(self, request, pk):
        teacher = get_object_or_404(Teacher, pk=pk)
        serializer = TeacherPostSerializer(teacher, data=request.data)

        if serializer.is_valid():
            teacher = serializer.save()
            return Response(StudentSerializer(teacher).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        teacher = get_object_or_404(Teacher, pk=pk)
        serializer = StudentPostSerializer(teacher, data=request.data, partial=True)

        if serializer.is_valid():
            teacher = serializer.save()
            return Response(StudentSerializer(teacher).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        teacher = get_object_or_404(Student, pk=pk)
        user = teacher.user
        with transaction.atomic():
            teacher.delete()
            user.delete()
        return Response({"success": True, "message": "Teacher va bog‘liq user o‘chirildi."},
                        status=status.HTTP_204_NO_CONTENT)


class StudentAPI(APIView):
    permission_classes = [IsAdminUser, ]
    def get(self, request):
        students = Student.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(students, request)
        serializer = StudentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    def post(self,request):
        serializers = TeacherSerializers(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(data=serializers.data)
        return Response(data=serializers.errors)

    def put(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        serializer = StudentPostSerializer(student, data=request.data)

        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        serializer = StudentPostSerializer(student, data=request.data, partial=True)

        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        user = student.user
        with transaction.atomic():
            student.delete()
            user.delete()
        return Response({"success": True, "message": "Student va bog‘liq user o‘chirildi."},
                        status=status.HTTP_204_NO_CONTENT)

from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from configapp.add_pagination import CustomPagination
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrTeacherLimitedEdit
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class GroupApi(APIView):
    @swagger_auto_schema(request_body=GroupSerializer)
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        group_title = GroupStudent.objects.all().order_by('-id')
        paginator = CustomPagination()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(group_title, request)
        serializer = GroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class GroupStudentDetailUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrTeacherLimitedEdit]
    @swagger_auto_schema(request_body=GroupSerializer)
    def patch(self, request, pk):
        group = get_object_or_404(GroupStudent, pk=pk)
        self.check_object_permissions(request, group)
        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)