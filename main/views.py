# --- START OF FILE app/backend/main/views.py ---
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes as dec_permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Max, Count, Case, When # BooleanField n'est pas utilisé ici directement

# Assure-toi que tous les modèles et serializers nécessaires sont importés.
# L'import * est pratique mais lister explicitement est parfois plus clair pour le débogage.
from .models import Eleve, Fichier, Activite, Exercice, Note, Message, Notification, CompletionActivite, ReponseExercice
from .serializers import (
    EleveSerializer, FichierSerializer, ActiviteSerializer, ExerciceSerializer,
    ReponseExerciceSerializer, ReponseExerciceDetailSerializer, NoteSerializer,
    MessageSerializer, ConversationSerializer, NotificationSerializer # Ajout de NotificationSerializer
)

# --- FONCTION HELPER POUR LES NOTIFICATIONS (Partie 5.1) ---
def creer_notifications_pour_classes(classes_cibles_str, message_template, type_notification, lien_relatif_template=None, **kwargs):
    """
    Crée des notifications pour les élèves des classes cibles.
    """
    classes_list = [c.strip().lower() for c in classes_cibles_str.split(',') if c.strip()]
    eleves_a_notifier = []

    if not classes_list:
        return

    if 'all' in classes_list:
        eleves_a_notifier = Eleve.objects.all()
    else:
        eleves_a_notifier = Eleve.objects.filter(classe__in=classes_list)

    notifications_a_creer = []
    for eleve in eleves_a_notifier:
        message_final = message_template.format(**kwargs)
        lien_final = lien_relatif_template.format(**kwargs) if lien_relatif_template else None
        
        notifications_a_creer.append(
            Notification(
                destinataire=eleve,
                message=message_final,
                type_notification=type_notification,
                lien_relatif=lien_final
            )
        )
    
    if notifications_a_creer:
        Notification.objects.bulk_create(notifications_a_creer)
# --- FIN DE LA FONCTION HELPER ---


