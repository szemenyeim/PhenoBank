from django import forms
from .models import Property_base, Individual, Location, Species, Subspecies, upl_file_name

class PropertyMain(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    TYPE_CHOICES = (
        ('N', 'Node'),
        ('T', 'Text'),
        ('F', 'Number'),
        ('C', 'Choice'),
    )
    type = forms.MultipleChoiceField(choices=TYPE_CHOICES, required=True)
    parent = forms.ModelChoiceField(queryset=Property_base.objects._mptt_filter(type='N'), required=True)

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
    ENAR = forms.CharField(max_length=100, required=True)

    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    species = forms.ModelChoiceField(queryset=Species.objects.all(), required=True)
    subspecies = forms.ModelChoiceField(queryset=Subspecies.objects.all(), required=True)

    date = forms.DateField(required=True)

    parents = forms.ModelMultipleChoiceField(queryset=Individual.objects.all(), required=False)
    children = forms.ModelMultipleChoiceField(queryset=Individual.objects.all(), required=False)

    image = forms.ImageField(upload_to=upl_file_name, required=False)
    meas = forms.FileField(upload_to=upl_file_name, required=False)

class IndividualProperties(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
