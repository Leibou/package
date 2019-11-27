from django.urls import path
from . import views


urlpatterns = [
    path('mescours/', views.ManageCourseListView.as_view(), name='manage_cours_list'),
    path('<pk>/chapitre/', views.CoursModuleUpdateView.as_view(), name='cours_chapitre_update'),
    path('chapitre/<int:chapitre_id>/content/<model_name>/create/',
         views.ContentCreateUpdateView.as_view(), name='chapitre_content_create'),
    path('content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='chapitre_content_delete'),
    path('chapitre/<int:chapitre_id>/content/<model_name>/<id>/', views.ContentCreateUpdateView.as_view(), name='chapitre_content_update'),
    path('chapitre/<int:chapitre_id>/', views.ChapitreContentListView.as_view(), name='chapitre_content_list'),
    path('create/', views.CoursCreateView.as_view(), name='cours_create'),
    path('<pk>/edit/', views.CoursUpdateView.as_view(), name='cours_edit'),
    path('<pk>/delete/', views.CoursDeleteView.as_view(), name='cours_delete'),
    path('cours/<slug:cours>)/', views.CoursListView.as_view(), name='cours_list'),
    path('<slug:slug>/', views.CoursDetailView.as_view(), name='cours_detail'),
]
