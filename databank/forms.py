from django import forms
from .models import Property_base, Individual, Location, Species, Subspecies, Option, Property, Image
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError

class ImageForm(forms.ModelForm):
    animal = forms.ModelChoiceField(queryset=Individual.objects.all(), disabled=True, widget=forms.HiddenInput, required=False)
    class Meta:
        model = Image
        fields = ('image', 'animal' )

class PropertyForm(forms.ModelForm):

    class Meta:
        model = Property
        fields = ('numVal', 'textVal', 'parent', 'animal' )

    def __init__(self, *args, **kwargs):
        super(PropertyForm,self).__init__(*args, **kwargs)
        if self.instance is not None:
            property = self.instance.parent
            if not property:
                property = self.initial['parent']
            if property:
                _type = property.type
                name = property.name
                self.fields['parent'] = forms.ModelChoiceField(queryset=Property_base.objects.all(), disabled=False, widget=forms.HiddenInput, required=False)
                self.fields['animal'] = forms.ModelChoiceField(queryset=Individual.objects.all(), disabled=True, widget=forms.HiddenInput, required=False)
                if _type == 'N':
                    self.fields['textVal'] = forms.CharField(max_length=0, widget=NameOnlyWidget, required=False, label=name)
                    self.fields['numVal'] = forms.FloatField(widget=forms.HiddenInput, required=False)
                elif _type == 'T':
                    self.fields['textVal'] = forms.CharField(max_length=100, required=True, label=name)
                    self.fields['numVal'] = forms.FloatField(widget=forms.HiddenInput, required=False)
                elif _type == 'F':
                    self.fields['textVal'] = forms.CharField(max_length=0,widget=forms.HiddenInput, required=False)
                    self.fields['numVal'] = forms.FloatField(max_value=property.maxVal, min_value=property.minVal, required=True, label=name)
                elif _type == 'C':
                    options = Option.objects.filter(property=property)
                    choices = []
                    for opt in options:
                        choices.append([opt.name, opt.name])
                    choices = tuple(choices)
                    self.fields['textVal'] = forms.ChoiceField(choices=choices, required=True, label=name)
                    self.fields['numVal'] = forms.FloatField(disabled=True, widget=forms.HiddenInput, required=False)

    def clean(self):
        data=super(PropertyForm, self).clean()
        property = self.instance.parent
        if not property:
            property = self.initial['parent']
        type = property.type
        if type == 'F':
            if data.get('numVal',None):
                if property.maxVal is not None and data['numVal'] > property.maxVal:
                    raise ValidationError("The maximum value of this property is %f" % property.maxVal)
                if property.minVal is not None and data['numVal'] < property.minVal:
                    raise ValidationError("The minimum value of this property is %f" % property.minVal)
        return data

BasePropertyFormSet = forms.modelformset_factory(Property,form=PropertyForm, extra=0)

