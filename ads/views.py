from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import View
from django.contrib.auth import logout
from django import forms

from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm
from .forms import RussianUserCreationForm


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        queryset = Ad.objects.select_related('user').all()
        search_query = self.request.GET.get('search')
        category = self.request.GET.get('category')
        condition = self.request.GET.get('condition')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Ad.CATEGORY_CHOICES
        context['conditions'] = Ad.CONDITION_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_condition'] = self.request.GET.get('condition', '')
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    queryset = Ad.objects.select_related('user').prefetch_related('user__ads')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.object

        context['user_ads'] = ad.user.ads.exclude(pk=ad.pk)[:5]
        context['can_edit'] = ad.user == self.request.user

        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Объявление успешно создано!')
        return response

    def get_success_url(self):
        return reverse_lazy('ad-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать новое объявление'
        return context


class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Объявление успешно обновлено!')
        return response

    def get_success_url(self):
        return reverse_lazy('ad-detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать объявление'
        return context


class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Объявление успешно удалено!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('ad-list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ExchangeProposalCreateView(LoginRequiredMixin, CreateView):
    model = ExchangeProposal
    form_class = ExchangeProposalForm
    template_name = 'ads/proposal_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.ads.exists():
            messages.warning(request, "Чтобы предложить обмен, сначала создайте свое объявление")
            return redirect(reverse('ad-create'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Убедимся, что передаем пользователя
        return kwargs

    def form_valid(self, form):
        ad_receiver = get_object_or_404(Ad, id=self.kwargs['ad_receiver_id'])
        ad_sender = form.cleaned_data['ad_sender']

        # Проверка, что пользователь не пытается обменять свое же объявление
        if ad_receiver.user == self.request.user:
            form.add_error(None, 'Невозможно создать предложение для собственного объявления')
            return self.form_invalid(form)

        # Создаем объект предложения
        proposal = ExchangeProposal(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver,
            comment=form.cleaned_data['comment'],
            status='pending'
        )
        proposal.save()

        self.object = proposal  # Устанавливаем объект для последующего использования
        messages.success(self.request, 'Предложение обмена успешно отправлено!')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_receiver'] = get_object_or_404(Ad, id=self.kwargs['ad_receiver_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('proposal-detail', kwargs={'pk': self.object.pk})


class ExchangeProposalStatusForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'Новый статус',
        }


class ExchangeProposalUpdateView(LoginRequiredMixin, UpdateView):
    model = ExchangeProposal
    form_class = ExchangeProposalStatusForm
    template_name = 'ads/proposal_update_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Статус предложения изменен на "{self.object.get_status_display()}"!')
        return response

    def get_success_url(self):
        return reverse_lazy('proposal-detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        return ExchangeProposal.objects.filter(
            ad_receiver__user=self.request.user
        ).select_related('ad_sender', 'ad_receiver')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Обновить статус предложения'
        context['proposal'] = self.object
        return context


class ExchangeProposalListView(LoginRequiredMixin, ListView):
    model = ExchangeProposal
    template_name = 'ads/proposal_list.html'
    context_object_name = 'proposals'
    paginate_by = 10

    def get_queryset(self):
        return ExchangeProposal.objects.filter(
            Q(ad_sender__user=self.request.user) |
            Q(ad_receiver__user=self.request.user)
        ).select_related('ad_sender', 'ad_receiver').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ExchangeProposal.STATUS_CHOICES
        return context


class ExchangeProposalDetailView(LoginRequiredMixin, DetailView):
    model = ExchangeProposal
    template_name = 'ads/proposal_detail.html'
    context_object_name = 'proposal'  # Явно задаем имя контекста
    queryset = ExchangeProposal.objects.select_related(
        'ad_sender',
        'ad_sender__user',
        'ad_receiver',
        'ad_receiver__user'
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.object

        # Проверка прав на обновление статуса
        context['can_update'] = False
        if proposal.ad_receiver and proposal.ad_receiver.user == self.request.user:
            context['can_update'] = True

        # Явная передача объявлений в контекст
        context['ad_sender'] = proposal.ad_sender
        context['ad_receiver'] = proposal.ad_receiver

        return context


class SignUpView(CreateView):
    model = User
    form_class = RussianUserCreationForm  # Используем кастомную форму с русскими сообщениями
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('ad-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать!')
        return response

    def form_invalid(self, form):
        # Добавляем сообщения об ошибках
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form.fields[field].label}: {error}")
        return super().form_invalid(form)


class CustomLogoutView(View):
    def get(self, request):
        return self.logout_user(request)

    def post(self, request):
        return self.logout_user(request)

    def logout_user(self, request):
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
        return redirect('ad-list')
