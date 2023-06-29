from django_filters import FilterSet, filters
from foodgram.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug',)
    is_in_favorite = filters.BooleanFilter(
        method='is_in_favorite_filter'
    )
    is_in_shopping_list = filters.BooleanFilter(
        method='is_in_shopping_list_filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def is_in_favorite_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipes__user=user)
        return queryset

    def is_in_shopping_list_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_list__user=user)
        return queryset
