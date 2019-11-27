from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .Fields import OrderField
from datetime import timedelta

class Cours(models.Model):
    auteur = models.ForeignKey(User,
                               related_name='cours_crée_par',
                               on_delete=models.CASCADE)
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    dateCreation = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Chapitre(models.Model):
    cours = models.ForeignKey(Cours,
                              related_name='cours',
                              on_delete=models.CASCADE)
    titre = models.CharField(max_length=120)
    objectifs = models.TextField(blank=True)
    dateCreation = models.DateTimeField(auto_now_add=True)
    duree = models.DurationField(default=timedelta(minutes=30))
    order = OrderField(blank=True, for_fields=['cours'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.order, self.titre)


class Exercie(models.Model):
    chapitre = models.ForeignKey(Chapitre,
                                 related_name='chapitre',
                                 on_delete=models.CASCADE)
    numero = models.IntegerField()
    contenu = models.TextField()
    dateCreation = models.DateTimeField()


class Content(models.Model):
    chapitre = models.ForeignKey(Chapitre,
                                 related_name='contents',
                                 on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': (
                                         'text',
                                         'video',
                                         'image',
                                         'file'
                                     )})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['chapitre'])

    class Meta:
        ordering = ['order']

 
class ItemBase(models.Model):
    auteur = models.ForeignKey(User,
                               related_name='%(class)s_related',
                               on_delete=models.CASCADE)
    titre = models.CharField(max_length=250)
    dateCreation = models.DateTimeField(auto_now_add=True)
    dateMAJ = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.titre


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    file = models.FileField(upload_to='videos')
