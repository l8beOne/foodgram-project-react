from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                             ShoppingList, Tag)
from foodgram_users.models import Follow, User
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (ChangePasswordSerializer, CustomUserCreateSerializer,
                          FollowAuthorSerializer, FollowingListSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          TagSerializer, UserReadSerializer)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return CustomUserCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def change_password(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль изменён!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPagination)
    def following_list(self, request):
        queryset = User.objects.filter(following__user=request.user)
        paginated_pages = self.paginate_queryset(queryset)
        serializer = FollowingListSerializer(
            paginated_pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def follow_author(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = FollowAuthorSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, author=author)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            get_object_or_404(Follow, user=request.user,
                              author=author).delete()
            return Response(
                {'detail': 'Вы отписались от автора.'},
                status=status.HTTP_204_NO_CONTENT
            )


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже в находится избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из избранного.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_list(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            if not ShoppingList.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingList.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже находится в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            get_object_or_404(ShoppingList, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_list(self, request, **kwargs):
        ingredients = (
            IngredientRecipe.objects
            .filter(recipe__shopping_list__user=request.user)
            .values('ingredient')
            .annotate(total_quantity=Sum('quantity'))
            .values_list('ingredient__name', 'total_quantity',
                         'ingredient__measurement_unit')
        )
        file_with_ingredients = []
        for ingredient in ingredients:
            file_with_ingredients.append('{}: {} {}.'.format(*ingredient))
        file = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(file_with_ingredients),
            content_type='text/plain'
        )
        file['Content-Disposition'] = 'attachment; filename=shopping_list.txt'
        return file
