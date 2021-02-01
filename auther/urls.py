from django.urls import include, path
from rest_framework import routers

from auther.views import DomainViewSet, PermViewSet, RoleViewSet, UserViewSet, LoginView, LogoutView

router = routers.DefaultRouter()
router.register(r'domains', DomainViewSet)
router.register(r'perms', PermViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view())
]
