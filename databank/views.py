from .models import Species, Subspecies, Location, Individual, Option, Property_base, Property
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .forms import SignUpForm
from .tokens import account_activation_token
from django.utils.encoding import force_text
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode

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
        return HttpResponseRedirect('../properties/')

class IndividualWizard(SessionWizardView):

    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photos'))
    species = None

    def get_template_names(self):
        return "databank/property_form.html"

    def get_form_kwargs(self, step):
        if step == '1':
            return {'species' : self.species}
        return {}

    def process_step(self, form):
        formData = self.get_form_step_data(form)
        if self.steps.current == '0':
            self.species = formData.get('0-species')
        return formData

    def done(self, form_list, **kwargs):
        return HttpResponseRedirect('../individuals/')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('databank/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
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
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'databank/account_activation_invalid.html')