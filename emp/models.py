from django.db import models


class Emp(models.Model):
    name = models.CharField(max_length=200)
    emp_id = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=150)
    working = models.BooleanField(default=True)
    department = models.CharField(max_length=200)

    def __str__(self):
        return self.name
