from django.db import models
from django.contrib.auth.models import User
import json

CLASSES_CHOICES = [
    ('1am1', '1AM1'), ('1am2', '1AM2'), ('1am3', '1AM3'), ('1am4', '1AM4'), ('1am5', '1AM5'),
    ('2am1', '2AM1'), ('2am2', '2AM2'), ('2am3', '2AM3'), ('2am4', '2AM4'), ('2am5', '2AM5'),
    ('3am1', '3AM1'), ('3am2', '3AM2'), ('3am3', '3AM3'), ('3am4', '3AM4'), ('3am5', '3AM5'),
    ('4am1', '4AM1'), ('4am2', '4AM2'), ('4am3', '4AM3'), ('4am4', '4AM4'), ('4am5', '4AM5'),
]

class Eleve(models.Model):
    nom = models.CharField(max_length=100, verbose_name="الاسم")
    prenom = models.CharField(max_length=100, verbose_name="اللقب")
    classe = models.CharField(max_length=10, choices=CLASSES_CHOICES, verbose_name="القسم")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['nom', 'prenom', 'classe']
        verbose_name = "تلميذ"
        verbose_name_plural = "التلاميذ"
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.classe}"

class Fichier(models.Model):
    titre = models.CharField(max_length=200, verbose_name="العنوان")
    fichier = models.FileField(upload_to='fichiers/', verbose_name="الملف")
    classes_cibles = models.CharField(max_length=500, default='all', verbose_name="الأقسام المستهدفة")
    date_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "ملف"
        verbose_name_plural = "الملفات"
    
    def __str__(self):
        return self.titre

class Activite(models.Model):
    titre = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(verbose_name="الوصف")
    fichier_joint = models.FileField(upload_to='activites/', blank=True, null=True)
    classes_cibles = models.CharField(max_length=500, default='all')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "نشاط"
        verbose_name_plural = "الأنشطة"
    
    def __str__(self):
        return self.titre

class CompletionActivite(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    completee = models.BooleanField(default=False)
    date_completion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['eleve', 'activite']

class Exercice(models.Model):
    titre = models.CharField(max_length=200, verbose_name="العنوان")
    enonce = models.TextField(verbose_name="نص التمرين")
    classes_cibles = models.CharField(max_length=500, default='all')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "تمرين"
        verbose_name_plural = "التمارين"
    
    def __str__(self):
        return self.titre

class ReponseExercice(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    reponse = models.TextField(verbose_name="الإجابة")
    corrigee = models.BooleanField(default=False)
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['eleve', 'exercice']

class Note(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    note = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="العلامة")
    commentaire = models.TextField(blank=True, verbose_name="ملاحظة")
    date_attribution = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "علامة"
        verbose_name_plural = "العلامات"

class Message(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    contenu = models.TextField(verbose_name="المحتوى")
    expediteur = models.CharField(max_length=20, choices=[('eleve', 'تلميذ'), ('enseignant', 'أستاذ')])
    lu = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "الرسائل"
        ordering = ['-date_envoi']
        
# --- À AJOUTER À LA FIN DE app/backend/main/models.py ---

# ... (tous tes modèles existants Eleve, Fichier, Activite, etc. sont au-dessus) ...

NOTIFICATION_TYPES = [
    ('new_file', 'Nouveau Fichier'),
    ('new_activity', 'Nouvelle Activité'),
    ('new_exercise', 'Nouvel Exercice'),
    ('grade_updated', 'Note Mise à Jour'), # Pour une note d'exercice corrigé ou note générale
    ('new_message', 'Nouveau Message'),
    ('activity_reminder', 'Rappel d\'Activité'), # Exemple, peut être ajouté plus tard
]

class Notification(models.Model):
    destinataire = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255, verbose_name="Message de notification")
    lu = models.BooleanField(default=False, verbose_name="Lue")
    date_creation = models.DateTimeField(auto_now_add=True)
    type_notification = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='new_file', verbose_name="Type")
    # Optionnel: lien vers l'objet concerné (pour rediriger l'élève)
    # Par exemple, si c'est une notif pour un nouveau fichier, on pourrait stocker l'ID du fichier.
    # Cela peut être fait avec des GenericForeignKeys ou des champs ForeignKey optionnels vers chaque type d'objet.
    # Pour une version de base, on peut inclure l'info pertinente dans le 'message'.
    # Exemple plus avancé :
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    # object_id = models.PositiveIntegerField(null=True, blank=True)
    # content_object = GenericForeignKey('content_type', 'object_id')
    lien_relatif = models.CharField(max_length=200, blank=True, null=True, verbose_name="Lien relatif (frontend)")
    # Exemples de lien_relatif: '/student/dashboard/files', '/student/dashboard/exercises/view/5'

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Notification pour {self.destinataire.prenom} {self.destinataire.nom} : {self.message[:50]}"

# --- FIN DE L'AJOUT ---