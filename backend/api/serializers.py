from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from foodgram.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                             ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Follow, User

from .validators import validate_username


class UserReadSerializer(UserSerializer):
    """Получение списка пользователей."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name')


class CustomUserCreateSerializer(UserCreateSerializer):
    """Создание нового пользователя."""
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validate_username
        ],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'password')
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False},
        }

    def validate(self, value):
        email = value['email']
        username = value['username']
        if (User.objects.filter(email=email).exists()
                and not User.objects.filter(username=username).exists()):
            raise serializers.ValidationError(
                'Попробуйте указать другую электронную почту.'
            )
        if (User.objects.filter(username=username).exists()
                and not User.objects.filter(email=email).exists()):
            raise serializers.ValidationError(
                'Попробуйте указать другое имя пользователя.'
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Изменение пароля пользователя."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'new_password')

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError('Неправильный пароль.')
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                'Новый пароль должен отличаться от предыдущего.'
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class FollowingListSerializer(serializers.ModelSerializer):
    """Список подписок пользователя."""
    is_subscribed = serializers.SerializerMethodField()
    recipes_quantity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'recipes_quantity', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Follow.objects.filter(user=self.context['request'].user,
                                      author=obj).exists()
        )

    def get_recipes_quantity(self, obj):
        return obj.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time',)
        read_only_fields = ('name', 'cooking_time',)


class FollowAuthorSerializer(serializers.ModelSerializer):
    """Подписка и отписка от авторов."""
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_quantity = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'recipes',
                  'recipes_quantity', 'is_subscribed',)
        read_only_fields = ('email', 'username',)

    def validate(self, obj):
        if (self.context['request'].user == obj):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        return obj

    def get_recipes_quantity(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Follow.objects.filter(user=self.context['request'].user,
                                      author=obj).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Получение списка ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Получение списка тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Список ингредиентов с количеством"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name',
                  'measurement_unit', 'quantity')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Список рецептов"""
    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, read_only=True, source='recipes'
    )
    image = Base64ImageField()
    is_in_favorite = serializers.SerializerMethodField()
    is_in_shopping_list = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_in_favorite', 'is_in_shopping_list',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_in_favorite(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

    def get_is_in_shopping_list(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists()
        )


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'quantity')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание рецепта."""
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(),
                                        many=True,
                                        slug_field='slug'
                                        )
    author = UserReadSerializer(read_only=True)
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'tags', 'image',
                  'name', 'text',
                  'cooking_time', 'author')
        extra_kwargs = {
            'ingredients': {'required': True, 'allow_blank': False},
            'tags': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'image': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get(
                pk=ingredient['id']
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                quantity=ingredient['quantity']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tag = validated_data.get('tag', instance.tag)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            lst = []
            for ingredient in ingredients_data:
                current_ingredient, status = Ingredient.objects.get(
                    pk=ingredient['id']
                )
                lst.append(current_ingredient)
            instance.ingredients.set(lst)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context=self.context).data
