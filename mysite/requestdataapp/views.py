from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import UploadFileForm, UserBioForm
from .misc import check_file_type, convert_file_size

file_extensions = {
    "video": [".mp4", "mov", "avi", "wmv", ]
}


def process_get_view(request: HttpRequest) -> HttpResponse:
    storage_1 = request.GET.get("a", "")
    storage_2 = request.GET.get("b", "")
    result = storage_1 + storage_2

    context = {
        "storage_1": storage_1,
        "storage_2": storage_2,
        "result": result,
    }
    return render(request, "requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm()
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    max_file_size_in_mb = 1

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]

            file_size = convert_file_size(file.size, "mbytes")

            if file_size > max_file_size_in_mb:
                return render(request, "requestdataapp/file-exception.html",
                              context={
                                  'file_size': file_size,
                                  'max_file_size': max_file_size_in_mb,
                              })

            file_path = check_file_type(file.name.lower())
            file_sys = FileSystemStorage(location=file_path)
            filename = file_sys.save(file.name, file)
            print("Saved file", filename)
    else:
        form = UploadFileForm()

    context = {
        "form": form
    }

    return render(request, "requestdataapp/file-upload.html", context=context)


def frequent_request_exception(request: HttpRequest):
    return render(request, "requestdataapp/frequent-request-exception.html")
