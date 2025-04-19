from django.db import models
from .auth_users import BaseModel


class Student(BaseModel):
    user = models.OneToOneField('configapp.User', on_delete=models.CASCADE)
    course = models.ManyToManyField('configapp.Course',related_name="get_student_course")
    group = models.ManyToManyField('configapp.Group', related_name='get_student_group')
    is_line = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.phone_number
