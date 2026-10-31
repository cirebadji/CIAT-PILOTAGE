from django.contrib import admin
from .models import *
admin.site.register([Domaine,Cohorte,PorteurProjet,Mentor,Partenaire,Jalon,Financement,HistoriqueProgression,Notification])
@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ("nom","porteur","domaine","cohorte","statut","progression","date_fin_prevue")
    list_filter = ("statut","domaine","cohorte")
    search_fields = ("nom","porteur__nom_complet")
