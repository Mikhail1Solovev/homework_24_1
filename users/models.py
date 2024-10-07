from django.contrib.auth.models import AbstractUser
from django.db import models
from courses.models import Course, Lesson


class CustomUser(AbstractUser):
    # Дополнительные поля для пользователя
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    phone_number = models.CharField(max_length=15, blank=True, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')

    def __str__(self):
        return self.username


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)

    def __str__(self):
        return f"{self.user} - {self.payment_date}"
