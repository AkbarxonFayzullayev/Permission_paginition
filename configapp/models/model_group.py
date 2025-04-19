from django.db import models

from configapp.models import BaseModel


class Course(BaseModel):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title

class Group(BaseModel):
    title = models.CharField(max_length=25, unique=True)
    course = models.ForeignKey('configapp.Course', on_delete=models.RESTRICT, related_name='group_course')
    teacher = models.ManyToManyField('configapp.Teacher',related_name="group_teacher")
    start_date = models.DateField()
    end_date = models.DateField()
    descriptions = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        return self.title
