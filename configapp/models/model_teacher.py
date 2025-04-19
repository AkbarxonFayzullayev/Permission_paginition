from django.db import models

from configapp.models import BaseModel

class Departments(BaseModel):
    title = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title

class Teacher(BaseModel):
    user = models.OneToOneField('configapp.User', on_delete=models.CASCADE, related_name='user')
    departments = models.ManyToManyField('configapp.Departments', related_name="get_department")
    course = models.ManyToManyField('configapp.Course', related_name="get_teacher_course")
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.user.phone_number}"
