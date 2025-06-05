from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Ad(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('books', 'Книги'),
        ('clothes', 'Одежда'),
        ('furniture', 'Мебель'),
        ('other', 'Другое'),
    ]

    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
        ('broken', 'Требует ремонта'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Пользователь'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на изображение')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ad-detail', kwargs={'pk': self.pk})

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    def get_condition_display(self):
        return dict(self.CONDITION_CHOICES).get(self.condition, self.condition)


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='sent_proposals',
        verbose_name='Предлагаемое объявление'
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='received_proposals',
        verbose_name='Запрашиваемое объявление'
    )
    comment = models.TextField(verbose_name='Комментарий')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"Предложение #{self.id}"

    def get_absolute_url(self):
        return reverse('proposal-detail', kwargs={'pk': self.pk})

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
