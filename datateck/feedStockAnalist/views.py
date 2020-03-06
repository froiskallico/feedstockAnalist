from django.shortcuts import render
from django.views import generic
from django.utils import timezone

from feedStockAnalist.scripts.app import App
from feedStockAnalist.forms import CreateAnalyzeForm
from .models import Analysis

import json

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'feedStockAnalist/index.html'
    context_object_name = 'analysis_list'

    def get_queryset(self):
        analysis_from_db = Analysis.objects.all()
        return analysis_from_db

        # for analyze in analysis_from_db:
        #     analyze_converted = self.convert_analyze_report_from_json_to_dict(analyze)
        #     queryset.append(analyze_converted)

        # return queryset

    def convert_analyze_report_from_json_to_dict(self, analyze):
        analyze_report_as_dict = json.loads(analyze.report)
        analyze_parsed = analyze
        analyze_parsed.report = analyze_report_as_dict
        return analyze_parsed

class DetailView(generic.TemplateView):
    model = Analysis
    template_name = 'feedStockAnalist/detail.html'

    def get_queryset(self):
        return Analysis.objects.all()

class NewAnalyzeView(generic.FormView):
    form_class = CreateAnalyzeForm
    template_name = 'feedStockAnalist/new_analyze.html'
    success_url = '/'

    def form_valid(self, form):
        new_analyze = Analysis(created_at=timezone.now())
        synthesis = self.analyze(form.cleaned_data["production_orders_list"])
        json_synthesis = json.dumps(synthesis)
        new_analyze.synthesis = json_synthesis
        new_analyze.save()
        print(new_analyze)
        return super(NewAnalyzeView, self).form_valid(form)


    def analyze(self, production_orders_to_analyze):
        analyze = App()
        analyze.analyze(production_orders_to_analyze_list=production_orders_to_analyze)
        return analyze.synthesis




