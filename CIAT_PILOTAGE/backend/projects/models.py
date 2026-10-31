from django.conf import settings
from django.db import models
from django.utils import timezone

class Domaine(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.nom

class Cohorte(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    annee = models.PositiveIntegerField()
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.nom

class PorteurProjet(models.Model):
    nom_complet = models.CharField(max_length=160)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    genre = models.CharField(max_length=20, blank=True)
    organisation = models.CharField(max_length=160, blank=True)
    def __str__(self): return self.nom_complet

class Mentor(models.Model):
    nom_complet = models.CharField(max_length=160)
    specialite = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    def __str__(self): return self.nom_complet

class Partenaire(models.Model):
    TYPE_CHOICES = [("institutionnel","Institutionnel"),("financier","Financier"),("technique","Technique"),("academique","Académique"),("autre","Autre")]
    nom = models.CharField(max_length=160, unique=True)
    type_partenaire = models.CharField(max_length=30, choices=TYPE_CHOICES, default="autre")
    contact = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    date_partenariat = models.DateField(null=True, blank=True)
    def __str__(self): return self.nom

class Projet(models.Model):
    STATUTS = [
        ("idee","Nouvelle idée"),("soumis","Soumis"),("evaluation","En évaluation"),
        ("selectionne","Sélectionné"),("incubation","En incubation"),
        ("prototype","Prototype en développement"),("termine","Terminé"),
        ("suspendu","Suspendu"),("rejete","Rejeté")
    ]
    nom = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    porteur = models.ForeignKey(PorteurProjet, on_delete=models.PROTECT, related_name="projets")
    domaine = models.ForeignKey(Domaine, on_delete=models.PROTECT, related_name="projets")
    cohorte = models.ForeignKey(Cohorte, on_delete=models.SET_NULL, null=True, blank=True, related_name="projets")
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, blank=True, related_name="projets")
    partenaires = models.ManyToManyField(Partenaire, blank=True, related_name="projets")
    date_soumission = models.DateField(default=timezone.localdate)
    date_demarrage = models.DateField(null=True, blank=True)
    date_fin_prevue = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="idee")
    progression = models.PositiveSmallIntegerField(default=0)
    budget_previsionnel = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    financement_obtenu = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fictif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["-date_soumission"]
    def __str__(self): return self.nom
    def save(self, *args, **kwargs):
        self.progression = min(100, max(0, self.progression))
        super().save(*args, **kwargs)
    @property
    def en_retard(self):
        return bool(self.date_fin_prevue and self.date_fin_prevue < timezone.localdate() and self.statut != "termine")

class Jalon(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="jalons")
    titre = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    date_limite = models.DateField()
    termine = models.BooleanField(default=False)
    def __str__(self): return f"{self.projet.nom} — {self.titre}"

class Financement(models.Model):
    STATUTS = [("demande","Demandé"),("accorde","Accordé"),("verse","Versé"),("refuse","Refusé")]
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="financements")
    source = models.CharField(max_length=160)
    montant_demande = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    montant_obtenu = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    date_obtention = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="demande")
    def __str__(self): return f"{self.source} — {self.projet.nom}"

class HistoriqueProgression(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="historiques")
    progression = models.PositiveSmallIntegerField()
    observation = models.TextField(blank=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: ordering = ["-date_enregistrement"]

class Notification(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    lue = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)
