from django.urls import path
from . import views

urlpatterns = [
    # The Homepage
    path('', views.home, name='home'),
    
    # The New PDF Invoice Page
    path('invoice/<int:billing_id>/', views.generate_invoice, name='generate_invoice'),
]