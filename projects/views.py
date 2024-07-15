from django.shortcuts import render
from projects.models import Project


# Create your views here.
def project_index(request):
    projects = Project.objects.all().order_by("-repo_only", "pk")
    for project in projects:
        if project.pk % 2 == 0:
            # hack to alternate parallax effect direction
            project.condition = None

    # context = {'projects': Project.objects.order_by("-date_created")}
    return render(
        request,
        "project_index.html",
        {"projects": projects},
    )


def project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        # TODO error page or something
        # Exception case currently impossible due to structure of request
        # (only triggered via button on existing project record)
        return

    # context = {"project": project}
    return render(request, "project_detail.html", {"project": project})
