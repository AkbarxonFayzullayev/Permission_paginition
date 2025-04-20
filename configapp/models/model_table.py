from django.db import models

from configapp.models import BaseModel

class Rooms(BaseModel):
    title=models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, null=True, blank=True)
    def __str__(self):
        return self.title


class TableType(BaseModel):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, null=True, blank=True)
    def __str__(self):
        return self.title
class Table(BaseModel):
    start_time=models.TimeField()
    end_time=models.TimeField()
    room=models.ForeignKey(Rooms,on_delete=models.RESTRICT)
    type=models.ForeignKey(TableType,on_delete=models.RESTRICT)
    descriptions = models.CharField(max_length=500, null=True, blank=True)
