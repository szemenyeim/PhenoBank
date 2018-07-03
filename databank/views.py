from .models import Species, Subspecies, Location, Individual, Option, Property_base, Property, Image
from django.http import HttpResponseRedirect, HttpResponseForbidden
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .forms import SignUpForm
from .tokens import account_activation_token
from django.utils.encoding import force_text
from django.contrib.auth import login
from django.contrib.auth.models import User

# Create your views here.

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

    species = None

    def get_form_kwargs(self, step):
        if step == '1':
            return {'species' : self.species}
        return {}

    def get_template_names(self):
        return "databank/property_form.html"

    def process_step(self, form):
        formData = self.get_form_step_data(form)
        if self.steps.current == '0':
            self.species = formData.get('0-species')
        return formData

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        prop = Property_base.objects.create(
            name = data['name'],
            species = data['species'],
            parent = data['parent'],
            type = data['type'][0],
        )
        if( data['type'] == ['F'] ):
            prop.minVal = data['minVal']
            prop.maxVal = data['maxVal']
            prop.save()
        elif(data['type'] == ['C']):
            for i in range(10):
                optName = "opt%d" % (i+1)
                if( data[optName] != "" ):
                    Option.objects.create(
                        name = data[optName],
                        property = prop
                    )
        individuals = Individual.objects.filter(species = data['species'])
        for individual in individuals:
            Property.objects.create(
                parent = prop,
                animal = individual
            )
        return HttpResponseRedirect('../properties/')

class IndividualWizard(SessionWizardView):

    file_storage = FileSystemStorage(location=settings.UPLOAD_ROOT)
    species = None
    animal = None
    modify = False

    def render_next_step(self, form, **kwargs):
        step = self.steps.next
        if step == '0':
            id = self.kwargs.pop('id')
            if id:
                self.animal = get_object_or_404(Individual, pk=id)
                self.modify = True
                self.species = animal.species
            if self.animal.owner != request.user:
                return HttpResponseForbidden()
        return super(IndividualWizard, self).render_next_step()

    def get_template_names(self):
        return "databank/property_form.html"

    def get_form_kwargs(self, step):
        return {'species' : self.species,'modify' : self.modify}

    def process_step(self, form):
        formData = self.get_form_step_data(form)
        if not modify and self.steps.current == '0':
            self.species = formData.get('0-species')
        return formData

    def get_form_instance(self, step):
        if modify and step == 0:
            return self.animal  # do NOT set self.instance, just return the model instance you want
        return self.instance_dict.get(step, None)  # the default implementation

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        if self.animal is None:
            self.animal = animal = Individual.objects.create(
            owner = self.request.user
        )
        self.animal.ENAR = data['ENAR']
        self.animal.Name = data['Name']
        self.animal.species = data['species']
        self.animal.subspecies = data['subspecies']
        self.animal.gender = data['gender'][0]
        self.animal.date = data['date']
        self.animal.location = data['location']
        self.animal.parents.set(data['parents'])
        self.animal.save()
        for img in self.request.FILES.getlist('image'):
            Image.objects.create(
                animal=self.animal,
                image=img
            )
        properties = Property_base.objects._mptt_filter(species = data['species'])
        for property in properties:
            prop = Property.objects.filter(animal = animal, parent = property)
            if prop is None:
                prop = Property.objects.create(
                    animal = animal,
                    parent = property,
                )
            if (property.type == 'F'):
                prop.numVal = data[property.name]
            elif(property.type == 'T'):
                prop.textVal = data[property.name]
            elif(property.type == 'C'):
                prop.textVal = data[property.name].name
            prop.save()
        return HttpResponseRedirect('../individuals/')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your PhenoBank Account'
            message = render_to_string('databank/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'databank/signup.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'databank/account_activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'databank/account_activation_invalid.html')