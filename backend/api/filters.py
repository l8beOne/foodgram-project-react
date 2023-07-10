from django_filters import FilterSet, filters
from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug',)
    is_in_favorite = filters.NumberFilter(
        method='is_in_favorite_filter'
    )
    is_in_shopping_list = filters.NumberFilter(
        method='is_in_shopping_list_filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_favorite', 'is_in_shopping_list',)

    def is_in_favorite_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset.exclude(favorite_recipes__user=self.request.user)

    def is_in_shopping_list_filter(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset.exclude(shopping_cart__user=self.request.user)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
