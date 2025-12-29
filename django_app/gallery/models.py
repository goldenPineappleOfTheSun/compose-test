from django.db import models
from django.utils import timezone


class Image(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя изображения')
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении записи
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

