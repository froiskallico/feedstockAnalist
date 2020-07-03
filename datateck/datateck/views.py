
from django.urls import reverse_lazy
from django.views import generic
from datateck.forms import SignUpForm

class RegisterView(generic.FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)

class HelpView(generic.TemplateView):
    template_name = "help/help_page.html"

