"""
imports...
"""


class MeetingQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated:
            return self.none()
        if extra_perms and user.is_staff:
            return self.base_queryset()
        return self.filter(owner__in=user.__class__.get_tree(user))

    def annotate_owner_name(self):
        return self.annotate(
            owner_name=Concat(
                'owner__last_name', V(' '),
                'owner__first_name', V(' '),
                'owner__middle_name'))


class MeetingManager(models.Manager):
    def get_queryset(self):
        return MeetingQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)

    def annotate_owner_name(self):
        return self.get_queryset().annotate_owner_name()