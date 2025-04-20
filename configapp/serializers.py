from django.contrib.auth.models import Group
from rest_framework import serializers

from configapp.models import User, TableType, Table, GroupStudent, Course
from configapp.models.model_student import Student
from configapp.models.model_teacher import Teacher, Departments

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "success": False,
                    "detail": "user doest not exist"
                }
            )
        auth_user = authenticate(username=user.username, password=password)
        if auth_user is None:
            raise serializers.ValidationError(
                {
                    "success": False,
                    "detail": "username or password is invalid"
                }

            )
        attrs["user"] = auth_user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'password', 'is_active', 'is_staff', "is_teacher", 'is_admin', 'is_student')


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    re_new_password = serializers.CharField(required=True, write_only=True)

    def update(self, instance, validated_data):

        instance.password = validated_data.get('password', instance.password)

        if not validated_data['new_password']:
            raise serializers.ValidationError({'new_password': 'not found'})

        if not validated_data['old_password']:
            raise serializers.ValidationError({'old_password': 'not found'})

        if not instance.check_password(validated_data['old_password']):
            raise serializers.ValidationError({'old_password': 'wrong password'})

        if validated_data['new_password'] != validated_data['re_new_password']:
            raise serializers.ValidationError({'passwords': 'passwords do not match'})

        if validated_data['new_password'] == validated_data['re_new_password'] and instance.check_password(
                validated_data['old_password']):
            instance.set_password(validated_data['new_password'])
            instance.save()
            return instance

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 're_new_password']


class SMSSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class VerifySMSSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    verification_code = serializers.CharField()


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class DepartmentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'

class TeacherSerializers(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class BaseUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_student = serializers.BooleanField(read_only=True)
    is_teacher = serializers.BooleanField(read_only=True)
    class Meta:
        model = User
        fields = '__all__'

class TeacherPostSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(),many=True)

    class Meta:
        model = Teacher
    def create(self, validated_data):
        user_db = validated_data.pop("user")
        user_db["is_teacher"] = True
        user_db["is_active"] = True
        departments_db = validated_data.pop("departments")
        course_db = validated_data.pop("course")
        user = User.objects.create_user(**user_db)
        teacher = Teacher.objects.create(user=user,**validated_data)
        teacher.departments.set(departments_db)
        teacher.course.set(course_db)
        return teacher

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class StudentPostSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), many=True)

    class Meta:
        model = Student

    def create(self, validated_data):
        user_db = validated_data.pop("user")
        user_db["is_student"] = True
        user_db["is_active"] = True
        departments_db = validated_data.pop("departments")
        course_db = validated_data.pop("course")
        user = User.objects.create_user(**user_db)
        student = Student.objects.create(user=user, **validated_data)
        student.departments.set(departments_db)
        student.course.set(course_db)
        return student
class TableTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableType
        fields = '__all__'
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class GroupStudentSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField()
    table = TableSerializer(read_only=True)

    teacher = serializers.StringRelatedField(many=True)

    class Meta:
        model = GroupStudent
        fields = '__all__'
        extra_kwargs = {
            'start_date': {'format': '%Y-%m-%d'},
            'end_date': {'format': '%Y-%m-%d'},
        }


# If you need nested serializers for related fields:
class GroupStudentDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    teacher = TeacherSerializers(many=True, read_only=True)
    table = TableSerializer(read_only=True)

    class Meta:
        model = GroupStudent
        fields = '__all__'





class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupStudent
        fields = ['title', 'course', 'teacher', 'table', 'start_date', 'finish_date']