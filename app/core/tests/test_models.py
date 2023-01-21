from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@test.com', password='test123'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    
    def test_creat_user_with_email_succssful(self):
        email = 'test@test.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_normalized(self):
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(email, 'test123')
        
        self.assertEqual(user.email, email.lower())
        
    def test_new_user_inalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')
            
    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        
        self.assertEqual(str(tag), tag.name)
        
    def test_ingredient_str(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucunber'
        )
        
        self.assertEqual(str(ingredient), ingredient.name)
        
    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='bla bla',
            time_minutes=5,
        )
        
        self.assertEqual(str(recipe), recipe.title)