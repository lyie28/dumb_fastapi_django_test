from django.db import models

class Item(models.Model):
    animal = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.animal}"