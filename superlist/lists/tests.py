from django.core.urlresolvers import resolve
from django.shortcuts import render
from django.test import TestCase
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item

class HomePageTest(TestCase):

	def test_root_url_resolves_to_home_page(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)

	def test_home_page_return_correct_html(self):
		request = HttpRequest()
		response = home_page(request)
		self.assertIn('To-Do lists', response.content.decode())

	def test_home_page_only_save_item_when_necessary(self):
		request = HttpRequest()
		home_page(request)
		self.assertEqual(Item.objects.count(), 0)

	def test_home_page_can_save_post_request(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['item_text'] = 'A new list item'
		response = home_page(request)
		self.assertEqual(Item.objects.count(), 1)
		new_item = Item.objects.first()
		self.assertEqual(new_item.text, 'A new list item')
		
	def test_home_page_redirects_after_post_request(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['item_text'] = 'A new list item'
		response = home_page(request)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')
	
	def test_home_page_display_all_list_item(self):
		Item.objects.create(text='Item 1')
		Item.objects.create(text='Item 2')

		request = HttpRequest()
		response = home_page(request)
		self.assertIn('Item 1', response.content.decode())
		self.assertIn('Item 2', response.content.decode())

class ItemModelTest(TestCase):

	def test_saving_and_retrieving_items(self):
		first_item = Item()
		first_item.text = 'The first ever list item'
		first_item.save()

		second_item = Item()
		second_item.text = 'Item the second'
		second_item.save()

		saved_item = Item.objects.all()
		self.assertEqual(saved_item.count(), 2)

		first_saved_item = saved_item[0]
		second_saved_item = saved_item[1]
		self.assertEqual(first_saved_item.text, 'The first ever list item')
		self.assertEqual(second_saved_item.text, 'Item the second')