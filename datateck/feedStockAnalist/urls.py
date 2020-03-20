from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name='feedStockAnalist'
urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('new/', views.NewAnalyzeView.as_view(), name='new'),
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('delete/<int:pk>/', views.DeleteAnalyzeView.as_view(), name='delete'),
]
