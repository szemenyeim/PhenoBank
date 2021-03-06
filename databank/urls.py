from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .forms import PropertyMain, PropertyChoice, PropertyNumeric, IndividualMain, PropertyFormSet
from .views import PropertyWizard, isNumber, isMulti, IndividualWizard, model_form_upload, delete_image, animal_download, property_delete, searchProperty, privacy, individual_list
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django_filters.views import FilterView

property_forms = [PropertyMain, PropertyChoice, PropertyNumeric]
inidividual_forms = [IndividualMain, PropertyFormSet]

urlpatterns = [
    path('', views.index, name='index'),
    path('spec/<pk>/', login_required(views.speciesSelector), name='species-selection'),
    path('individuals/', login_required(individual_list), name='individuals'),
    path('individual/<pk>/', login_required(views.IndividualDetailView.as_view()), name='individual-detail'),
    path('individual/download/<pk>/<format>', login_required(animal_download), name='individual-download'),
    path('properties/', login_required(views.PropertyListView.as_view()), name='properties'),
    path('property/<pk>/', login_required(views.PropertyDetailView.as_view()), name='property-detail'),
    path('search/<pk>/', login_required(searchProperty), name='search'),
    path('privacy/', privacy, name='privacy'),
    path('property/delete/<pk>/', login_required(property_delete), name='property-delete'),
    path('properties/new/', staff_member_required(PropertyWizard.as_view(property_forms,
        condition_dict={'1': isMulti, '2': isNumber}
    ))),
    path('individuals/new/', login_required(IndividualWizard.as_view(inidividual_forms))),
    path('individuals/edit/<pk>/', login_required(IndividualWizard.as_view(inidividual_forms)), name='individual-edit'),
    path('individuals/add_image/<pk>/', login_required(model_form_upload), name='individual-image-add'),
    path('delete-image/<pk>/', login_required(delete_image), name='delete_image'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>[0-9A-Za-z_\-]/<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('signup/', views.signup, name='signup'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>[0-9A-Za-z_\-]/<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/',
         views.activate, name='activate'),
    path('captcha/', include('captcha.urls')),
]