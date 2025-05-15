from django.urls import path
from . import views

urlpatterns = [
    path('', views.DesignListView.as_view(), name='design_list'),
    path('create/', views.DesignCreateView.as_view(), name='design_create'),
    path('<int:pk>/', views.DesignDetailView.as_view(), name='design_detail'),
    path('<int:pk>/edit/', views.DesignUpdateView.as_view(), name='design_edit'),
    path('<int:pk>/publish/', views.publish_design, name='design_publish'),
    path('<int:pk>/unpublish/', views.unpublish_design, name='design_unpublish'),
]