@api_view(['POST'])
@dec_permission_classes([AllowAny])
def login_eleve(request):
    nom = request.data.get('nom')
    prenom = request.data.get('prenom')
    try:
        eleve = Eleve.objects.get(nom__iexact=nom, prenom__iexact=prenom)
        return Response({'success': True, 'eleve': EleveSerializer(eleve).data})
    except Eleve.DoesNotExist:
        return Response({'success': False, 'message': 'التلميذ غير موجود'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@dec_permission_classes([AllowAny])
def login_enseignant(request):
    password = request.data.get('password')
    if password == 'admin123': 
        return Response({'success': True, 'message': 'Connexion enseignant réussie'})
    else:
        return Response({'success': False, 'message': 'كلمة المرور خاطئة'}, status=status.HTTP_400_BAD_REQUEST)

class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all().order_by('classe', 'nom', 'prenom')
    serializer_class = EleveSerializer
    def get_queryset(self):
        queryset = Eleve.objects.all().order_by('classe', 'nom', 'prenom')
        classe = self.request.query_params.get('classe', None)
        search = self.request.query_params.get('search', None)
        if classe:
            queryset = queryset.filter(classe=classe)
        if search:
            queryset = queryset.filter(Q(nom__icontains=search) | Q(prenom__icontains=search))
        return queryset

class FichierViewSet(viewsets.ModelViewSet):
    queryset = Fichier.objects.all().order_by('-date_upload')
    serializer_class = FichierSerializer

    # --- MODIFICATION (Partie 5.2) ---
    def perform_create(self, serializer):
        fichier_instance = serializer.save()
        creer_notifications_pour_classes(
            classes_cibles_str=fichier_instance.classes_cibles,
            message_template="Nouveau fichier '{titre}' disponible pour votre classe.",
            type_notification='new_file',
            lien_relatif_template="/student/dashboard/files",
            titre=fichier_instance.titre
        )
    # --- FIN MODIFICATION ---

@api_view(['GET'])
@dec_permission_classes([AllowAny])
def fichiers_eleve(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    fichiers = Fichier.objects.filter(
        Q(classes_cibles__iexact='all') | Q(classes_cibles__icontains=eleve.classe)
    ).order_by('-date_upload')
    serializer = FichierSerializer(fichiers, many=True)
    return Response(serializer.data)

class ActiviteViewSet(viewsets.ModelViewSet):
    queryset = Activite.objects.all().order_by('-date_creation')
    serializer_class = ActiviteSerializer

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        activite = self.get_object()
        cibles_str = activite.classes_cibles.lower()
        classes_cibles_list = [c.strip() for c in cibles_str.split(',') if c.strip()]
        if 'all' in classes_cibles_list:
            eleves_concernes = Eleve.objects.all()
        else:
            eleves_concernes = Eleve.objects.filter(classe__in=classes_cibles_list)
        completions = CompletionActivite.objects.filter(activite=activite, eleve__in=eleves_concernes).select_related('eleve')
        completions_dict = {comp.eleve.id: comp for comp in completions}
        progression_data = []
        for eleve_obj in eleves_concernes: # Renommé 'eleve' en 'eleve_obj' pour éviter conflit avec module 'eleve'
            completion_obj = completions_dict.get(eleve_obj.id)
            progression_data.append({
                'eleve_id': eleve_obj.id, 'eleve_nom': eleve_obj.nom, 'eleve_prenom': eleve_obj.prenom,
                'eleve_classe': eleve_obj.classe, 'completee': completion_obj.completee if completion_obj else False,
                'date_completion': completion_obj.date_completion if completion_obj else None,
            })
        return Response(sorted(progression_data, key=lambda x: (x['eleve_classe'], x['eleve_nom'])))

    # --- MODIFICATION (Partie 5.2) ---
    def perform_create(self, serializer):
        activite_instance = serializer.save()
        creer_notifications_pour_classes(
            classes_cibles_str=activite_instance.classes_cibles,
            message_template="Nouvelle activité '{titre}' assignée.",
            type_notification='new_activity',
            lien_relatif_template=f"/student/dashboard/activities", # Lien vers la page des activités
            # Ou /student/dashboard/activities/{activite_instance.id} si tu as une vue détail
            titre=activite_instance.titre
            # id=activite_instance.id # Si tu utilises {id}
        )
    # --- FIN MODIFICATION ---

@api_view(['GET'])
@dec_permission_classes([AllowAny])
def activites_eleve(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    activites = Activite.objects.filter(
        Q(classes_cibles__iexact='all') | Q(classes_cibles__icontains=eleve.classe)
    ).order_by('-date_creation')
    setattr(request, 'eleve_id', eleve_id) 
    serializer = ActiviteSerializer(activites, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@dec_permission_classes([AllowAny])
def completer_activite(request):
    eleve_id = request.data.get('eleve_id')
    activite_id = request.data.get('activite_id')
    get_object_or_404(Eleve, id=eleve_id)
    get_object_or_404(Activite, id=activite_id)
    completion, created = CompletionActivite.objects.get_or_create(
        eleve_id=eleve_id, activite_id=activite_id, defaults={'completee': True}
    )
    if not created and not completion.completee:
        completion.completee = True
        completion.save()
    return Response({'success': True, 'message': 'Activité marquée comme complétée.'})

class ExerciceViewSet(viewsets.ModelViewSet):
    queryset = Exercice.objects.all().order_by('-date_creation')
    serializer_class = ExerciceSerializer

    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        exercice = self.get_object()
        cibles_str = exercice.classes_cibles.lower()
        classes_cibles_list = [c.strip() for c in cibles_str.split(',') if c.strip()]
        if 'all' in classes_cibles_list:
            eleves_concernes = Eleve.objects.all()
        else:
            eleves_concernes = Eleve.objects.filter(classe__in=classes_cibles_list)
        reponses = ReponseExercice.objects.filter(exercice=exercice, eleve__in=eleves_concernes).select_related('eleve').order_by('eleve__classe', 'eleve__nom')
        serializer = ReponseExerciceDetailSerializer(reponses, many=True)
        return Response(serializer.data)

    # --- MODIFICATION (Partie 5.2) ---
    def perform_create(self, serializer):
        exercice_instance = serializer.save()
        creer_notifications_pour_classes(
            classes_cibles_str=exercice_instance.classes_cibles,
            message_template="Nouvel exercice '{titre}' disponible.",
            type_notification='new_exercise',
            lien_relatif_template=f"/student/dashboard/exercises", # Lien vers la page des exercices
            # Ou /student/dashboard/exercises/{exercice_instance.id} si tu as une vue détail
            titre=exercice_instance.titre
            # id=exercice_instance.id # Si tu utilises {id}
        )
    # --- FIN MODIFICATION ---

@api_view(['GET'])
@dec_permission_classes([AllowAny])
def exercices_eleve(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    exercices = Exercice.objects.filter(
        Q(classes_cibles__iexact='all') | Q(classes_cibles__icontains=eleve.classe)
    ).order_by('-date_creation')
    setattr(request, 'eleve_id', eleve_id)
    serializer = ExerciceSerializer(exercices, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@dec_permission_classes([AllowAny])
def soumettre_reponse(request):
    eleve_id = request.data.get('eleve_id')
    exercice_id = request.data.get('exercice_id')
    reponse_text = request.data.get('reponse')
    get_object_or_404(Eleve, id=eleve_id)
    get_object_or_404(Exercice, id=exercice_id)
    reponse, created = ReponseExercice.objects.update_or_create(
        eleve_id=eleve_id, exercice_id=exercice_id,
        defaults={'reponse': reponse_text, 'corrigee': False, 'note': None}
    )
    return Response({'success': True, 'message': 'Réponse soumise.'})

class ReponseExerciceViewSet(viewsets.ModelViewSet):
    queryset = ReponseExercice.objects.all()
    serializer_class = ReponseExerciceDetailSerializer

    # --- MODIFICATION (Partie 5.4 - Optionnel mais inclus) ---
    def perform_update(self, serializer):
        # Récupère l'instance avant la mise à jour pour comparer l'état 'corrigee'
        # reponse_instance_avant_update = self.get_object() # Pas nécessaire si on vérifie juste le flag 'corrigee' envoyé
        
        # Pour vérifier si la note a été effectivement ajoutée/changée et si 'corrigee' est passé à True
        # On doit inspecter les données validées avant de sauvegarder, ou comparer avant/après.
        # Une approche plus simple: si 'note' est dans les données validées et 'corrigee' est True.
        
        old_corrigee_status = ReponseExercice.objects.get(pk=serializer.instance.pk).corrigee
        
        reponse_instance_apres_update = serializer.save()

        # Notifier si la réponse vient d'être marquée comme corrigée ET qu'une note est présente
        if not old_corrigee_status and reponse_instance_apres_update.corrigee and reponse_instance_apres_update.note is not None:
            Notification.objects.create(
                destinataire=reponse_instance_apres_update.eleve,
                message=f"Votre réponse à l'exercice '{reponse_instance_apres_update.exercice.titre}' a été notée : {reponse_instance_apres_update.note}/20.",
                type_notification='grade_updated',
                lien_relatif=f"/student/dashboard/exercises"
                # lien_relatif=f"/student/dashboard/exercises/{reponse_instance_apres_update.exercice.id}" # Si tu as une vue exercice détail
            )
    # --- FIN MODIFICATION ---


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().order_by('-date_attribution')
    serializer_class = NoteSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        eleve_id = self.request.query_params.get('eleve_id')
        classe = self.request.query_params.get('classe')
        if eleve_id:
            queryset = queryset.filter(eleve_id=eleve_id)
        if classe:
            queryset = queryset.filter(eleve__classe=classe)
        return queryset
    
    # Optionnel: Notifier l'élève quand une note générale est ajoutée
    def perform_create(self, serializer):
        note_instance = serializer.save()
        Notification.objects.create(
            destinataire=note_instance.eleve,
            message=f"Une nouvelle note générale a été publiée : {note_instance.note}/20. Commentaire: {note_instance.commentaire[:30]}...",
            type_notification='grade_updated', # Peut-être un type 'new_general_note' ?
            lien_relatif=f"/student/dashboard/grades"
        )


@api_view(['GET'])
@dec_permission_classes([AllowAny])
def note_eleve(request, eleve_id):
    notes = Note.objects.filter(eleve_id=eleve_id).order_by('-date_attribution')
    if not notes.exists():
         return Response([], status=status.HTTP_200_OK)
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-date_envoi')
    serializer_class = MessageSerializer

@api_view(['GET'])
@dec_permission_classes([AllowAny])
def teacher_conversations(request):
    eleves_converses = Eleve.objects.annotate(
        dernier_message_date=Max('message__date_envoi'),
        non_lus_enseignant=Count(Case(When(message__expediteur='eleve', message__lu=False, then=1)))
    ).filter(message__isnull=False).distinct().order_by('-dernier_message_date')
    data = []
    for eleve_obj in eleves_converses: # Renommé 'eleve' en 'eleve_obj'
        dernier_message_obj = Message.objects.filter(eleve=eleve_obj).latest('date_envoi')
        data.append({
            'eleve_id': eleve_obj.id, 'eleve_nom': eleve_obj.nom, 'eleve_prenom': eleve_obj.prenom,
            'eleve_classe': eleve_obj.classe,
            'dernier_message_contenu': dernier_message_obj.contenu[:50] + '...' if dernier_message_obj.contenu and len(dernier_message_obj.contenu) > 50 else dernier_message_obj.contenu,
            'dernier_message_date': dernier_message_obj.date_envoi,
            'dernier_message_expediteur': dernier_message_obj.expediteur,
            'non_lus_enseignant': eleve_obj.non_lus_enseignant
        })
    serializer = ConversationSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@dec_permission_classes([AllowAny])
def messages_eleve(request, eleve_id):
    get_object_or_404(Eleve, id=eleve_id)
    # Marquer comme lu par l'enseignant si c'est lui qui consulte.
    # Pour cette démo, on suppose que si l'URL contient '/teacher/', c'est l'enseignant.
    # Ceci est une simplification. Une vraie solution utiliserait l'authentification.
    if '/teacher/' in request.path: # Simple vérification de l'URL
         Message.objects.filter(eleve_id=eleve_id, expediteur='eleve', lu=False).update(lu=True)
    
    messages = Message.objects.filter(eleve_id=eleve_id).order_by('date_envoi')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@dec_permission_classes([AllowAny])
def envoyer_message(request): # --- MODIFICATION (Partie 5.3) ---
    eleve_id = request.data.get('eleve')
    contenu = request.data.get('contenu')
    expediteur = request.data.get('expediteur')

    if not all([eleve_id, contenu, expediteur]):
        return Response({'error': 'Données manquantes (eleve, contenu, expediteur requis).'}, status=status.HTTP_400_BAD_REQUEST)
    
    eleve_obj = get_object_or_404(Eleve, id=eleve_id)

    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        message_instance = serializer.save()

        if expediteur == 'enseignant': # Si c'est l'enseignant qui envoie
            Notification.objects.create(
                destinataire=eleve_obj,
                message=f"Nouveau message de l'enseignant: \"{message_instance.contenu[:30]}...\"", # Message plus court
                type_notification='new_message',
                lien_relatif=f"/student/dashboard/messages"
            )
        # Si c'est l'élève qui envoie, on pourrait aussi notifier l'enseignant,
        # mais cela sort du cadre du système de notification pour l'élève.
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# --- FIN MODIFICATION ---


# --- VUES POUR LES NOTIFICATIONS (déjà ajoutées à l'étape précédente, vérifie qu'elles sont là) ---
@api_view(['GET'])
@dec_permission_classes([AllowAny])
def get_eleve_notifications(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    notifications = Notification.objects.filter(destinataire=eleve)
    lu_filter = request.query_params.get('lu')
    if lu_filter is not None:
        notifications = notifications.filter(lu=lu_filter.lower() == 'true')
    notifications = notifications.order_by('-date_creation')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@dec_permission_classes([AllowAny])
def mark_notification_as_read(request, eleve_id, notification_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    notification = get_object_or_404(Notification, id=notification_id, destinataire=eleve)
    if not notification.lu:
        notification.lu = True
        notification.save()
        return Response({'status': 'notification marquée comme lue'}, status=status.HTTP_200_OK)
    return Response({'status': 'notification déjà lue'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@dec_permission_classes([AllowAny])
def mark_all_notifications_as_read(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    updated_count = Notification.objects.filter(destinataire=eleve, lu=False).update(lu=True)
    if updated_count > 0:
        return Response({'status': f'{updated_count} notifications marquées comme lues'}, status=status.HTTP_200_OK)
    return Response({'status': 'aucune notification non lue à marquer'}, status=status.HTTP_200_OK)

# --- END OF FILE app/backend/main/views.py ---