import django_filters
from django_filters.widgets import RangeWidget
from .models import Individual

class IndividualFilter(django_filters.FilterSet):
    Name = django_filters.CharFilter(lookup_expr='contains', label="Name:")
    ENAR = django_filters.CharFilter(lookup_expr='contains', label="ENAR:")
    location = django_filters.CharFilter(lookup_expr='contains', label="Location:")
    date_range = django_filters.DateFromToRangeFilter(label="Date:",widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))

    o = django_filters.OrderingFilter(
        fields={
            'ENAR': 'ENAR',
            'Name': 'Name',
            'Location': 'location',
            'Sub Species': 'subspecies',
            'Sex': 'sex',
            'Birth Date': 'date',
        },
        field_labels={
            'ENAR': 'ENAR',
            'Name': 'Name',
            'Location': 'Location',
            'Sub Species': 'Sub Species',
            'Sex': 'Sex',
            'Birth Date': 'Birth Date',
        }
    )

    class Meta:
        model = Individual
        fields = ['Name','ENAR','location','subspecies','sex']
