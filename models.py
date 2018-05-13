"""
imports...
"""


@python_2_unicode_compatible
class AbstractStatusModel(models.Model):
    IN_PROGRESS, SUBMITTED, EXPIRED = 1, 2, 3

    STATUS_LIST = (
        (IN_PROGRESS, _('in_progress')),
        (SUBMITTED, _('submitted')),
        (EXPIRED, _('expired')),
    )
    status = models.PositiveSmallIntegerField(_('Status'), choices=STATUS_LIST, default=IN_PROGRESS)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Meeting(AbstractStatusModel):
    date = models.DateField(_('Date'))
    type = models.ForeignKey(MeetingType, on_delete=models.PROTECT, verbose_name=_('Meeting type'))

    owner = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT,
                              limit_choices_to={'hierarchy__level__gte': 1})

    home_group = models.ForeignKey('group.HomeGroup', on_delete=models.CASCADE,
                                   verbose_name=_('Home Group'))

    visitors = models.ManyToManyField('account.CustomUser', verbose_name=_('Visitors'),
                                      through='event.MeetingAttend',
                                      related_name='meeting_types')

    total_sum = models.DecimalField(_('Total sum'), max_digits=12,
                                    decimal_places=2, default=0)

    image = models.ImageField(_('Event Image'), upload_to=get_event_week(), blank=True, null=True)

    objects = MeetingManager()

    class Meta:
        ordering = ('-id', '-date')
        verbose_name = _('Meeting')
        verbose_name_plural = _('Meetings')
        unique_together = ['type', 'date', 'home_group']

    def __str__(self):
        return 'Отчет ДГ - {} ({}): {}'.format(
            self.home_group,
            self.type.name,
            self.date.strftime('%d %B %Y'))

    def get_absolute_url(self):
        return reverse('events:meeting_report_detail', args=(self.id,))

    @property
    def phone_number(self):
        return self.home_group.phone_number

    @property
    def church(self):
        return self.home_group.church

    @property
    def department(self):
        return self.home_group.church.department

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def table_columns(self):
        return meeting_table(self.owner, category_title='attends')

    @cached_property
    def can_submit(self):
        if Meeting.objects.filter(owner=self.owner, status=Meeting.EXPIRED).exists() \
                and self.status == Meeting.IN_PROGRESS:
            return False
        return True

    @property
    def cant_submit_cause(self):
        if not self.can_submit:
            return _('Can"t submit report. Expired meetings is exists')
        return ''
