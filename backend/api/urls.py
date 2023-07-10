from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(
    r'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)
router.register(r'tags', views.TagViewSet, basename='tags')
urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:pk>/shopping_cart/',
        views.RecipeViewSet.as_view(
            {
                'post': 'shopping_cart',
                'delete': 'delete_from_shopping_cart'
            }
        ), name='shopping_cart'),
    path(
        'recipes/<int:pk>/favorite/',
        views.RecipeViewSet.as_view(
            {
                'post': 'favorite',
                'delete': 'delete_from_favorite'
            }
        ), name='favorite'),
]
