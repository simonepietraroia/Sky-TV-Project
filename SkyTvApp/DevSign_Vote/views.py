from django.shortcuts import render

# Create your views here.

def test_base_template(request):
    return render(request, 'DevSign_Vote/base.html')