from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name='feedStockAnalist'
urlpatterns = [
    path('', login_required(views.IndexView.as_view())),
    path('detail/', views.DetailView.as_view(), name='detail')
]
