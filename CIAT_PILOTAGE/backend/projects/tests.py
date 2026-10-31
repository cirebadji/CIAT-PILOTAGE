from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Domaine,Cohorte,PorteurProjet,Projet
class DashboardTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="testeur",password="MotDePasseSolide2026!")
        self.client=Client()
        self.client.login(username="testeur",password="MotDePasseSolide2026!")
        d=Domaine.objects.create(nom="Numérique")
        p=PorteurProjet.objects.create(nom_complet="Test Porteur")
        Projet.objects.create(nom="Projet test",porteur=p,domaine=d,statut="termine",progression=100)
    def test_dashboard_requires_login(self):
        c=Client()
        self.assertEqual(c.get(reverse("dashboard")).status_code,302)
    def test_dashboard_loads(self):
        self.assertEqual(self.client.get(reverse("dashboard")).status_code,200)
    def test_project_list_loads(self):
        self.assertEqual(self.client.get(reverse("project_list")).status_code,200)
    def test_assistant_demo(self):
        response=self.client.post(reverse("ai_assistant"),{"question":"Combien de projets terminés ?"})
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"terminé")
