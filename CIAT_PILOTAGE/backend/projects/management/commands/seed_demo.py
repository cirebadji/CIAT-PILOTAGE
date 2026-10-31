from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from projects.models import Domaine,Cohorte,PorteurProjet,Mentor,Partenaire,Projet,Financement,Jalon
import random

class Command(BaseCommand):
    help="Charge un jeu de démonstration fictif sans doublons."
    def handle(self,*args,**kwargs):
        random.seed(42)
        domaines=["TIC et intelligence artificielle","Agriculture et environnement","Énergie","Mécanique et fabrication","Pharmaceutique et biomédical","Éducation et formation","Entrepreneuriat et services"]
        ds=[Domaine.objects.get_or_create(nom=n)[0] for n in domaines]
        cs=[Cohorte.objects.get_or_create(nom=f"Cohorte {y}",defaults={"annee":y})[0] for y in [2024,2025,2026]]
        mentors=[Mentor.objects.get_or_create(nom_complet=n,defaults={"specialite":"Accompagnement entrepreneurial"})[0] for n in ["Aminata Sarr","Mamadou Ba","Fatou Ndiaye","Ibrahima Diallo"]]
        partners=[Partenaire.objects.get_or_create(nom=n,defaults={"type_partenaire":t})[0] for n,t in [("Fonds Innovation Démo","financier"),("Université partenaire Démo","academique"),("TechLab Démo","technique"),("Collectivité Démo","institutionnel")]]
        for role in ["Administrateur","Coordonnateur","Analyste"]: Group.objects.get_or_create(name=role)
        statuses=["idee","soumis","evaluation","selectionne","incubation","prototype","termine","suspendu","rejete"]
        first_names=["Awa","Moussa","Fatou","Ibrahima","Mariama","Cheikh","Aminata","Ousmane","Ndeye","Abdou"]
        last_names=["Diop","Ndiaye","Fall","Sarr","Ba","Diallo","Sow","Gueye","Faye","Sy"]
        today=timezone.localdate()
        for i in range(1,51):
            porteur,_=PorteurProjet.objects.get_or_create(nom_complet=f"{first_names[(i-1)%10]} {last_names[(i*3)%10]}",defaults={"email":f"porteur{i}@exemple.test","genre":"F" if i%2 else "M"})
            name=f"Projet démonstration {i:02d}"
            if Projet.objects.filter(nom=name).exists(): continue
            status=statuses[(i-1)%len(statuses)]
            deadline=today+timedelta(days=(i%18)-8)
            p=Projet.objects.create(nom=name,description="Projet fictif destiné à illustrer le suivi des activités de l'incubateur.",porteur=porteur,domaine=ds[(i-1)%len(ds)],cohorte=cs[(i-1)%3],mentor=mentors[(i-1)%len(mentors)],date_soumission=today-timedelta(days=i*5),date_demarrage=today-timedelta(days=i*3),date_fin_prevue=deadline,statut=status,progression=100 if status=="termine" else random.randint(5,95),budget_previsionnel=Decimal(500000+i*25000),financement_obtenu=Decimal(150000+i*10000),fictif=True)
            p.partenaires.add(partners[(i-1)%len(partners)])
            Financement.objects.create(projet=p,source="Fonds Innovation Démo",montant_demande=p.budget_previsionnel,montant_obtenu=p.financement_obtenu,statut="accorde")
            Jalon.objects.create(projet=p,titre="Validation du prototype",date_limite=deadline,termine=(status=="termine"))
        self.stdout.write(self.style.SUCCESS("Jeu de démonstration fictif chargé. 50 projets au maximum, sans doublons."))
