from django.db import models


class Profile(models.Model):
    gender = models.CharField("Пол", max_length=10)
    first_name = models.CharField("Имя", max_length=30)
    last_name = models.CharField("Фамилия", max_length=30)
    phone = models.CharField("Номер телефона", max_length=20)
    email = models.EmailField("Эл. почта", max_length=254)
    location = models.CharField("Место жительства", max_length=100)
    photo = models.URLField("Фото", max_length=250)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
