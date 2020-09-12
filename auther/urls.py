from django.urls import include, path
from rest_framework import routers

from auther.views import PermViewSet, RoleViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'perms', PermViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls))
]
