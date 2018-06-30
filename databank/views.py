from django.shortcuts import render

# Create your views here.
from .models import Species, Subspecies, Location, Individual, Option, Property_base, Property
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView


def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_phenomes = Individual.objects.all().count()
    # Available books (status = 'a')
    num_species = Species.objects.count()  # The 'all()' is implied by default.
    num_locations = Location.objects.count()  # The 'all()' is implied by default.

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_phenomes': num_phenomes, 'num_species': num_species,
                 'num_locations': num_locations},
    )

from django.views import generic

class IndividualListView(generic.ListView):
    model = Individual
    paginate_by = 100

class IndividualDetailView(generic.DetailView):
    model = Individual

class PropertyListView(generic.ListView):
    model = Property_base
    paginate_by = 100

class PropertyDetailView(generic.DetailView):
    model = Property_base
    def get_context_data(self, *args, **kwargs):
        context = super(PropertyDetailView, self).get_context_data(*args, **kwargs)
        context['property_base_list'] = Property_base.objects.all()
        return context

def isNumber(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    # check if the property is a number
    return cleaned_data.get('type', True) == ['F']

def isMulti(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    # check if the property is multiple choice
    return cleaned_data.get('type', True) == ['C']

class PropertyWizard(SessionWizardView):
    def get_template_names(self):
        return "databank/property_form.html"

    def done(self, form_list, **kwargs):

        return HttpResponseRedirect('../properties/')