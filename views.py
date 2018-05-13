"""
imports...
"""


@login_required(login_url='entry')
def meeting_report_list(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    ctx = {
        'departments': Department.objects.all(),
        'churches': Church.objects.all(),
        'home_groups': HomeGroup.objects.all(),
        'owners': CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct(),
        'types': MeetingType.objects.all()
    }

    return render(request, 'event/home_reports.html', context=ctx)


@login_required(login_url='entry')
def meeting_report_detail(request, pk):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    ctx = {
        'home_report': get_object_or_404(Meeting, pk=pk),
        'leader': request.user,
    }
    return render(request, 'event/home_report_detail.html', context=ctx)


@login_required(login_url='entry')
def meeting_report_statistics(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')

    ctx = {
        'departments': Department.objects.all(),
        'churches': Church.objects.all(),
        'home_groups': HomeGroup.objects.all(),
        'owners': CustomUser.objects.filter(home_group__leader__id__isnull=False).distinct(),
        'types': MeetingType.objects.all()
    }

    return render(request, 'event/home_statistics.html', context=ctx)


@login_required(login_url='entry')
def meetings_summary(request):
    if not request.user.is_staff and (not request.user.hierarchy or request.user.hierarchy.level < 1):
        return redirect('/')
    ctx = {
        'departments': Department.objects.all()
    }

    return render(request, 'event/meetings_summary.html', context=ctx)
