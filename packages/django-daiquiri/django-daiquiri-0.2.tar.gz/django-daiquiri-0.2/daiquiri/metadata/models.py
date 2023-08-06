from django.db import models
from django.contrib.auth.models import Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.constants import LICENSE_CHOICES, LICENSE_URLS, ACCESS_LEVEL_CHOICES
from daiquiri.core.managers import AccessLevelManager


@python_2_unicode_compatible
class Schema(models.Model):

    objects = AccessLevelManager()

    order = models.IntegerField(
        default=0, null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Name of the schema on the database server.')
    )
    title = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Title'),
        help_text=_('Human readable title of the schema.')
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the schema to be displayed in the user interface.')
    )
    long_description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Long description'),
        help_text=_('A more extensive description of the schema to be displayed on the public schema page.')
    )
    attribution = models.TextField(
        null=True, blank=True,
        verbose_name=_('Attribution'),
        help_text=_('The desired attribution for the schema.')
    )
    license = models.CharField(
        max_length=8, choices=LICENSE_CHOICES, null=True, blank=True,
        verbose_name=_('License')
    )
    doi = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Digital object identifier')
    )
    utype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA Utype'),
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the schema.')
    )

    class Meta:
        ordering = ('order', )

        verbose_name = _('Schema')
        verbose_name_plural = _('Schemas')

        permissions = (('view_schema', 'Can view Schema'),)

    def __str__(self):
        return self.name

    @property
    def query_strings(self):
        return [self.name]

    @property
    def license_label(self):
        return dict(LICENSE_CHOICES)[self.license]

    @property
    def license_url(self):
        return LICENSE_URLS[self.license]


@python_2_unicode_compatible
class Table(models.Model):

    TYPE_TABLE = 'table'
    TYPE_VIEW = 'view'
    TYPE_CHOICES = (
        (TYPE_TABLE, _('Table')),
        (TYPE_VIEW, _('View'))
    )

    objects = AccessLevelManager()

    schema = models.ForeignKey(
        Schema, related_name='tables',
        verbose_name=_('Database'),
        help_text=_('Database the table belongs to.')
    )
    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the table on the database server.')
    )
    title = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Title'),
        help_text=_('Human readable title of the table.')
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the table to be displayed in the user interface.')
    )
    long_description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Long description'),
        help_text=_('A more extensive description of the table to be displayed on the public database page.')
    )
    attribution = models.TextField(
        null=True, blank=True,
        verbose_name=_('Attribution'),
        help_text=_('The desired attribution for the table.')
    )
    license = models.CharField(
        max_length=8, choices=LICENSE_CHOICES, null=True, blank=True,
        verbose_name=_('License')
    )
    doi = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Digital object identifier')
    )
    type = models.CharField(
        max_length=8, choices=TYPE_CHOICES,
        verbose_name=_('Type of table')
    )
    nrows = models.BigIntegerField(
        null=True, blank=True,
        verbose_name=_('Number of rows in the table')
    )
    size = models.BigIntegerField(
        null=True, blank=True,
        verbose_name=_('Size of the table in bytes')
    )
    utype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA Utype')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the table.')
    )

    class Meta:
        ordering = ('schema__order', 'order', )

        verbose_name = _('Table')
        verbose_name_plural = _('Tables')

        permissions = (('view_table', 'Can view Table'),)

    def __str__(self):
        return self.schema.name + '.' + self.name

    @property
    def query_strings(self):
        return [self.schema.name, self.name]

    @property
    def license_label(self):
        return dict(LICENSE_CHOICES)[self.license]

    @property
    def license_url(self):
        return LICENSE_URLS[self.license]


@python_2_unicode_compatible
class Column(models.Model):

    objects = AccessLevelManager()

    table = models.ForeignKey(
        Table, related_name='columns',
        help_text=_('Table the column belongs to.')
    )
    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the column on the database server.')
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the column to be displayed in the user interface.')
    )
    unit = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Unit')
    )
    ucd = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA UCDs')
    )
    utype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA Utype')
    )
    datatype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Datatype'),
        help_text=_('The datatype of the column on the database server.')
    )
    arraysize = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Arraysize'),
        help_text=_('The length of variable length datatypes, e.g. varchar(256).')
    )
    principal = models.BooleanField(
        default=False,
        verbose_name=_('Principal'),
        help_text=_('Designates whether the column is considered a core part of the content.')
    )
    indexed = models.BooleanField(
        default=False,
        verbose_name=_('Indexed'),
        help_text=_('Designates whether the column is indexed.')
    )
    std = models.BooleanField(
        default=False,
        verbose_name=_('Standard'),
        help_text=_('Designates whether the column is defined by some standard.')
    )
    index_for = models.CharField(
        max_length=256, blank=True, default='',
        verbose_name=_('Index for'),
        help_text=_('The columns which this column is an index for (e.g. for pgSphere).')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the column.')
    )

    class Meta:
        ordering = ('table__schema__order', 'table__order', 'order', )

        verbose_name = _('Column')
        verbose_name_plural = _('Columns')

        permissions = (('view_column', 'Can view Column'),)

    def __str__(self):
        return self.table.schema.name + '.' + self.table.name + '.' + self.name

    @property
    def query_strings(self):
        return [self.name]

    @property
    def indexed_columns(self):
        if self.index_for:
            return [(self.table.schema.name, self.table.name, name.strip()) for name in self.index_for.split(',')] + [self.name]
        else:
            return None


@python_2_unicode_compatible
class Function(models.Model):

    objects = AccessLevelManager()

    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the function on the server.')
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the function to be displayed in the user interface.')
    )
    query_string = models.CharField(
        max_length=256,
        verbose_name=_('Query string'),
        help_text=_('Prototype of this function in a SQL query.')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to this function.')
    )

    class Meta:
        ordering = ('order', )

        verbose_name = _('Function')
        verbose_name_plural = _('Functions')

        permissions = (('view_function', 'Can view Function'),)

    def __str__(self):
        return self.name
