"""
imports...
"""


class ValidateDataBeforeUpdateMixin(object):
    @staticmethod
    def validate_before_serializer_update(instance, validated_data, not_editable_fields):
        if instance.status != AbstractStatusModel.SUBMITTED:
            raise serializers.ValidationError({
                'detail': _('Can"t UPDATE. Report - {%s} was not submitted.'
                            % instance)
            })

        if week_range(instance.date) != week_range(validated_data.get('date')):
            raise serializers.ValidationError({
                'detail': _('Can"t submit report, transferred date - %s. '
                            'The report should be submitted for the week at which it was created.'
                            % validated_data.get('date'))
            })

        [validated_data.pop(field, None) for field in not_editable_fields]

        return instance, validated_data


class MeetingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingType
        fields = ('id', 'code', 'name',)


class MeetingAttendSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.fullname')
    spiritual_level = ReadOnlyChoiceField(source='user.spiritual_level',
                                          choices=CustomUser.SPIRITUAL_LEVEL_CHOICES,
                                          read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = MeetingAttend
        fields = ('id', 'user_id', 'fullname', 'spiritual_level', 'attended', 'note',
                  'phone_number',)


class MeetingVisitorsSerializer(serializers.ModelSerializer):
    spiritual_level = ReadOnlyChoiceField(
        choices=CustomUser.SPIRITUAL_LEVEL_CHOICES, read_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('user_id', 'fullname', 'spiritual_level', 'phone_number',)


class MeetingSerializer(serializers.ModelSerializer, ValidateDataBeforeUpdateMixin):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())
    date = serializers.DateField(default=datetime.now().date())
    can_submit = serializers.BooleanField(read_only=True)
    cant_submit_cause = serializers.CharField(read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'home_group', 'owner', 'type', 'date', 'total_sum',
                  'status', 'can_submit', 'cant_submit_cause', 'image')

        validators = [
            UniqueTogetherValidator(
                queryset=Meeting.objects.all(),
                fields=('home_group', 'type', 'date',)
            )]

    def create(self, validated_data):
        owner = validated_data.get('owner')
        home_group = validated_data.get('home_group')
        if home_group.leader != owner:
            raise serializers.ValidationError({
                'detail': _('The transferred leader is not the leader of this Home Group')
            })

        meeting = Meeting.objects.create(**validated_data)
        return meeting


class OwnerRelatedField(serializers.RelatedField):
    def get_attribute(self, instance):
        return instance.owner_id, instance.owner_name

    def to_representation(self, value):
        owner_id, owner_name = value
        return {
            'id': owner_id,
            'fullname': owner_name
        }


class MeetingListSerializer(MeetingSerializer):
    visitors_absent = serializers.IntegerField()
    visitors_attended = serializers.IntegerField()
    type = MeetingTypeSerializer()
    home_group = HomeGroupNameSerializer()
    owner = OwnerRelatedField(read_only=True)
    status = serializers.JSONField(source='get_status_display')

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + (
            'phone_number',
            'visitors_attended',
            'visitors_absent',
            'link',)
        read_only_fields = ['__all__']


class MeetingDetailSerializer(MeetingSerializer):
    attends = MeetingAttendSerializer(many=True, required=False, read_only=True)
    home_group = HomeGroupNameSerializer(read_only=True, required=False)
    type = MeetingTypeSerializer(read_only=True, required=False)
    owner = UserNameSerializer(read_only=True, required=False)
    status = serializers.ReadOnlyField(read_only=True, required=False)

    not_editable_fields = ['home_group', 'owner', 'type', 'status']

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + ('attends', 'table_columns',)

    def update(self, instance, validated_data):
        instance, validated_data = self.validate_before_serializer_update(
            instance, validated_data, self.not_editable_fields)

        return super(MeetingDetailSerializer, self).update(instance, validated_data)


class MeetingStatisticSerializer(serializers.ModelSerializer):
    total_visitors = serializers.IntegerField()
    total_visits = serializers.IntegerField()
    total_absent = serializers.IntegerField()
    new_repentance = serializers.IntegerField()
    total_donations = serializers.DecimalField(max_digits=13, decimal_places=2)
    reports_in_progress = serializers.IntegerField()
    reports_submitted = serializers.IntegerField()
    reports_expired = serializers.IntegerField()

    class Meta:
        model = Meeting
        fields = ('total_visitors', 'total_visits', 'total_absent', 'total_donations',
                  'new_repentance', 'reports_in_progress', 'reports_submitted',
                  'reports_expired',)
        read_only_fields = ['__all__']


class MeetingDashboardSerializer(serializers.ModelSerializer):
    meetings_submitted = serializers.IntegerField()
    meetings_in_progress = serializers.IntegerField()
    meetings_expired = serializers.IntegerField()

    class Meta:
        model = Meeting
        fields = ('meetings_submitted', 'meetings_in_progress', 'meetings_expired')
        read_only_fields = ['__all__']


class MeetingSummarySerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='fullname', read_only=True)
    master = UserNameWithLinkSerializer()
    meetings_submitted = serializers.IntegerField(read_only=True)
    meetings_in_progress = serializers.IntegerField(read_only=True)
    meetings_expired = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'owner', 'link', 'master', 'meetings_submitted', 'meetings_in_progress',
                  'meetings_expired')
