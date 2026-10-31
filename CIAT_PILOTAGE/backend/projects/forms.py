from django import forms
from .models import Projet
class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ["nom","description","porteur","domaine","cohorte","mentor","partenaires","date_soumission","date_demarrage","date_fin_prevue","statut","progression","budget_previsionnel","financement_obtenu"]
        widgets = {
            "description": forms.Textarea(attrs={"rows":3}),
            "date_soumission": forms.DateInput(attrs={"type":"date"}),
            "date_demarrage": forms.DateInput(attrs={"type":"date"}),
            "date_fin_prevue": forms.DateInput(attrs={"type":"date"}),
            "partenaires": forms.CheckboxSelectMultiple(),
        }
