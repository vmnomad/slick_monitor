from django.db import models

# Create your models here.


class Alerts(models.Model):
    type = models.CharField(primary_key=True, unique=True, max_length=100)
    settings = models.CharField(unique=True, max_length=1000)

    class Meta:
        db_table = 'ALERTS'

    def __str__(self):
        return self.type