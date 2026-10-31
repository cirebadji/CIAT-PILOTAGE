# Initial migration for CIAT PILOTAGE project models.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Cohorte",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nom", models.CharField(max_length=100, unique=True)), ("annee", models.PositiveIntegerField()), ("date_debut", models.DateField(blank=True, null=True)), ("date_fin", models.DateField(blank=True, null=True)), ("description", models.TextField(blank=True))],
        ),
        migrations.CreateModel(
            name="Domaine",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nom", models.CharField(max_length=120, unique=True)), ("description", models.TextField(blank=True))],
        ),
        migrations.CreateModel(
            name="Mentor",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nom_complet", models.CharField(max_length=160)), ("specialite", models.CharField(blank=True, max_length=120)), ("email", models.EmailField(blank=True, max_length=254))],
        ),
        migrations.CreateModel(
            name="Partenaire",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nom", models.CharField(max_length=160, unique=True)), ("type_partenaire", models.CharField(choices=[("institutionnel", "Institutionnel"), ("financier", "Financier"), ("technique", "Technique"), ("academique", "Académique"), ("autre", "Autre")], default="autre", max_length=30)), ("contact", models.CharField(blank=True, max_length=120)), ("email", models.EmailField(blank=True, max_length=254)), ("telephone", models.CharField(blank=True, max_length=30)), ("date_partenariat", models.DateField(blank=True, null=True))],
        ),
        migrations.CreateModel(
            name="PorteurProjet",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nom_complet", models.CharField(max_length=160)), ("email", models.EmailField(blank=True, max_length=254)), ("telephone", models.CharField(blank=True, max_length=30)), ("genre", models.CharField(blank=True, max_length=20)), ("organisation", models.CharField(blank=True, max_length=160))],
        ),
        migrations.CreateModel(
            name="Projet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=180)), ("description", models.TextField(blank=True)),
                ("date_soumission", models.DateField(default=django.utils.timezone.localdate)),
                ("date_demarrage", models.DateField(blank=True, null=True)), ("date_fin_prevue", models.DateField(blank=True, null=True)),
                ("statut", models.CharField(choices=[("idee", "Nouvelle idée"), ("soumis", "Soumis"), ("evaluation", "En évaluation"), ("selectionne", "Sélectionné"), ("incubation", "En incubation"), ("prototype", "Prototype en développement"), ("termine", "Terminé"), ("suspendu", "Suspendu"), ("rejete", "Rejeté")], default="idee", max_length=20)),
                ("progression", models.PositiveSmallIntegerField(default=0)), ("budget_previsionnel", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("financement_obtenu", models.DecimalField(decimal_places=2, default=0, max_digits=14)), ("fictif", models.BooleanField(default=True)),
                ("cree_le", models.DateTimeField(auto_now_add=True)), ("modifie_le", models.DateTimeField(auto_now=True)),
                ("cohorte", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="projets", to="projects.cohorte")),
                ("domaine", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="projets", to="projects.domaine")),
                ("mentor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="projets", to="projects.mentor")),
                ("partenaires", models.ManyToManyField(blank=True, related_name="projets", to="projects.partenaire")),
                ("porteur", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="projets", to="projects.porteurprojet")),
            ],
            options={"ordering": ["-date_soumission"]},
        ),
        migrations.CreateModel(
            name="Financement",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("source", models.CharField(max_length=160)), ("montant_demande", models.DecimalField(decimal_places=2, default=0, max_digits=14)), ("montant_obtenu", models.DecimalField(decimal_places=2, default=0, max_digits=14)), ("date_obtention", models.DateField(blank=True, null=True)), ("statut", models.CharField(choices=[("demande", "Demandé"), ("accorde", "Accordé"), ("verse", "Versé"), ("refuse", "Refusé")], default="demande", max_length=20)), ("projet", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="financements", to="projects.projet"))],
        ),
        migrations.CreateModel(
            name="HistoriqueProgression",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("progression", models.PositiveSmallIntegerField()), ("observation", models.TextField(blank=True)), ("date_enregistrement", models.DateTimeField(auto_now_add=True)), ("auteur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)), ("projet", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="historiques", to="projects.projet"))],
            options={"ordering": ["-date_enregistrement"]},
        ),
        migrations.CreateModel(
            name="Jalon",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("titre", models.CharField(max_length=180)), ("description", models.TextField(blank=True)), ("date_limite", models.DateField()), ("termine", models.BooleanField(default=False)), ("projet", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="jalons", to="projects.projet"))],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("message", models.CharField(max_length=255)), ("lue", models.BooleanField(default=False)), ("cree_le", models.DateTimeField(auto_now_add=True)), ("utilisateur", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL))],
        ),
    ]
