"""
imports...
"""


class MeetingFilter(CommonMeetingFilterMixin):
    owner = django_filters.ModelChoiceFilter(name='owner', queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())

    class Meta(CommonMeetingFilterMixin.Meta):
        model = Meeting
        fields = CommonMeetingFilterMixin.Meta.fields + ('home_group', 'owner', 'type')


class MeetingCustomFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        department = request.query_params.get('department')
        church = request.query_params.get('church')

        if department:
            queryset = queryset.filter(home_group__church__department__id=department)
        if church:
            queryset = queryset.filter(home_group__church__id=church)

        return queryset


class MeetingStatusFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_submitted = request.query_params.get('is_submitted')

        if is_submitted == 'true':
            queryset = queryset.filter(status=Meeting.SUBMITTED)
        if is_submitted == 'false':
            queryset = queryset.filter(status__in=[Meeting.IN_PROGRESS, Meeting.EXPIRED])

        return queryset


class CommonGroupsLast5Filter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        last_5 = request.query_params.get('last_5')
        if last_5 == 'true':
            queryset = queryset[:5]

        return queryset
