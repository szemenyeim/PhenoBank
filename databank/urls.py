from django.urls import path
from . import views
from .forms import PropertyMain, PropertyChoice, PropertyNumeric
from .views import PropertyWizard, isNumber, isMulti

property_forms = [PropertyMain, PropertyChoice, PropertyNumeric]

urlpatterns = [
    path('', views.index, name='index'),
    path('individuals/', views.IndividualListView.as_view(), name='individuals'),
    path(r'individual/(?P<pk>\d+)$', views.IndividualDetailView.as_view(), name='individual-detail'),
    path('properties/', views.PropertyListView.as_view(), name='properties'),
    path(r'property/(?P<pk>\d+)$', views.PropertyDetailView.as_view(), name='property-detail'),
    path('addproperty/', PropertyWizard.as_view(property_forms,
        condition_dict={'1': isMulti, '2': isNumber}
    )),
]