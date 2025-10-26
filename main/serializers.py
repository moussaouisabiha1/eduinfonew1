# --- START OF FILE app/backend/main/serializers.py ---
from rest_framework import serializers
from .models import *

class EleveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleve
        fields = '__all__'

class FichierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fichier
        fields = '__all__'

class ActiviteSerializer(serializers.ModelSerializer):
    completion_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Activite
        fields = '__all__' # Conserve tous les champs pour l'enseignant
    
    def get_completion_status(self, obj):
        # Ce champ est plus pertinent pour la vue élève.
        # Pour l'enseignant, on aura une vue dédiée à la progression.
        request = self.context.get('request')
        if request and hasattr(request, 'eleve_id'): # Contexte pour élève
            try:
                completion = CompletionActivite.objects.get(
                    eleve_id=request.eleve_id,
                    activite=obj
                )
                return completion.completee
            except CompletionActivite.DoesNotExist:
                return False
        return None # Retourne None si pas de contexte élève

class CompletionActiviteEleveSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.nom', read_only=True)
    eleve_prenom = serializers.CharField(source='eleve.prenom', read_only=True)
    eleve_classe = serializers.CharField(source='eleve.classe', read_only=True)

    class Meta:
        model = CompletionActivite
        fields = ['eleve_id', 'eleve_nom', 'eleve_prenom', 'eleve_classe', 'completee', 'date_completion']


class ExerciceSerializer(serializers.ModelSerializer):
    reponse_eleve = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercice
        fields = '__all__' # Conserve tous les champs pour l'enseignant
    
    def get_reponse_eleve(self, obj):
        # Ce champ est plus pertinent pour la vue élève.
        # Pour l'enseignant, on aura une vue dédiée aux réponses.
        request = self.context.get('request')
        if request and hasattr(request, 'eleve_id'): # Contexte pour élève
            try:
                reponse = ReponseExercice.objects.get(
                    eleve_id=request.eleve_id,
                    exercice=obj
                )
                return {
                    'reponse_id': reponse.id,
                    'reponse': reponse.reponse,
                    'note': float(reponse.note) if reponse.note else None,
                    'corrigee': reponse.corrigee
                }
            except ReponseExercice.DoesNotExist:
                return None
        return None # Retourne None si pas de contexte élève


class ReponseExerciceSerializer(serializers.ModelSerializer): # Pour soumission par l'élève
    class Meta:
        model = ReponseExercice
        fields = '__all__'

class ReponseExerciceDetailSerializer(serializers.ModelSerializer): # Pour la vue enseignant
    eleve_nom = serializers.CharField(source='eleve.nom', read_only=True)
    eleve_prenom = serializers.CharField(source='eleve.prenom', read_only=True)
    eleve_classe = serializers.CharField(source='eleve.classe', read_only=True)

    class Meta:
        model = ReponseExercice
        fields = ['id', 'eleve', 'eleve_nom', 'eleve_prenom', 'eleve_classe', 'exercice', 'reponse', 'corrigee', 'note', 'date_soumission']
        read_only_fields = ['eleve', 'exercice', 'reponse', 'date_soumission'] # L'enseignant modifie corrigee et note

class NoteSerializer(serializers.ModelSerializer):
    eleve_details = EleveSerializer(source='eleve', read_only=True) # Pour afficher les détails de l'élève avec la note
    class Meta:
        model = Note
        fields = ['id', 'eleve', 'eleve_details', 'note', 'commentaire', 'date_attribution']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ConversationSerializer(serializers.Serializer): # Pour la liste des conversations de l'enseignant
    eleve_id = serializers.IntegerField()
    eleve_nom = serializers.CharField()
    eleve_prenom = serializers.CharField()
    eleve_classe = serializers.CharField()
    dernier_message_contenu = serializers.CharField(allow_null=True)
    dernier_message_date = serializers.DateTimeField(allow_null=True)
    dernier_message_expediteur = serializers.CharField(allow_null=True)
    non_lus_enseignant = serializers.IntegerField() # Messages de l'élève non lus par l'enseignant

# --- À AJOUTER DANS app/backend/main/serializers.py (par exemple, après MessageSerializer) ---

# ... (tous tes serializers existants sont au-dessus) ...

class NotificationSerializer(serializers.ModelSerializer):
    # Optionnel: Si tu veux afficher plus de détails que juste l'ID du destinataire.
    # destinataire_details = EleveSerializer(source='destinataire', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'message', 'lu', 'date_creation', 'type_notification', 'lien_relatif']
        # 'destinataire' n'est pas inclus ici car l'API sera typiquement pour un élève spécifique,
        # donc le destinataire est implicite. Si besoin, on peut l'ajouter.
        read_only_fields = ['date_creation', 'message', 'type_notification', 'lien_relatif'] # L'élève ne modifie que 'lu' via des actions.

