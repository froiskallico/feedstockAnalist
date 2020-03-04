from django.shortcuts import render
from django.views import generic

from .models import analysis


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'feedStockAnalist/index.html'
    context_object_name = 'ops_list'

    def get_queryset(self):
        # TODO: Here call new analysis
         return []
