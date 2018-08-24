from django import forms
from .models import Property_base, Individual, Species, Subspecies, Option, Property, Image
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError
import datetime

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
    def render(self, name, value, attrs=None, renderer=None):
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
    description = forms.CharField(max_length=1000,required=False,widget=forms.Textarea)

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

class IndividualMain(forms.ModelForm):
    class Meta:
        model = Individual
        exclude = ('owner','ID')

    species = forms.ModelChoiceField(queryset=Species.objects.all(),required=False,widget=forms.HiddenInput)

    ENAR = forms.CharField(max_length=10, required=True)
    Name = forms.CharField(max_length=100, required=True)

    location = forms.CharField(max_length=100, required=True)
    subspecies = forms.ModelChoiceField(queryset=Subspecies.objects.all(), required=True)

    date = forms.DateField(widget = forms.SelectDateWidget(years=range(1950, datetime.date.today().year)),required=True)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)

    parents = forms.ModelMultipleChoiceField(queryset=Individual.objects.all(), required=False)

    modify = forms.BooleanField(required=False,widget=forms.HiddenInput)

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

class PropertySearchForm(forms.Form):

    prop = forms.ModelChoiceField(queryset=Property_base.objects.all(), widget=forms.HiddenInput, required=False)
    text = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput)
    numFrom = forms.FloatField(required=False, widget=forms.HiddenInput)
    numTo = forms.FloatField(required=False, widget=forms.HiddenInput)
    opt = forms.ModelChoiceField(queryset=Option.objects.all(),required=False, widget=forms.HiddenInput)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = kwargs.get('data',None)
        prefix = ""
        if not data:
            data = kwargs.get('initial',None)
        else:
            prefix = self.prefix + "-"


        if data:
            property = data.get(prefix+'prop',None)
            if not property:
                return
            if prefix != "":
                property = Property_base.objects.get(pk=property)

            self.fields['prop'] = forms.ModelChoiceField(queryset=Property_base.objects.all(), initial=property,
                                                            widget=forms.HiddenInput)

            name = property.name
            type = property.type

            if type == 'T':
                self.fields['text'] = forms.CharField(max_length=100, label=name, required=False, widget=forms.TextInput, initial=data.get(prefix+'text',None))
            elif type == 'F':
                self.fields['numFrom'] = forms.FloatField(max_value=property.maxVal, min_value=property.minVal, label=name + " From:",
                                                     required=False, widget=forms.NumberInput, initial=data.get(prefix+'numFrom',None))
                self.fields['numTo'] = forms.FloatField(max_value=property.maxVal, min_value=property.minVal, label="To:",
                                                     required=False, widget=forms.NumberInput, initial=data.get(prefix+'numTo',None))
            elif type == 'C':
                options = Option.objects.filter(property=property)
                self.fields['opt'] = forms.ModelChoiceField(queryset=options, label=name, required=False, widget=forms.Select, initial=data.get(prefix+'opt',None))

    def clean(self):
        data = self.cleaned_data
        f = data.get('numFrom',None)
        t = data.get('numTo',None)
        if f is not None and t is not None and t < f:
            raise ValidationError("The from value is higher than the t value")
        return data

BaseSearchFormSet = forms.formset_factory(PropertySearchForm, extra=0)

class SearchFormSet(BaseSearchFormSet):
    def __init__(self, *args, **kwargs):
        #  create a user attribute and take it out from kwargs
        # so it doesn't messes up with the other formset kwargs
        super(SearchFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

    def get_form_kwargs(self, index):
        form_kwargs = super(SearchFormSet, self).get_form_kwargs(index)
        return form_kwargs

