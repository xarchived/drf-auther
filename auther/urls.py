from django.urls import include, path
from rest_framework.routers import SimpleRouter

from auther.views import (
    PermViewSet,
    RoleViewSet,
    DomainViewSet,
    UserViewSet,
    LoginView,
    LogoutView,
    OtpLoginView
)

router = SimpleRouter()
router.register(r'perms', PermViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('otplogin/', OtpLoginView.as_view()),
    path('logout/', LogoutView.as_view())
]
