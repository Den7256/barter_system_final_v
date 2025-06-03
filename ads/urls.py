from django.urls import path
from .views import (
    AdListView, AdDetailView, AdCreateView,
    AdUpdateView, AdDeleteView, ExchangeProposalCreateView,
    ExchangeProposalUpdateView, ExchangeProposalListView,
    ExchangeProposalDetailView, SignUpView
)

urlpatterns = [
    path('', AdListView.as_view(), name='ad-list'),
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad-detail'),
    path('ad/new/', AdCreateView.as_view(), name='ad-create'),
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad-update'),
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad-delete'),

    path('proposals/', ExchangeProposalListView.as_view(), name='proposal-list'),
    path('proposal/<int:pk>/', ExchangeProposalDetailView.as_view(), name='proposal-detail'),
    path(
        'proposal/create/<int:ad_receiver_id>/',
        ExchangeProposalCreateView.as_view(),
        name='proposal-create'
    ),
    path(
        'proposal/<int:pk>/update/',
        ExchangeProposalUpdateView.as_view(),
        name='proposal-update'
    ),

    path('signup/', SignUpView.as_view(), name='signup'),
]