from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .forms import PropertyMain, PropertyChoice, PropertyNumeric, IndividualMain, PropertyFormSet, SpeciesSelector
from .views import PropertyWizard, isNumber, isMulti, IndividualWizard, model_form_upload, delete_image, animal_download, property_delete, searchProperty
from .filters import IndividualFilter
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django_filters.views import FilterView

property_forms = [SpeciesSelector, PropertyMain, PropertyChoice, PropertyNumeric]
inidividual_forms = [SpeciesSelector, IndividualMain, PropertyFormSet]

urlpatterns = [
    path('', views.index, name='index'),
    path('individuals/', login_required(FilterView.as_view(filterset_class=IndividualFilter)), name='individuals'),
    path('individual/<pk>/', login_required(views.IndividualDetailView.as_view()), name='individual-detail'),
    path('individual/download/<pk>/', login_required(animal_download), name='individual-download'),
    path('properties/', login_required(views.PropertyListView.as_view()), name='properties'),
    path('property/<pk>/', login_required(views.PropertyDetailView.as_view()), name='property-detail'),
    path('search/<pk>/', login_required(searchProperty), name='search'),
    path('property/delete/<pk>/', login_required(property_delete), name='property-delete'),
    path('properties/new/', staff_member_required(PropertyWizard.as_view(property_forms,
        condition_dict={'2': isMulti, '3': isNumber}
    ))),
    path('individuals/new/', login_required(IndividualWizard.as_view(inidividual_forms))),
    path('individuals/edit/<pk>/', login_required(IndividualWizard.as_view(inidividual_forms,
        condition_dict={'0': False})), name='individual-edit'),
    path('individuals/add_image/<pk>/', login_required(model_form_upload), name='individual-image-add'),
    path('delete-image/<pk>/', login_required(delete_image), name='delete_image'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('password_reset/', auth_views.password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>[0-9A-Za-z_\-]/<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', auth_views.password_reset_complete, name='password_reset_complete'),
    path('signup/', views.signup, name='signup'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>[0-9A-Za-z_\-]/<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/',
         views.activate, name='activate'),
    path('captcha/', include('captcha.urls')),
]