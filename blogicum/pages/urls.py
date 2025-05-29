from django.urls import path
from .views import StaticAboutView, StaticRulesView

app_name = 'pages'

urlpatterns = [
    path('about/', StaticAboutView.as_view(), name='about'),
    path('rules/', StaticRulesView.as_view(), name='rules'),
]
