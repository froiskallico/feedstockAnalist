from django.views import generic
from django.utils import timezone
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.mail import send_mail

from feedStockAnalist.scripts.app import App
from feedStockAnalist.forms import CreateAnalyzeForm
from .models import Analysis, MissingItems

import json

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'feedStockAnalist/index.html'
    context_object_name = 'analysis_list'
    paginate_by = 8

    def get_queryset(self):
        analysis_from_db = Analysis.objects.all()
        return analysis_from_db


class NewAnalyzeView(generic.FormView):
    form_class = CreateAnalyzeForm
    template_name = 'feedStockAnalist/new_analyze.html'
    success_url = reverse_lazy('feedStockAnalist:index')

    def form_valid(self, form):
        self.new_analyze = Analysis(created_at=timezone.now(), created_by=self.request.user)

        try:
            user = User.objects.get(pk=self.request.user.id)
            production_orders_to_analyze_list = form.cleaned_data["production_orders_list"]
            analyze_id = self.analyze(production_orders_to_analyze_list)
            send_mail(
            subject="feedstockAnalist - Análise finalizada com sucesso.",
            message="""
                Oi, {}

                Vim aqui só pra te avisar que a tua análise
                pra(s) OP(s) {} foi concluída com sucesso e já
                está disponível.

                Use o link http://192.168.1.117:80/detail/{}
                para acessá-la diretamente.
                """.format(
                    str(user.first_name),
                    str(form.cleaned_data["production_orders_list"]),
                    str(analyze_id)
                ),
            from_email="tri.inovacao@gmail.com",
            recipient_list=['kallico@datateck.com.br', user.email]
            )
        except Exception as e:
            print(e)
            send_mail(
            subject="feedstockAnalist - Deu merda!",
            message="""
                Oi.

                Vim aqui só pra te avisar que a tua análise
                pra(s) OP(s) {} não foi concluída com sucesso.
                Tente novamente acessando: http://192.168.1.117:80/new

                Detalhes do erro: {}

                """.format(
                    str(form.cleaned_data["production_orders_list"]),
                    str(e)
                ),
            from_email="tri.inovacao@gmail.com",
            recipient_list=['kallico@datateck.com.br', 'froiskallico@gmail.com']
            )

        return super(NewAnalyzeView, self).form_valid(form)

    def analyze(self, production_orders_to_analyze_list):
        self.synthesis = dict()
        self.synthesis["production_orders_to_analyze_list"] = production_orders_to_analyze_list

        analyze = App()

        items_to_analyze = analyze.get_list_of_items_to_analyze(production_orders_to_analyze_list=production_orders_to_analyze_list)

        self.synthesis["items_to_analyze"] = items_to_analyze
        self.synthesis["feedstock_items_count"] = len(items_to_analyze)
        self.synthesis["missing_feedstock_items_count"] = 0
        self.synthesis["total_cost_of_actions"] = 0
        self.new_analyze.synthesis = self.synthesis
        self.new_analyze.save()

        for item in items_to_analyze:
            report = analyze.timeline(item)
            if len(report) > 0:
                if "custo_acao_comprar" in report.keys():
                    self.synthesis["total_cost_of_actions"] += report["custo_acao_comprar"]

                if "custo_acao_antecipar" in report.keys():
                    self.synthesis["total_cost_of_actions"] += report["custo_acao_antecipar"]

                self.synthesis["missing_feedstock_items_count"] += 1
                self.new_analyze.missingitems_set.create(report = report)

        self.new_analyze.save()

        return self.new_analyze.id


class DetailView(generic.ListView):
    template_name = 'feedStockAnalist/detail.html'
    context_object_name = 'report'
    paginate_by = 10

    def get_queryset(self):
        queryset = MissingItems.objects.filter(analysis__id = self.kwargs["pk"])
        return queryset

    def get_context_data(self):
        context = super().get_context_data()

        pk = self.kwargs["pk"]

        analysis = Analysis.objects.get(pk=pk)
        context["synthesis"] = analysis.synthesis

        return context


class DeleteAnalyzeView(generic.DeleteView):
    model = Analysis
    success_url = reverse_lazy('feedStockAnalist:index')


