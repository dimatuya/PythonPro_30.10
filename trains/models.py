from django.core.exceptions import ValidationError
from django.db import models
from cities.models import City


class Train(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Номер поезда')
    from_city = models.ForeignKey(City, on_delete=models.CASCADE,
                                  verbose_name='Откуда', related_name='from_city_set')
    to_city = models.ForeignKey(City, on_delete=models.CASCADE,
                                verbose_name='Куда',  related_name='to_city_set')
    travel_time = models.IntegerField(verbose_name='Время в пути')

    class Meta:
        verbose_name = 'Поезд'
        verbose_name_plural = 'Поезда'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} -- {self.from_city} -> {self.to_city}'

    def clean(self, *args, **kwargs):
        if self.from_city == self.to_city:
            raise ValidationError('Измените город прибытия')

        qs = Train.objects.filter(from_city=self.from_city,
                              to_city=self.to_city,
                              travel_time=self.travel_time).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError('Измените время в пути')

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)

class TrainTest(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Номер поезда')
    from_city = models.ForeignKey(City, on_delete=models.CASCADE,  verbose_name='Откуда' )
