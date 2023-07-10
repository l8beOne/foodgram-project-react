from django_filters import FilterSet, filters
from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug',)
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def is_favorited_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
