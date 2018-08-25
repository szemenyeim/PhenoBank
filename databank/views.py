from .models import Species, Subspecies, Individual, Option, Property_base, Property, Image
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from formtools.wizard.views import SessionWizardView
import os
from .filters import IndividualFilter
from .forms import SearchFormSet
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes,smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .forms import SignUpForm, ImageForm
from .tokens import account_activation_token
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from .fileAgent import constructFile
import json
from django.db.models import Q
from django.core.management import call_command

# Create your views here.

def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_phenomes = Individual.objects.all().count()
    # Available books (status = 'a')
    num_species = Species.objects.count()  # The 'all()' is implied by default.

    species = Species.objects.all()

    currSpec = species.filter(pk=request.session.get('species'))
    currSpec = currSpec.get().name if len(currSpec) else None

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_phenomes': num_phenomes, 'num_species': num_species, 'species':species, 'pk':request.session.get('species'), 'name':currSpec},
    )

def speciesSelector(request,pk):
    request.session['species'] = pk
    return HttpResponseRedirect('/')

from django.views import generic

def getTree(animal, key, level):
    data = []
    if level > 3:
        return None
    leafs = animal.children.all() if key == 'descendants' else animal.parents.all()
    if leafs.count() == 0:
        return None
    for leaf in leafs:
        leafData = {}
        leafData['name'] = leaf.__str__()
        leafData['link'] = leaf.get_absolute_url()
        sub = getTree(leaf,key,level+1)
        if sub:
            leafData[key] = sub
        data.append(leafData)
    return data

def generateFamilyJSON(animal):
    data = {}
    data['name'] = animal.__str__()
    data['link'] = animal.get_absolute_url()
    anc = getTree(animal,'ancestors',0)
    if anc:
        data['ancestors'] = anc
    desc = getTree(animal,'descendants',0)
    if desc:
        data['descendants'] = desc
    if not os.path.exists(settings.MEDIA_ROOT):
        os.mkdir(settings.MEDIA_ROOT)
    with open(settings.MEDIA_ROOT + str(animal.ID) + ".json", "w+") as fp:
        json_data = json.dump(data,fp)

def getAnimalsForProperties(form):
    props = []
    species = None
    for data in form.cleaned_data:
        prop = data['prop']
        if prop:
            species = prop.species
            if prop.type == 'T' and data['text'] != '':
                props.append(Property.objects.filter(parent=prop,textVal__contains=data['text']))
            elif prop.type == 'F':
                qs = Property.objects.filter(parent=prop)
                if data['numFrom'] is not None:
                    qs = qs.filter(numVal__gte=data['numFrom'])
                if data['numTo'] is not None:
                    qs = qs.filter(numVal__lte=data['numTo'])
                props.append(qs)
            elif prop.type == 'C' and data['opt']:
                props.append(Property.objects.filter(parent=prop,textVal=data['opt'].name))

    if(len(props) == 0 or species is None):
        return None

    animals = Individual.objects.filter(species=species)
    for qs in props:
        animals = animals.filter(ID__in=qs.values('animal'))

    return animals

def searchProperty(request,pk):
    property = get_object_or_404(Property_base,pk=pk)
    prop_children = property.get_descendants(include_self=True).filter(~Q(type='N'))
    header = ['ENAR','Name','Location','Subspecies','Gender','Birt Date']
    initial = []
    propVals = []
    formErrors = []
    for prop in prop_children:
        initial.append({'prop':prop})
        header.append(prop.name)

    if request.method == 'GET':
        form = SearchFormSet(initial=initial)
        animals = Individual.objects.filter(species=property.species)
        formErrors = [None]*len(form.forms)
        #return render(request, 'databank/search.html', {'formset':form,'animals':animals,'formsanderrors':zip(form.forms,[None]*len(form.forms))})
    else:
        form = SearchFormSet(request.POST)
        formErrors = form.errors
        animals = None
        if form.is_valid():
            animals = getAnimalsForProperties(form)

    for animal in animals:
        propVals.append(Property.objects.filter(animal=animal, parent__in=prop_children).order_by('parent__parent__name','parent__parent','parent__name'))

    return render(request, 'databank/search.html', {'formset':form,'animals':list(zip(animals,propVals)), 'header':header, 'formsanderrors':zip(form.forms,formErrors)})

def individual_list(request):
    f = IndividualFilter(request.GET, queryset=Individual.objects.filter(species=request.session.get('species')))
    return render(request, 'databank/individual_filter.html', {'filter': f})

class IndividualDetailView(generic.DetailView):
    model = Individual


    def get_context_data(self, **kwargs):
        form = ImageForm()
        extra_context = {'form': form}
        context = super(IndividualDetailView, self).get_context_data(**kwargs)
        context.update(extra_context)
        animal = context['individual']
        generateFamilyJSON(animal)
        return context

class PropertyListView(generic.ListView):
    model = Property_base
    paginate_by = 100

    def get_queryset(self):
        return Property_base.objects.filter(species=self.request.session.get('species'))

class PropertyDetailView(generic.DetailView):
    model = Property_base
    def get_context_data(self, *args, **kwargs):
        context = super(PropertyDetailView, self).get_context_data(*args, **kwargs)
        context['property_base_list'] = Property_base.objects.filter(species=self.request.session.get('species'))
        return context

