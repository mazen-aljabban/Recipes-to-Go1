from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URLS = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='some tag'):
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='some ingredient'):
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 5
    }
    defaults.update(params)
    
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_required(self):
        res = self.client.get(RECIPES_URLS)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
    
class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'test123'
        )
        self.client.force_authenticate(self.user)
        
    def test_retrieve_recipe(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URLS)
        
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'bla@test.com',
            'blabla123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URLS)
        
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
        
    def test_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        
        url = detail_url(recipe.id)
        res = self.client.get(url)
        
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        
    def test_create_basic_recipe(self):
        payload = {
            'title': 'chocolate',
            'time_minutes': 2,
        }
        res = self.client.post(RECIPES_URLS, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
            
    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(user=self.user, name='blaa')
        tag2 = sample_tag(user=self.user, name='bla')
        payload = {
            'title': 'blassss',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 33,
        }
        res = self.client.post(RECIPES_URLS, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        
    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(user=self.user, name='blaa')
        ingredient2 = sample_ingredient(user=self.user, name='bla')
        payload = {
            'title': 'blassss',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 33,
        }
        res = self.client.post(RECIPES_URLS, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)