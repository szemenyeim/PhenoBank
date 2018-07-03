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
    type = forms.MultipleChoiceField(choices=TYPE_CHOICES, required=True)
    parent = forms.ModelChoiceField(Property_base.objects._mptt_filter(type='N'),required=True)

    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        super(PropertyMain, self).__init__(*args, **kwargs)
        if species:
            self.fields['parent'] = forms.ModelChoiceField(Property_base.objects._mptt_filter(species=species, type='N'),required=True)

    def clean_name(self):
        name = self.cleaned_data['name']
        species = self.cleaned_data['species']
        if Property_base.objects._mptt_filter(name=name,species=species).exists():
            raise ValidationError("Property with this name already exists for this species")
        return email

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
        exclude = ('owner','id','species')

    ENAR = forms.CharField(max_length=10, required=True)
    Name = forms.CharField(max_length=100, required=True)

    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    subspecies = forms.ModelChoiceField(queryset=Subspecies.objects.all(), required=True)

    date = forms.DateField(widget = forms.SelectDateWidget(),required=True)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = forms.MultipleChoiceField(choices=GENDER_CHOICES, required=True)

    parents = forms.ModelMultipleChoiceField(queryset=Individual.objects.all(), required=False)

    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}),required=False)

    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        super(IndividualMain, self).__init__(*args, **kwargs)
        if species:
            subspecies = forms.ModelChoiceField(queryset=Subspecies.objects.filter(species=species), required=True)
            parents = forms.ModelMultipleChoiceField(queryset=Individual.objects.filter(species=species), required=False)

    def clean_ENAR(self):
        ENAR = self.cleaned_data['ENAR']
        species = self.cleaned_data['species']
        if Individual.objects._mptt_filter(ENAR=ENAR, species=species).exists():
            raise ValidationError("Individual with this ENAR already exists for this species")
        return ENAR

    def clean_parents(self):
        parents = self.cleaned_data['parents']
        if parents.count() > 2:
            raise ValidationError("You can select 2 parents at most")
        if parents.count() == 2 and parents[0].gender == parents[1].gender():
            raise ValidationError("Parents must be a different gender")
        return ENAR

class IndividualProperties(forms.Form):

    data = Null
    formIdxStr = ""

    def getInitial(self,name):
        return data[self.formIdxStr+name] if data else Null


    def __init__(self, *args, **kwargs):
        species = kwargs.pop('species')
        modify = kwargs.pop('modify')
        self.formIdxStr = "1-" if modify else "2-"
        super().__init__(*args, **kwargs)
        if not species:
            self.data = kwargs.pop('data')
            species = data[formIdxStr+'species']

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
                self.fields[name] = forms.CharField(max_length=100, required=True, initial=getInitial(name))
            elif type == 'F':
                self.fields[name] = forms.FloatField(max_value=property.maxVal, min_value=property.minVal,
                                                     required=True, initial=getInitial(name))
            elif type == 'C':
                options = Option.objects.filter(property=property)
                self.fields[name] = forms.ModelChoiceField(queryset=options, required=True, initial=getInitial(name))


