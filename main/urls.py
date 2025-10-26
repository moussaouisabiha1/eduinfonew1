# --- START OF FILE app/backend/main/urls.py ---
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'eleves', views.EleveViewSet)
router.register(r'fichiers', views.FichierViewSet)
router.register(r'activites', views.ActiviteViewSet)
router.register(r'exercices', views.ExerciceViewSet)
router.register(r'reponses-exercice', views.ReponseExerciceViewSet, basename='reponseexercice') # Pour noter
router.register(r'notes', views.NoteViewSet) # Notes générales
router.register(r'messages-admin', views.MessageViewSet, basename='message-admin') # Pour admin/debug si besoin

urlpatterns = [
    path('', include(router.urls)),
    
    # Authentification
    path('login/eleve/', views.login_eleve, name='login_eleve'),
    path('login/enseignant/', views.login_enseignant, name='login_enseignant'),
    
    # Endpoints spécifiques aux élèves (déjà existants)
    path('eleve/<int:eleve_id>/fichiers/', views.fichiers_eleve, name='fichiers_eleve'),
    path('eleve/<int:eleve_id>/activites/', views.activites_eleve, name='activites_eleve'),
    path('eleve/<int:eleve_id>/exercices/', views.exercices_eleve, name='exercices_eleve'),
    path('eleve/<int:eleve_id>/notes/', views.note_eleve, name='note_eleve'), # Renommé pour clarté (anciennement /note/)
    path('eleve/<int:eleve_id>/messages/', views.messages_eleve, name='messages_eleve_pour_eleve'), # Pour l'élève consultant ses messages

    path('completer-activite/', views.completer_activite, name='completer_activite'),
    path('soumettre-reponse/', views.soumettre_reponse, name='soumettre_reponse'),
    path('envoyer-message/', views.envoyer_message, name='envoyer_message'), # Commun élève/enseignant

    # Endpoints spécifiques à l'enseignant
    path('teacher/conversations/', views.teacher_conversations, name='teacher_conversations'),
    path('teacher/messages/<int:eleve_id>/', views.messages_eleve, name='teacher_messages_for_eleve'), # L'enseignant consulte les messages d'un élève
]
# --- END OF FILE app/backend/main/urls.py ---

# --- MODIFIER app/backend/main/urls.py ---

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Assure-toi que views est bien importé

router = DefaultRouter()
router.register(r'eleves', views.EleveViewSet)
router.register(r'fichiers', views.FichierViewSet)
router.register(r'activites', views.ActiviteViewSet)
router.register(r'exercices', views.ExerciceViewSet)
router.register(r'reponses-exercice', views.ReponseExerciceViewSet, basename='reponseexercice')
router.register(r'notes', views.NoteViewSet)
router.register(r'messages-admin', views.MessageViewSet, basename='message-admin')

urlpatterns = [
    path('', include(router.urls)),

    # Authentification
    path('login/eleve/', views.login_eleve, name='login_eleve'),
    path('login/enseignant/', views.login_enseignant, name='login_enseignant'),

    # Endpoints spécifiques aux élèves
    path('eleve/<int:eleve_id>/fichiers/', views.fichiers_eleve, name='fichiers_eleve'),
    path('eleve/<int:eleve_id>/activites/', views.activites_eleve, name='activites_eleve'),
    path('eleve/<int:eleve_id>/exercices/', views.exercices_eleve, name='exercices_eleve'),
    path('eleve/<int:eleve_id>/notes/', views.note_eleve, name='note_eleve'),
    path('eleve/<int:eleve_id>/messages/', views.messages_eleve, name='messages_eleve_pour_eleve'),

    # Actions élèves
    path('completer-activite/', views.completer_activite, name='completer_activite'),
    path('soumettre-reponse/', views.soumettre_reponse, name='soumettre_reponse'),
    
    # Messages (commun)
    path('envoyer-message/', views.envoyer_message, name='envoyer_message'),

    # Endpoints spécifiques à l'enseignant
    path('teacher/conversations/', views.teacher_conversations, name='teacher_conversations'),
    path('teacher/messages/<int:eleve_id>/', views.messages_eleve, name='teacher_messages_for_eleve'),

    # --- AJOUTER LES URLS POUR LES NOTIFICATIONS CI-DESSOUS ---
    path('eleve/<int:eleve_id>/notifications/', views.get_eleve_notifications, name='get_eleve_notifications'),
    path('eleve/<int:eleve_id>/notifications/<int:notification_id>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('eleve/<int:eleve_id>/notifications/mark-all-as-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    # --- FIN DE L'AJOUT ---
]
# --- FIN DES MODIFICATIONS ---