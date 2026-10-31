# Cahier des charges — CIAT PILOTAGE
## Finalité
Centraliser le suivi des projets incubés, analyser les performances et aider les responsables à décider à partir d'indicateurs vérifiables.

## Utilisateurs
- Administrateur : administration complète.
- Coordonnateur : gestion opérationnelle.
- Analyste : consultation des analyses et rapports.

## Modules livrés dans cette version
Authentification Django, gestion des projets, cohortes, indicateurs, graphiques Chart.js, assistant IA (API facultative et mode démonstration), exports PDF/Excel et données de démonstration.

## Règles de gestion
Les KPI sont calculés à partir des enregistrements de la base. Un projet est considéré en retard lorsque sa date de fin prévue est passée et que son statut n'est pas « Terminé ». Les données de démonstration portent le marqueur fictif.

## Limites
Les alertes, notifications en temps réel, historique détaillé des jalons, comparaisons temporelles et gestion d'écran dédiée des partenaires/financements peuvent être approfondis dans une itération ultérieure. Les droits des rôles doivent être attribués et contrôlés avant déploiement.
