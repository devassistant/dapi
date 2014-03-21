from django.shortcuts import render_to_response, get_object_or_404
from dapi.models import Dap

def index(request):
    daps_list = Dap.objects.all().order_by('package_name')
    return render_to_response('dapi/index.html', {'daps_list': daps_list})

def dap(request, dap):
    d = get_object_or_404(Dap, package_name=dap)
    return render_to_response('dapi/dap.html', {'dap': d})
