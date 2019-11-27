from django import forms
from django.forms.models import inlineformset_factory
from .models import Cours, Chapitre

ModuleFormset = inlineformset_factory(
                            Cours,
                            Chapitre,
                            fields=['titre', 'objectifs', 'duree', ],
                            extra=1,
                            can_delete=True
)