from django.shortcuts import render
from projects.models import Project


# Create your views here.
def project_index(request):
    # repo_only projects are most recent
    # TODO add a date_created field for cleaner sorting
    projects = Project.objects.all().order_by("-repo_only")
    for project in projects:
        if project.pk % 2 == 0:
            # hack to alternate parallax effect direction
            project.condition = None

    context = {'projects': projects}
    return render(request, 'project_index.html', context)


def project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        # TODO error page or something
        # Exception case currently impossible due to structure of request
        # (only triggered via button on existing project record)
        return

    context = {'project': project}
    return render(request, 'project_detail.html', context)
