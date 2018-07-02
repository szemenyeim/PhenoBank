from django import forms
from .models import Property_base, Individual, Location, Species, Subspecies, Option
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    captcha = CaptchaField()

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
    type = forms.MultipleChoiceField(choices=TYPE_CHOICES, required=True)
    species = forms.ModelChoiceField(queryset=Species.objects.all(),required=True)

class PropertyParents(forms.Form):
    parent = forms.ModelChoiceField(Property_base.objects._mptt_filter(type='N'),required=True)
    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        super(PropertyParents, self).__init__(*args, **kwargs)
        if species:
            self.fields['parent'] = forms.ModelChoiceField(Property_base.objects._mptt_filter(species=species, type='N'),required=True)

class PropertyNumeric(forms.Form):
    maxVal = forms.FloatField(required=False)
    minVal = forms.FloatField(required=False)

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


class IndividualMain(forms.Form):

    ENAR = forms.CharField(max_length=10, required=True)
    Name = forms.CharField(max_length=100, required=True)

    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    species = forms.ModelChoiceField(queryset=Species.objects.all(), required=True)
    subspecies = forms.ModelChoiceField(queryset=Subspecies.objects.all(), required=True)

    date = forms.DateField(widget = forms.SelectDateWidget(),required=True)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = forms.MultipleChoiceField(choices=GENDER_CHOICES, required=True)

    parents = forms.ModelMultipleChoiceField(queryset=Individual.objects.all(), required=False)
    children = forms.ModelMultipleChoiceField(queryset=Individual.objects.all(), required=False)

    image = forms.ImageField(required=False)
    meas = forms.FileField(required=False)

class IndividualProperties(forms.Form):
    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        super().__init__(*args, **kwargs)
        if species:
            self.fields['species'] = forms.ModelChoiceField(queryset=Species.objects.all(), initial=species, widget=forms.HiddenInput)
            properties = Property_base.objects._mptt_filter(species=species)
            for property in properties:
                name = property.name
                type = property.type
                if type == 'N':
                    self.fields[name] = forms.CharField(max_length=0, disabled=True, show_hidden_initial=True,
                                                        widget=NameOnlyWidget)
                elif type == 'T':
                    self.fields[name] = forms.CharField(max_length=100, required=False)
                elif type == 'F':
                    self.fields[name] = forms.FloatField(max_value=property.maxVal, min_value=property.minVal,
                                                         required=True)
                elif type == 'C':
                    options = Option.objects.filter(property=property)
                    self.fields[name] = forms.ModelChoiceField(queryset=options, required=True)
        else:
            data = kwargs.pop('data')
            species = data['1-species']
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
                    self.fields[name] = forms.CharField(max_length=100, required=False, initial=data["1-"+name])
                elif type == 'F':
                    self.fields[name] = forms.FloatField(max_value=property.maxVal, min_value=property.minVal,
                                                         required=True, initial=data["1-"+name])
                elif type == 'C':
                    options = Option.objects.filter(property=property)
                    self.fields[name] = forms.ModelChoiceField(queryset=options, required=True, initial=data["1-"+name])


