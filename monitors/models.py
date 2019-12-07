from django.db import models

# Create your models here.

class Monitors(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, auto_created=True)
    hostname = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    interval = models.IntegerField()
    ftt = models.IntegerField()
    alert_type = models.CharField(max_length=100)
    alert_enabled = models.BooleanField()
    params = models.CharField(max_length=1000)

    class Meta:
        db_table = 'MONITORS'
        unique_together = ('hostname', 'type',)

    def __str__(self):
        return self.type