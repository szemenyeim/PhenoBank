from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .forms import PropertyMain, PropertyChoice, PropertyNumeric, IndividualMain, PropertyFormSet, SpeciesSelector
from .views import PropertyWizard, isNumber, isMulti, IndividualWizard, model_form_upload, delete_image
from .filters import IndividualFilter
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django_filters.views import FilterView

property_forms = [SpeciesSelector, PropertyMain, PropertyChoice, PropertyNumeric]
inidividual_forms = [SpeciesSelector, IndividualMain, PropertyFormSet]

urlpatterns = [
    path('', views.index, name='index'),
    path('individuals/', login_required(FilterView.as_view(filterset_class=IndividualFilter)), name='individuals'),
    path(r'individual/(?P<pk>\d+)$', login_required(views.IndividualDetailView.as_view()), name='individual-detail'),
    path('properties/', login_required(views.PropertyListView.as_view()), name='properties'),
    path(r'property/(?P<pk>\d+)$', login_required(views.PropertyDetailView.as_view()), name='property-detail'),
    path('properties/new/', staff_member_required(PropertyWizard.as_view(property_forms,
        condition_dict={'2': isMulti, '3': isNumber}
    ))),
    path('individuals/new/', login_required(IndividualWizard.as_view(inidividual_forms))),
    path(r'individuals/edit/(?P<pk>\d+)/$', login_required(IndividualWizard.as_view(inidividual_forms,
        condition_dict={'0': False})), name='individual-edit'),
    path(r'individuals/add_image/(?P<pk>\d+)/$', login_required(model_form_upload), name='individual-image-add'),
    path(r'delete-image/(?P<pk>\d+)/$', login_required(delete_image), name='delete_image'),
    path(r'login/*', auth_views.login, name='login'),
    path(r'logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    path(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    path(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    path(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    path(r'^signup/$', views.signup, name='signup'),
    path(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
         views.activate, name='activate'),
    path(r'^captcha/', include('captcha.urls')),
]