from django.urls import path
from .views import *

urlpatterns = [
    path('detail/<int:pk>/', TrainDetailView.as_view(), name='detail'),
    path('add/', TrainCreateView.as_view(), name='add'),
    path('update/<int:pk>/', TrainUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', TrainDeleteView.as_view(), name='delete'),
    path('', home, name='home'),

]
