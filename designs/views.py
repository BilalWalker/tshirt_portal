# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Design, DesignStatus
from .forms import DesignForm
from .shopify_integration import publish_to_shopify, unpublish_from_shopify

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Design, DesignStatus
from .forms import DesignForm

# Import both integration modules to give options
from .shopify_integration import publish_to_shopify, unpublish_from_shopify
from .shopify_graphql import publish_product as publish_to_shopify_graphql
from .shopify_graphql import unpublish_product as unpublish_from_shopify_graphql
from .shopify_graphql import test_connection as test_graphql_connection

# Use the REST API by default
USE_GRAPHQL_API = True  # Set to True to use GraphQL API instead of REST


class DesignListView(LoginRequiredMixin, ListView):
    model = Design
    template_name = 'designs/list.html'
    context_object_name = 'designs'
    
    def get_queryset(self):
        # Admin can see all designs, others see only their own
        if self.request.user.is_admin():
            return Design.objects.all().order_by('-created_at')
        return Design.objects.filter(creator=self.request.user).order_by('-created_at')

class DesignDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Design
    template_name = 'designs/detail.html'
    
    def test_func(self):
        design = self.get_object()
        return self.request.user.is_admin() or design.creator == self.request.user

class DesignCreateView(LoginRequiredMixin, CreateView):
    model = Design
    form_class = DesignForm
    template_name = 'designs/create.html'
    success_url = reverse_lazy('design_list')
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.status = DesignStatus.DRAFT
        return super().form_valid(form)

class DesignUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Design
    form_class = DesignForm
    template_name = 'designs/edit.html'
    
    def test_func(self):
        design = self.get_object()
        return self.request.user.is_admin() or design.creator == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('design_detail', kwargs={'pk': self.object.pk})



@login_required
def test_shopify_api(request):
    """Test the Shopify API connection and show the results"""
    if USE_GRAPHQL_API:
        success, message = test_graphql_connection()
    else:
        from .shopify_integration import test_shopify_connection
        success, message = test_shopify_connection()
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('dashboard')

@login_required
def publish_design(request, pk):
    design = get_object_or_404(Design, pk=pk)
    
    # Check permission
    if not (request.user.is_admin() or design.creator == request.user):
        messages.error(request, "You don't have permission to publish this design.")
        return redirect('design_detail', pk=pk)
    
    # Already published
    if design.status == DesignStatus.PUBLISHED:
        messages.info(request, "This design is already published to Shopify.")
        return redirect('design_detail', pk=pk)
    
    # Publish to Shopify using selected API
    if USE_GRAPHQL_API:
        success, product_id, product_url = publish_to_shopify_graphql(design)
    else:
        success, product_id, product_url = publish_to_shopify(design)
    
    if success:
        design.status = DesignStatus.PUBLISHED
        design.shopify_product_id = product_id
        design.shopify_product_url = product_url
        design.save()
        messages.success(request, f"Design '{design.title}' published to Shopify successfully!")
    else:
        messages.error(request, "Failed to publish design to Shopify. Please try again.")
    
    return redirect('design_detail', pk=pk)

@login_required
def unpublish_design(request, pk):
    design = get_object_or_404(Design, pk=pk)
    
    # Check permission
    if not (request.user.is_admin() or design.creator == request.user):
        messages.error(request, "You don't have permission to unpublish this design.")
        return redirect('design_detail', pk=pk)
    
    # Not published
    if design.status == DesignStatus.DRAFT:
        messages.info(request, "This design is not published.")
        return redirect('design_detail', pk=pk)
    
    # Unpublish from Shopify using selected API
    if USE_GRAPHQL_API:
        success = unpublish_from_shopify_graphql(design.shopify_product_id)
    else:
        success = unpublish_from_shopify(design.shopify_product_id)
    
    if success:
        design.status = DesignStatus.DRAFT
        design.shopify_product_id = None
        design.shopify_product_url = None
        design.save()
        messages.success(request, f"Design '{design.title}' unpublished from Shopify successfully!")
    else:
        messages.error(request, "Failed to unpublish design from Shopify. Please try again.")
    
    return redirect('design_detail', pk=pk)