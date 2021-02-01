from django.urls import include, path
from rest_framework import routers

from auther import views

router = routers.DefaultRouter()
router.register(r'domains', views.DomainViewSet)
router.register(r'perms', views.PermViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view())
]
