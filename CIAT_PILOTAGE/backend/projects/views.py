import json, os
from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Projet, Cohorte, Domaine, Partenaire, HistoriqueProgression, Financement
from .forms import ProjetForm

def kpi_data(queryset=None):
    qs = queryset if queryset is not None else Projet.objects.all()
    return {
        "idees": qs.count(),
        "selectionnes": qs.filter(statut="selectionne").count() + qs.filter(statut__in=["incubation","prototype","termine"]).count(),
        "incubes": qs.filter(statut__in=["incubation","prototype"]).count(),
        "prototypes": qs.filter(statut="prototype").count(),
        "termines": qs.filter(statut="termine").count(),
        "retard": sum(1 for p in qs if p.en_retard),
        "partenaires": Partenaire.objects.filter(projets__in=qs).distinct().count(),
        "financements": qs.aggregate(total=Sum("financement_obtenu"))["total"] or Decimal("0"),
    }

@login_required
def dashboard(request):
    qs = Projet.objects.select_related("porteur","domaine","cohorte")
    data = kpi_data(qs)
    domaines = list(qs.values("domaine__nom").annotate(total=Count("id")).order_by("-total"))
    statuts = list(qs.values("statut").annotate(total=Count("id")).order_by("statut"))
    recent = qs[:7]
    return render(request,"dashboard.html",{"kpi":data,"domaines":domaines,"statuts":statuts,"recent":recent,"fictif":qs.filter(fictif=True).exists()})

@login_required
def project_list(request):
    qs = Projet.objects.select_related("porteur","domaine","cohorte")
    q = request.GET.get("q","").strip()
    statut = request.GET.get("statut","")
    domaine = request.GET.get("domaine","")
    cohorte = request.GET.get("cohorte","")
    if q: qs = qs.filter(nom__icontains=q) | qs.filter(porteur__nom_complet__icontains=q)
    if statut: qs = qs.filter(statut=statut)
    if domaine: qs = qs.filter(domaine_id=domaine)
    if cohorte: qs = qs.filter(cohorte_id=cohorte)
    return render(request,"projects/list.html",{"projets":qs,"domaines":Domaine.objects.all(),"cohortes":Cohorte.objects.all(),"statuts":Projet.STATUTS})

@login_required
def project_create(request):
    form = ProjetForm(request.POST or None)
    if form.is_valid():
        obj=form.save()
        HistoriqueProgression.objects.create(projet=obj,progression=obj.progression,observation="Création du projet",auteur=request.user)
        messages.success(request,"Projet enregistré.")
        return redirect("project_detail",pk=obj.pk)
    return render(request,"projects/form.html",{"form":form,"titre":"Ajouter un projet"})

@login_required
def project_detail(request,pk):
    obj=get_object_or_404(Projet.objects.select_related("porteur","domaine","cohorte","mentor"),pk=pk)
    return render(request,"projects/detail.html",{"projet":obj})

@login_required
def project_update(request,pk):
    obj=get_object_or_404(Projet,pk=pk)
    old=obj.progression
    form=ProjetForm(request.POST or None,instance=obj)
    if form.is_valid():
        obj=form.save()
        if old != obj.progression:
            HistoriqueProgression.objects.create(projet=obj,progression=obj.progression,observation="Mise à jour de la progression",auteur=request.user)
        messages.success(request,"Projet mis à jour.")
        return redirect("project_detail",pk=obj.pk)
    return render(request,"projects/form.html",{"form":form,"titre":"Modifier le projet"})

@login_required
@require_POST
def project_delete(request,pk):
    obj=get_object_or_404(Projet,pk=pk); obj.delete()
    messages.success(request,"Projet supprimé.")
    return redirect("project_list")

@login_required
def cohort_list(request):
    cohorts=Cohorte.objects.annotate(total=Count("projets"),termines=Count("projets",filter=__import__("django").db.models.Q(projets__statut="termine")))
    return render(request,"cohorts.html",{"cohortes":cohorts})

@login_required
def analytics_page(request):
    qs=Projet.objects.all()
    if request.GET.get("cohorte"): qs=qs.filter(cohorte_id=request.GET["cohorte"])
    if request.GET.get("domaine"): qs=qs.filter(domaine_id=request.GET["domaine"])
    if request.GET.get("statut"): qs=qs.filter(statut=request.GET["statut"])
    domain_data=list(qs.values("domaine__nom").annotate(total=Count("id")).order_by("-total"))
    status_data=list(qs.values("statut").annotate(total=Count("id")))
    cohort_data=list(qs.values("cohorte__nom").annotate(total=Count("id")).order_by("cohorte__nom"))
    progress=list(qs.values("nom","progression").order_by("-progression")[:10])
    return render(request,"analytics.html",{"domain_json":json.dumps(domain_data),"status_json":json.dumps(status_data),"cohort_json":json.dumps(cohort_data),"progress_json":json.dumps(progress),"cohortes":Cohorte.objects.all(),"domaines":Domaine.objects.all(),"statuts":Projet.STATUTS})