class PropertyFormSet(BasePropertyFormSet):
    def __init__(self, *args, **kwargs):
        #  create a user attribute and take it out from kwargs
        # so it doesn't messes up with the other formset kwargs
        self.species = kwargs.pop('species')
        self.modify = kwargs.pop('modify')
        initial = kwargs.get('initial',None)
        self.extra = len(initial) if initial else 0
        super(PropertyFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

    def _construct_form(self, *args, **kwargs):
        # inject user in each form on the formset
        return super(PropertyFormSet, self)._construct_form(*args, **kwargs)

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    captcha = CaptchaField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class NameOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        #super().render(name, value, attrs)
        flat_attrs = flatatt(attrs)
        html = '''
            <label %(attrs)s value="%(value)s"/>
            
        ''' % {
            'attrs': flat_attrs,
            'value': value,
        }
        return mark_safe(html)

class PropertyMain(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    TYPE_CHOICES = (
        ('N', 'Node'),
        ('T', 'Text'),
        ('F', 'Number'),
        ('C', 'Choice'),
    )
    type = forms.ChoiceField(choices=TYPE_CHOICES, required=True)
    parent = forms.ModelChoiceField(Property_base.objects._mptt_filter(type='N'),required=True)
    species = forms.ModelChoiceField(Species.objects.all(),required=False,widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        super(PropertyMain, self).__init__(*args, **kwargs)
        if species:
            self.fields['parent'] = forms.ModelChoiceField(Property_base.objects._mptt_filter(species=species, type='N'),required=True)
            self.fields['species'] = forms.ModelChoiceField(Species.objects.all(),required=False,widget=forms.HiddenInput,initial=species)

    def clean(self):
        data = self.cleaned_data
        name = data['name']
        species = data['species']
        if Property_base.objects._mptt_filter(name=name,species=species).exists():
            raise ValidationError("Property with this name already exists for this species")
        return data

class PropertyNumeric(forms.Form):
    maxVal = forms.FloatField(required=False)
    minVal = forms.FloatField(required=False)
    def clean(self):
        form_data = self.cleaned_data
        maxVal = form_data['maxVal']
        minVal = form_data['minVal']
        if minVal and maxVal and minVal >= maxVal:
            self._errors["password"] = ["Password do not match"]
        return form_data

class PropertyChoice(forms.Form):
    opt1 = forms.CharField(max_length=100, required=True)
    opt2 = forms.CharField(max_length=100, required=True)
    opt3 = forms.CharField(max_length=100, required=False)
    opt4 = forms.CharField(max_length=100, required=False)
    opt5 = forms.CharField(max_length=100, required=False)
    opt6 = forms.CharField(max_length=100, required=False)
    opt7 = forms.CharField(max_length=100, required=False)
    opt8 = forms.CharField(max_length=100, required=False)
    opt9 = forms.CharField(max_length=100, required=False)
    opt10 = forms.CharField(max_length=100, required=False)

class SpeciesSelector(forms.Form):
    species = forms.ModelChoiceField(queryset=Species.objects.all(),required=True)

class IndividualMain(forms.ModelForm):
    class Meta:
        model = Individual
        exclude = ('owner','ID')

    species = forms.ModelChoiceField(queryset=Species.objects.all(),required=False,widget=forms.HiddenInput)

    ENAR = forms.CharField(max_length=10, required=True)
    Name = forms.CharField(max_length=100, required=True)

    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    subspecies = forms.ModelChoiceField(queryset=Subspecies.objects.all(), required=True)

    date = forms.DateField(widget = forms.SelectDateWidget(),required=True)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)

    parents = forms.ModelMultipleChoiceField(queryset=Individual.objects.all(), required=False)

    modify = forms.BooleanField(required=False,widget=forms.HiddenInput)

    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': False}),required=False)

    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        modify = kwargs.pop('modify')
        super(IndividualMain, self).__init__(*args, **kwargs)
        if species:
            self.fields['species'] = forms.ModelChoiceField(queryset=Species.objects.all(),required=False, widget=forms.HiddenInput, initial=species)
            self.fields['subspecies'] = forms.ModelChoiceField(queryset=Subspecies.objects.filter(species=species), required=True)
            self.fields['parents'] = forms.ModelMultipleChoiceField(queryset=Individual.objects.filter(species=species), required=False)
            self.fields['modify'] = forms.BooleanField(required=False,widget=forms.HiddenInput, initial=modify)

    def clean(self):
        data = self.cleaned_data
        ENAR = data['ENAR']
        species = data['species']
        modify = data['modify']
        if not modify and Individual.objects.filter(ENAR=ENAR, species=species).exists():
            raise ValidationError("Individual with this ENAR already exists for this species")
        return data

    def clean_parents(self):
        parents = self.cleaned_data['parents']
        if parents.count() > 2:
            raise ValidationError("You can select 2 parents at most")
        if parents.count() == 2 and parents.first().gender == parents.last().gender:
            raise ValidationError("Parents must be a different gender")
        return parents

class IndividualProperties(forms.Form):

    data = None
    formIdxStr = ""

    def getInitial(self,name):
        return self.data[self.formIdxStr+name] if self.data else None


    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        modify = kwargs.pop('modify')
        print(kwargs)
        self.formIdxStr = "2-"
        super().__init__(*args, **kwargs)
        if not species:
            self.data = kwargs.pop('data')
            species = self.data[self.formIdxStr+'species']

        self.fields['species'] = forms.ModelChoiceField(queryset=Species.objects.all(), initial=species,
                                                        widget=forms.HiddenInput)
        properties = Property_base.objects._mptt_filter(species=species)
        for property in properties:
            name = property.name
            type = property.type
            if type == 'N':
                self.fields[name] = forms.CharField(max_length=0, disabled=True, show_hidden_initial=True,
                                                    widget=NameOnlyWidget, required=False)
            elif type == 'T':
                self.fields[name] = forms.CharField(max_length=100, required=True, initial=self.getInitial(name))
            elif type == 'F':
                self.fields[name] = forms.FloatField(max_value=property.maxVal, min_value=property.minVal,
                                                     required=True, initial=self.getInitial(name))
            elif type == 'C':
                options = Option.objects.filter(property=property)
                self.fields[name] = forms.ModelChoiceField(queryset=options, required=True, initial=self.getInitial(name))


