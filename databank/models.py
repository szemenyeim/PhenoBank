from django.db import models
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
import uuid
from mptt.models import MPTTModel, TreeForeignKey

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

def upl_file_name(instance, filename):
    return '/'.join(['upload', str(instance.animal.ENAR), filename])

def upl_file_name_spec(instance, filename):
    return '/'.join(['upload', str(instance.name), filename])

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# Create your models here.

class Species(models.Model):
    """
    Model representing a species.
    """
    name = models.CharField(max_length=200, help_text="Enter the species name")
    image = models.ImageField('Image',upload_to=upl_file_name_spec, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name

class Subspecies(models.Model):
    """
    Model representing a subspecies.
    """
    name = models.CharField(max_length=200, help_text="Enter the subspecies name")
    species = models.ForeignKey(Species, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.species.name + "/" + self.name

class Property_base(MPTTModel):
    """
    Model representing a option.
    """
    name = models.CharField(max_length=200, help_text="Enter the property name")
    ID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular base property across whole bank")
    TYPE_CHOICES = (
        ('N', 'Node'),
        ('T', 'Text'),
        ('F', 'Number'),
        ('C', 'Choice'),
    )
    type = models.CharField(max_length=1,choices=TYPE_CHOICES)
    maxVal = models.FloatField(help_text="Enter the maximal value of the numerical option",null=True, blank=True)
    minVal = models.FloatField(help_text="Enter the minimal value of the numerical option",null=True, blank=True)
    species = models.ForeignKey('Species', on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length = 1000, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class MPTTMeta:
        order_insertion_by = ["name", "type", "species", "parent"]

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name if self.parent else "Properties"


    def get_absolute_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('property-detail', args=[str(self.ID)])

    def get_search_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('search', args=[str(self.ID)])

    def get_delete_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('property-delete', args=[str(self.ID)])

    def get_type_str(self):
        TYPE_NAMES = {'N':"Node",'C':"Multiple Choice", 'F':"Number",'T':"Text"}
        return TYPE_NAMES[self.type]

class Option(models.Model):
    """
    Model representing a option.
    """
    name = models.CharField(max_length=200, help_text="Enter the option name")
    ID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular option across whole bank")
    property = models.ForeignKey('Property_base', on_delete=models.CASCADE, null=True, related_name='options')

    class Meta:
        ordering = ["name"]

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name

class Individual(models.Model):
    """
    Model representing a individual.
    """
    ENAR = models.CharField('ENAR ID', max_length=50, help_text='ENAR ID')
    Name = models.CharField('Name', max_length=100, help_text='Name')

    location = models.CharField('location', max_length=100, null=True, help_text="Birth Location")
    date = models.DateField( help_text='Birth Date', null=True)
    species = models.ForeignKey('Species', on_delete=models.SET_NULL, null=True)
    subspecies = models.ForeignKey('Subspecies', on_delete=models.SET_NULL, null=True)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)

    parents = models.ManyToManyField('self', blank=True, related_name='children', symmetrical=False)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text="Assigned User")

    ID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular Individual across whole bank")

    class Meta:
        ordering = ["ID","ENAR", "date", "subspecies", "location"]

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.Name + " (" + self.ENAR + ")"

    def get_absolute_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('individual-detail', args=[str(self.ID)])

    def get_addimage_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('individual-image-add', args=[str(self.ID)])

    def get_edit_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('individual-edit', args=[str(self.ID)])

    def get_download_url_xls(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('individual-download', args=[str(self.ID), 'xls'])

    def get_download_url_xml(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('individual-download', args=[str(self.ID), 'xml'])


class Image(models.Model):

    UNID = models.UUIDField(primary_key=True, default=uuid.uuid1,
                          help_text="Unique ID for this particular image across whole bank")
    animal = models.ForeignKey('Individual', on_delete=models.CASCADE, null=True, related_name='images')
    image = models.ImageField('Image',upload_to=upl_file_name)

    def get_delete_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('delete_image', args=[str(self.UNID)])

class Property(models.Model):
    """
    Model representing a option.
    """

    ID = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular property across whole bank")
    numVal = models.FloatField(help_text="Enter the value of the numerical option", null=True)
    textVal = models.CharField(max_length=200, help_text="Enter the minimal value of the text option", null=True)
    parent = models.ForeignKey('Property_base', on_delete=models.CASCADE, null=True)
    animal = models.ForeignKey('Individual', on_delete=models.CASCADE, null=True, related_name='properties')

    class Meta:
        ordering = ["parent__parent","parent__name"]


    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return ((self.animal.ENAR + "/") if self.animal else "") + self.parent.name