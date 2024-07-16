from django.shortcuts import render
from projects.models import Project


# Create your views here.
def project_index(request):
    # changes to condition below do not update unless query is first executed here (by using list())
    projects = list(Project.objects.all().order_by("-date_created"))
    for project in projects[::2]:
        # hack to alternate parallax effect direction
        project.condition = None

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

    return render(request, "project_detail.html", {"project": project})
