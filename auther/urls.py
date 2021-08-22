from django.urls import include, path
from rest_framework.routers import SimpleRouter

from auther.views import (
    PermViewSet,
    RoleViewSet,
    DomainViewSet,
    UserViewSet,
    LoginView,
    LogoutView,
    SendOtpView,
    MeViewSet,
)

router = SimpleRouter()
router.register(r'perms', PermViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('self/', MeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update'})),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('send_otp/', SendOtpView.as_view()),
]
