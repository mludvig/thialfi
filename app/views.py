from django.http import HttpResponse
from utils import render_template

def index(request):
	return render_template(request, "thialfi/index.html")
