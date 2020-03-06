from django.shortcuts import render
from django.views import generic

from feedStockAnalist.scripts.app import App
from .models import Analysis

import json

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'feedStockAnalist/index.html'
    context_object_name = 'analysis_list'

    def get_queryset(self):
        analysis_from_db = Analysis.objects.all()
        queryset = []

        for analyze in analysis_from_db:
            analyze_converted = self.convert_analyze_report_from_json_to_dict(analyze)
            queryset.append(analyze_converted)

        return queryset

    def convert_analyze_report_from_json_to_dict(self, analyze):
        analyze_report_as_dict = json.loads(analyze.report)
        analyze_parsed = analyze
        analyze_parsed.report = analyze_report_as_dict
        return analyze_parsed





class DetailView(generic.TemplateView):
    template_name = 'feedStockAnalist/detail.html'

    def get_queryset(self):
        return []

class NewAnalyzeView(generic.CreateView):
    pass

    # TODO: Here call App(csv=True, lista_ops=(114562)).analist() on analysis creation
    # may not to call it here,
    # may i need to call it from view and,
    # from there, store it to analysis field
