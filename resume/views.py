from django.shortcuts import render


# Create your views here.
def resume_index(request):
    # return render(request, "index.html", {})
    return render(request, "resume.html", {})
