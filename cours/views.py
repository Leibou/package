from django.views.generic.list import ListView
from .models import Cours
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormset
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Chapitre, Content
from django.db.models import Count
from django.views.generic.detail import DetailView


class ManageCourseListView(ListView):
    model = Cours
    template_name = 'cours/gestion/cours/list.html'

    def get_queryset(self):
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(auteur=self.request.user)


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(auteur=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCoursMixin(OwnerMixin, LoginRequiredMixin):
    model = Cours
    fields = ['nom', 'slug', 'description']
    success_url = reverse_lazy('manage_cours_list')


class OwnerCoursEditMixin(OwnerCoursMixin, OwnerEditMixin):
    fields = ['nom', 'description', 'slug']
    success_url = reverse_lazy('manage_cours_list')
    template_name = 'cours/gestion/cours/form.html'


class ManageCoursListView(OwnerCoursMixin, ListView):
    template_name = 'cours/gestion/cours/list.html'


class CoursCreateView(PermissionRequiredMixin, OwnerCoursEditMixin, CreateView):
    permission_required = 'cours.add_cours'


class CoursUpdateView(PermissionRequiredMixin, OwnerCoursEditMixin, UpdateView):
    permission_required = 'cours.change_cours'


class CoursDeleteView(PermissionRequiredMixin,OwnerCoursMixin, DeleteView):
    template_name = 'cours/gestion/cours/delete.html'
    success_url = reverse_lazy('manage_cours_list')
    permission_required = 'cours.delete_cours'


class CoursModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'cours/gestion/chapitres/formset.html'
    cours = None

    def get_formset(self, data=None):
        return ModuleFormset(instance=self.cours, data=data)
 
    def dispatch(self, request, pk):
        self.cours = get_object_or_404(Cours, id=pk, auteur=request.user)
        return super(CoursModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'cours': self.cours, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_cours_list')
        return self.render_to_response({'cours': self.cours, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    chapitre = None
    model = None
    obj = None
    template_name = 'cours/gestion/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='cours', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['auteur',
                                                 'order',
                                                 'dateCreation'])
        return Form(*args, **kwargs)

    def dispatch(self, request, chapitre_id, model_name, id=None):
        self.chapitre = get_object_or_404(Chapitre,
                                          id=chapitre_id,
                                          cours__auteur=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         auteur=request.user)
        return super(ContentCreateUpdateView, self).dispatch(request, chapitre_id, model_name, id)

    def get(self, request, chapitre_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, chapitre_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.auteur = request.user
            obj.save()
            if not id:
                Content.objects.create(chapitre=self.chapitre, item=obj)
            return redirect('chapitre_content_list', self.chapitre.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    chapitre__cours__auteur=request.user

        )
        chapitre = content.chapitre
        content.item.delete()
        return redirect('chapitre_content_list', chapitre.id)


class ChapitreContentListView(TemplateResponseMixin, View):
    template_name = 'cours/gestion/chapitres/supports_list.html'

    def get(self, request, chapitre_id):
        chapitre = get_object_or_404(Chapitre,
                                     id = chapitre_id,
                                     cours__auteur=request.user)
        return self.render_to_response({'chapitre': chapitre})


class CoursListView(TemplateResponseMixin, View):
    model = Cours
    template_name = 'cours/cours/list.html'

    def get(self, request, cours=None):
        listcours = Cours.objects.annotate(
            total_chapitre = Count('cours')
        )
        chapitres = Chapitre.objects.annotate()
        if cours:
            cours = get_object_or_404(Cours, slug=cours)
            listcours.filter(cours=cours)
        
        return self.render_to_response({
            'cours': cours,
            'listcours': listcours,
            'chapitres': chapitres
        })

        
class CoursDetailView(DetailView):
    model = Cours
    template_name = 'cours/cours/detail.html'
