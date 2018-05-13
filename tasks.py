"""
imports...
"""


@app.task(name='processing_home_meetings', ignore_result=True,
          max_retries=10, default_retry_delay=1000)
def processing_home_meetings():
    current_date = datetime.now().date()
    active_home_groups = HomeGroup.objects.filter(active=True)
    meeting_types = MeetingType.objects.all()

    try:
        with transaction.atomic():
            expired_reports = Meeting.objects.filter(status=Meeting.IN_PROGRESS)
            expired_reports.update(status=Meeting.EXPIRED)

            for home_group in active_home_groups:
                for meeting_type in meeting_types:
                    Meeting.objects.get_or_create(home_group=home_group,
                                                  owner=home_group.leader,
                                                  date=current_date,
                                                  type=meeting_type)
    except IntegrityError as e:
        print(e)
