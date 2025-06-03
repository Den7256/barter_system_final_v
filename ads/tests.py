from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


class AdModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        Ad.objects.create(
            user=cls.user,
            title='Test Ad',
            description='Test description',
            category='electronics',
            condition='new'
        )

    def test_title_content(self):
        ad = Ad.objects.get(id=1)
        self.assertEqual(ad.title, 'Test Ad')

    def test_ad_str_method(self):
        ad = Ad.objects.get(id=1)
        self.assertEqual(str(ad), 'Test Ad')

    def test_ad_absolute_url(self):
        ad = Ad.objects.get(id=1)
        self.assertEqual(ad.get_absolute_url(), '/ad/1/')


class ExchangeProposalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1', password='12345')
        cls.user2 = User.objects.create_user(username='user2', password='12345')

        cls.ad1 = Ad.objects.create(
            user=cls.user1,
            title='Ad 1',
            description='Description 1',
            category='electronics',
            condition='new'
        )

        cls.ad2 = Ad.objects.create(
            user=cls.user2,
            title='Ad 2',
            description='Description 2',
            category='books',
            condition='used'
        )

        ExchangeProposal.objects.create(
            ad_sender=cls.ad1,
            ad_receiver=cls.ad2,
            comment='Test proposal'
        )

    def test_proposal_default_status(self):
        proposal = ExchangeProposal.objects.get(id=1)
        self.assertEqual(proposal.status, 'pending')

    def test_proposal_str_method(self):
        proposal = ExchangeProposal.objects.get(id=1)
        self.assertTrue(str(proposal).startswith('Предложение #'))

    def test_proposal_absolute_url(self):
        proposal = ExchangeProposal.objects.get(id=1)
        self.assertEqual(proposal.get_absolute_url(), '/proposal/1/')


class AdListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='12345')
        for i in range(15):
            Ad.objects.create(
                user=user,
                title=f'Ad {i}',
                description=f'Description {i}',
                category='electronics',
                condition='new'
            )

    def test_view_url_exists(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'ads/ad_list.html')

    def test_pagination(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['ads']), 10)

    def test_search(self):
        response = self.client.get('/?search=Ad+5')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 1)
        self.assertEqual(response.context['ads'][0].title, 'Ad 5')


class AdCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_view_url_exists(self):
        response = self.client.get('/ad/new/')
        self.assertEqual(response.status_code, 200)

    def test_create_ad(self):
        response = self.client.post('/ad/new/', {
            'title': 'New Ad',
            'description': 'New description',
            'category': 'electronics',
            'condition': 'new'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.count(), 1)
        self.assertEqual(Ad.objects.first().title, 'New Ad')