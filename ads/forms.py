from django import forms
from .models import Ad, ExchangeProposal
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RussianUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        help_text="Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.",
        error_messages={
            'required': 'Пожалуйста, введите имя пользователя',
            'max_length': 'Имя пользователя слишком длинное (максимум 150 символов)',
            'invalid': 'Недопустимое имя пользователя. Используйте только буквы, цифры и @/./+/-/_.',
        }
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Пароль должен содержать не менее 8 символов и не состоять только из цифр.",
        error_messages={
            'required': 'Пожалуйста, введите пароль',
        }
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Введите тот же пароль, что и выше, для проверки.",
        error_messages={
            'required': 'Пожалуйста, подтвердите пароль',
        }
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        return password2

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'image_url': 'Ссылка на изображение',
            'category': 'Категория',
            'condition': 'Состояние',
        }


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'comment': 'Комментарий к предложению',
        }

    # Добавляем поле для выбора объявления как отдельное поле
    ad_sender = forms.ModelChoiceField(
        queryset=Ad.objects.none(),
        label="Ваше объявление для обмена",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Сохраняем пользователя как атрибут формы
        super().__init__(*args, **kwargs)

        if self.user:
            # Ограничиваем выбор объявлений только объявлениями текущего пользователя
            self.fields['ad_sender'].queryset = Ad.objects.filter(user=self.user)

    def clean(self):
        cleaned_data = super().clean()
        ad_sender = cleaned_data.get('ad_sender')

        # Проверка, что объявление принадлежит пользователю
        if ad_sender and ad_sender.user != self.user:
            raise ValidationError("Вы не можете использовать чужое объявление для обмена")

        return cleaned_data

    # Переопределяем сохранение
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.ad_sender = self.cleaned_data['ad_sender']
        if commit:
            instance.save()
        return instance