def isNumber(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    # check if the property is a number
    return cleaned_data.get('type', True) == 'F'

def isMulti(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    # check if the property is multiple choice
    return cleaned_data.get('type', True) == 'C'

class PropertyWizard(SessionWizardView):

    def get_form_kwargs(self, step):
        if step == '0':
            return {'species' : self.request.session.get('species')}
        return {}

    def get_template_names(self):
        return "databank/property_form.html"


    def render(self, form=None, **kwargs):
        if self.request.session.get('species'):
            return super(PropertyWizard, self).render(form, **kwargs)
        else:
            return HttpResponseRedirect('/')

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        prop = Property_base.objects.create(
            name = data['name'],
            species = data['species'],
            parent = data['parent'],
            type = data['type'],
            description=data['description'],
            owner = self.request.user,
        )
        if( data['type'] == 'F' ):
            prop.minVal = data['minVal']
            prop.maxVal = data['maxVal']
            prop.save()
        elif(data['type'] == 'C'):
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
        return HttpResponseRedirect('../../properties/')

class IndividualWizard(SessionWizardView):

    file_storage = FileSystemStorage(location=settings.UPLOAD_ROOT)

    def __init__(self, **kwargs):
        super(IndividualWizard, self).__init__(**kwargs)

    def isModify(self):
        return self.kwargs.get('pk',None) is not None

    def getAnimal(self):
        query = Individual.objects.filter(ID=self.kwargs.get('pk', None))
        if query.exists():
            return query.get()
        return None

    def render(self, form=None, **kwargs):
        if self.isModify() and self.getAnimal().owner != self.request.user:
            return HttpResponseForbidden()
        if self.request.session.get('species'):
            return super(IndividualWizard, self).render(form, **kwargs)
        else:
            return HttpResponseRedirect('/')

    def get_template_names(self):
        return "databank/property_form.html"

    def get_form_kwargs(self, step):
        return {'species' : self.getSpecies(),'modify' : self.isModify()}

    def getSpecies(self):
        return self.request.session.get('species')

    def get_form_instance(self, step):
        if self.isModify() and step == '0':
            return self.getAnimal()  # do NOT set self.instance, just return the model instance you want
        if step == '1':
            if self.isModify():
                return Property.objects.filter(animal=self.getAnimal()).order_by('parent')
            else:
                return Property.objects.none()
        return self.instance_dict.get(step, None)  # the default implementation

    def get_form_initial(self, step):
        if step == '1' and not self.isModify():
            props = Property_base.objects._mptt_filter(species=self.getSpecies())
            animal = self.getAnimal()
            initial = []
            for prop in props:
                initial.append({'parent':prop, 'animal':animal})
            return initial
        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        animal = self.getAnimal()
        for i, form in enumerate(form_list):
            if form.is_valid():
                if self.isModify():
                    form.save()
                else:
                    if i == 0:
                        print(form)
                        animal = form.save(commit=False)
                        animal.owner = self.request.user
                        animal.save()
                        form.save_m2m()
                    elif i == 1:
                        props = form.save(commit=False)
                        for prop in props:
                            prop.animal=animal
                            prop.save()
        prefix = "../../../" if self.isModify() else "../../"
        return HttpResponseRedirect(prefix + "individuals")

def model_form_upload(request, pk=None):
    if request.method == 'POST':
        animal = None
        query = Individual.objects.filter(ID=pk)
        if query.exists():
            animal = query.get()
        if animal is None or animal.owner != request.user:
            return HttpResponseForbidden()

        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.animal = animal
            image.save()
            return redirect(animal.get_absolute_url())

    return HttpResponseNotFound()

def animal_download(request, pk=None):
    if request.method == 'GET':
        animal = None
        query = Individual.objects.filter(ID=pk)
        if query.exists():
            animal = query.get()
        if animal is None:
            return HttpResponseNotFound()

        fileName = animal.ENAR + ".xls"
        filePath = os.path.join(settings.MEDIA_ROOT,fileName)
        fileURL = os.path.join(settings.MEDIA_URL,fileName)
        constructFile(filePath,animal)
        with open(filePath, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filePath)

        return response

    return HttpResponseForbidden()

def property_delete(request, pk=None):
    if request.method == 'GET':
        property = None
        query = Property_base.objects.filter(ID=pk)
        if query.exists():
            property = query.get()
        if property is None:
            return HttpResponseNotFound()
        if property.owner != request.user:
            return HttpResponseForbidden()

        parent = property.parent
        property.delete()

        return redirect(parent.get_absolute_url())

    return HttpResponseForbidden()

def delete_image(request, pk):
    if request.method == 'GET':
        image = None
        animal = None
        query = Image.objects.filter(pk=pk)
        if query.exists():
            image = query.get()
            animal = image.animal
        if image is None or animal is None or animal.owner != request.user:
            return HttpResponseForbidden()

        image.delete()
        return redirect(animal.get_absolute_url())
    return HttpResponseNotFound()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False

            user.is_active = True
            user.save()
            user.profile.email_confirmed = True
            user.save()
            login(request, user)
            return redirect('index')
            '''user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your PhenoBank Account'
            message = render_to_string('databank/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')'''
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