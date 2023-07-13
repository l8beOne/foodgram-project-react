from django_filters import FilterSet, filters
from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    author = filters.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited',
        label='favorite',
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart',
        label='shopping_cart',
    )
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug',)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset.exclude(favorite_recipes__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset.exclude(shopping_cart__user=self.request.user)


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
