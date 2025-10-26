# --- START OF FILE app/backend/main/admin.py ---
from django.contrib import admin
from .models import Eleve, Fichier, Activite, Exercice, Note, Message, Notification, CompletionActivite, ReponseExercice
# J'ai listé explicitement les modèles importés pour plus de clarté,
# mais "from .models import *" fonctionne aussi.

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'classe', 'date_creation']
    list_filter = ['classe']
    search_fields = ['nom', 'prenom']
    ordering = ['classe', 'nom', 'prenom']

@admin.register(Fichier)
class FichierAdmin(admin.ModelAdmin):
    list_display = ['titre', 'get_classes_cibles_display', 'date_upload']
    list_filter = ['classes_cibles'] # Ce filtre sera basique car c'est un champ texte
    search_fields = ['titre']
    ordering = ['-date_upload']

    def get_classes_cibles_display(self, obj):
        return obj.classes_cibles.upper()
    get_classes_cibles_display.short_description = 'Classes Cibles'

@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'get_classes_cibles_display', 'date_creation']
    list_filter = ['classes_cibles']
    search_fields = ['titre']
    ordering = ['-date_creation']

    def get_classes_cibles_display(self, obj):
        return obj.classes_cibles.upper()
    get_classes_cibles_display.short_description = 'Classes Cibles'

@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = ['titre', 'get_classes_cibles_display', 'date_creation']
    list_filter = ['classes_cibles']
    search_fields = ['titre']
    ordering = ['-date_creation']

    def get_classes_cibles_display(self, obj):
        return obj.classes_cibles.upper()
    get_classes_cibles_display.short_description = 'Classes Cibles'

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'note', 'commentaire_court', 'date_attribution']
    list_filter = ['eleve__classe']
    search_fields = ['eleve__nom', 'eleve__prenom', 'commentaire']
    autocomplete_fields = ['eleve'] # Facilite la sélection de l'élève
    ordering = ['-date_attribution']

    def commentaire_court(self, obj):
        return obj.commentaire[:50] + '...' if len(obj.commentaire) > 50 else obj.commentaire
    commentaire_court.short_description = 'Commentaire'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'expediteur', 'contenu_court', 'lu', 'date_envoi']
    list_filter = ['expediteur', 'lu', 'eleve__classe']
    search_fields = ['eleve__nom', 'eleve__prenom', 'contenu']
    autocomplete_fields = ['eleve']
    ordering = ['-date_envoi']

    def contenu_court(self, obj):
        return obj.contenu[:75] + '...' if len(obj.contenu) > 75 else obj.contenu
    contenu_court.short_description = 'Contenu'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('destinataire', 'message_court', 'type_notification', 'lu', 'date_creation', 'lien_relatif')
    list_filter = ('lu', 'type_notification', 'destinataire__classe')
    search_fields = ('destinataire__nom', 'destinataire__prenom', 'message')
    readonly_fields = ('date_creation',)
    autocomplete_fields = ['destinataire']
    ordering = ['-date_creation']

    fieldsets = (
        (None, {
            'fields': ('destinataire', 'message', 'type_notification', 'lien_relatif')
        }),
        ('Statut', {
            'fields': ('lu', 'date_creation')
        }),
    )

    def message_court(self, obj):
        return obj.message[:75] + '...' if len(obj.message) > 75 else obj.message
    message_court.short_description = 'Message'


@admin.register(CompletionActivite)
class CompletionActiviteAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'activite', 'completee', 'date_completion')
    list_filter = ('completee', 'activite__titre', 'eleve__classe')
    autocomplete_fields = ['eleve', 'activite']
    ordering = ['-date_completion']

@admin.register(ReponseExercice)
class ReponseExerciceAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'exercice', 'reponse_courte', 'corrigee', 'note', 'date_soumission')
    list_filter = ('corrigee', 'exercice__titre', 'eleve__classe')
    search_fields = ('eleve__nom', 'eleve__prenom', 'reponse')
    autocomplete_fields = ['eleve', 'exercice']
    ordering = ['-date_soumission']
    
    def reponse_courte(self, obj):
        return obj.reponse[:75] + '...' if len(obj.reponse) > 75 else obj.reponse
    reponse_courte.short_description = 'Réponse Élève'

# --- END OF FILE app/backend/main/admin.py ---