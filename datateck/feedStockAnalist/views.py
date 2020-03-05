from django.shortcuts import render
from django.views import generic

from feedStockAnalist.scripts.app import App
from .models import Analysis


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'feedStockAnalist/index.html'
    context_object_name = 'analysis_list'

    def get_queryset(self):
        analysis = Analysis.objects.all()
        return analysis

        # TODO: Here call App(csv=True, lista_ops=(114562)).analist() on analysis creation
        # may not to call it here,
        # may i need to call it from view and,
        # from there, store it to analysis field

class DetailView(generic.TemplateView):
    template_name = 'feedStockAnalist/detail.html'

    def get_queryset(self):
        return []
