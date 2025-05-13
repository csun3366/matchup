from django.db import models

class Member(models.Model):
    username = models.CharField(max_length=50)
    self_ig = models.CharField(max_length=50, blank=True, null=True)
    other_ig = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username