@login_required
def ai_assistant(request):
    answer=None
    question=""
    if request.method=="POST":
        question=request.POST.get("question","").strip()
        stats=kpi_data()
        prompt_data={"kpi":{k:str(v) for k,v in stats.items()},"domaines":list(Projet.objects.values("domaine__nom").annotate(total=Count("id")).order_by("-total")),"retards":list(Projet.objects.filter(date_fin_prevue__lt=timezone.localdate()).exclude(statut="termine").values_list("nom",flat=True)[:10])}
        api_key=os.getenv("OPENAI_API_KEY","")
        if api_key and question:
            try:
                from openai import OpenAI
                client=OpenAI(api_key=api_key)
                completion=client.chat.completions.create(model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),messages=[
                    {"role":"system","content":"Tu es CIAT AI ANALYST. Réponds en français uniquement à partir du contexte chiffré fourni. N'invente aucun chiffre. Signale les limites des données."},
                    {"role":"user","content":f"Contexte base de données: {json.dumps(prompt_data,ensure_ascii=False)}\nQuestion: {question}"}
                ],temperature=0.2)
                answer=completion.choices[0].message.content
            except Exception as exc:
                answer=f"Le service IA distant est indisponible ({type(exc).__name__}). Mode de démonstration activé. "+demo_answer(question,stats,prompt_data)
        else:
            answer=demo_answer(question,stats,prompt_data)
    return render(request,"assistant.html",{"answer":answer,"question":question})

def demo_answer(question,stats,data):
    q=question.lower()
    if "retard" in q:
        return f"La base contient {stats['retard']} projet(s) en retard. Les échéances doivent être vérifiées avec les responsables."
    if "financement" in q:
        return f"Le montant total des financements obtenus enregistré dans la base est de {stats['financements']}."
    if "domaine" in q and data["domaines"]:
        d=data["domaines"][0]
        return f"Le domaine ayant le plus de projets enregistrés est {d['domaine__nom']} avec {d['total']} projet(s)."
    if "termin" in q:
        return f"La base contient {stats['termines']} projet(s) terminé(s)."
    return ("Voici la synthèse calculée depuis la base : "
            f"{stats['idees']} projets enregistrés, {stats['selectionnes']} sélectionnés ou engagés, "
            f"{stats['incubes']} en incubation/prototype, {stats['termines']} terminés et "
            f"{stats['retard']} en retard. Les données de démonstration sont fictives.")

@login_required
def export_excel(request):
    from openpyxl import Workbook
    wb=Workbook(); ws=wb.active; ws.title="Projets"
    ws.append(["Projet","Porteur","Domaine","Cohorte","Statut","Progression (%)","Budget","Financement"])
    for p in Projet.objects.select_related("porteur","domaine","cohorte"):
        ws.append([p.nom,p.porteur.nom_complet,p.domaine.nom,p.cohorte.nom if p.cohorte else "",p.get_statut_display(),p.progression,float(p.budget_previsionnel),float(p.financement_obtenu)])
    response=HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"]='attachment; filename="rapport_ciat.xlsx"'
    wb.save(response); return response

@login_required
def export_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    response=HttpResponse(content_type="application/pdf")
    response["Content-Disposition"]='attachment; filename="rapport_ciat.pdf"'
    c=canvas.Canvas(response,pagesize=A4); y=800
    c.setFont("Helvetica-Bold",16); c.drawString(50,y,"CIAT PILOTAGE — Rapport de synthèse"); y-=35
    c.setFont("Helvetica",10); c.drawString(50,y,f"Généré le {date.today().strftime('%d/%m/%Y')} — Données de démonstration si signalées fictives"); y-=30
    for key,val in kpi_data().items():
        c.drawString(60,y,f"{key.replace('_',' ').title()} : {val}"); y-=20
    y-=15; c.setFont("Helvetica-Bold",12); c.drawString(50,y,"Projets récents"); y-=25
    c.setFont("Helvetica",9)
    for p in Projet.objects.select_related("porteur")[:20]:
        c.drawString(55,y,f"- {p.nom[:55]} | {p.get_statut_display()} | {p.progression}%"); y-=15
        if y<60: c.showPage(); y=800; c.setFont("Helvetica",9)
    c.save(); return response
