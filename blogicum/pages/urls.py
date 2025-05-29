# from django.urls import path
# from . import views

# app_name = 'pages'

# urlpatterns = [
#     path('about/', views.AboutPage.as_view(), name='about'),
#     path('rules/', views.RulesPage.as_view(), name='rules')
# ]
from django.urls import path
from .views import StaticAboutView, StaticRulesView

app_name = 'pages'

urlpatterns = [
    path('about/', StaticAboutView.as_view(), name='about'),
    path('rules/', StaticRulesView.as_view(), name='rules'),
]
