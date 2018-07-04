import django_filters
from django_filters.widgets import RangeWidget
from .models import Individual

class IndividualFilter(django_filters.FilterSet):
    Name = django_filters.CharFilter(lookup_expr='contains', label="Name:")
    ENAR = django_filters.CharFilter(lookup_expr='contains', label="ENAR:")
    date_range = django_filters.DateFromToRangeFilter(label="Date:",widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))

    o = django_filters.OrderingFilter(
        fields={
            'ENAR': 'ENAR',
            'Name': 'Name',
            'Location': 'location',
            'Species': 'species',
            'Sub Species': 'subspecies',
            'Gender': 'gender',
            'Birth Date': 'date',
        },
        field_labels={
            'ENAR': 'ENAR',
            'Name': 'Name',
            'Location': 'Location',
            'Species': 'Species',
            'Sub Species': 'Sub Species',
            'Gender': 'Gender',
            'Birth Date': 'Birth Date',
        }
    )

    class Meta:
        model = Individual
        fields = ['Name','ENAR','location','species','subspecies','gender']