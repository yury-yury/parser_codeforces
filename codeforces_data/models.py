from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        pass


class Task(models.Model):
    number = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150)
    categories =  models.ManyToManyField('Category')
    difficulty = models.IntegerField()
    solution = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.number} {self.name}"

    class Meta:
        pass

