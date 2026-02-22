"""
Root URL configuration.

NinjaAPI routers are registered here.
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from management.tenants.api import router as tenants_router
from management.authentication.tenantusers.api import router as accounts_router
from apps.tickets.api import router as tickets_router

api = NinjaAPI(
    title="deskpro API",
    version="1.0.0",
    description="Multi-tenant helpdesk backend",
    docs_url="/docs",
)

api.add_router("/tenants", tenants_router)
api.add_router("/auth", accounts_router)
api.add_router("/tickets", tickets_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
