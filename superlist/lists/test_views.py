from django.core.urlresolvers import resolve
from django.shortcuts import render
from django.test import TestCase
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item, List

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


class ListViewTest(TestCase):
	"""docstring for ListViewTest"""
	def test_uses_list_template(self):
		list_ = List.objects.create()
		response = self.client.get('/lists/%d/' % (list_.id, ))
		self.assertTemplateUsed(response, 'list.html')

	def test_display_all_items(self):
		list_ = List.objects.create()
		Item.objects.create(text='Item 1', list=list_)
		Item.objects.create(text='Item 2', list=list_ )
		response = self.client.get('/lists/%d/' % list_.id)
		self.assertContains(response, 'Item 1')
		self.assertContains(response, 'Item 2')	

	def test_displays_only_item_for_that_list(self):
		correct_list = List.objects.create()
		Item.objects.create(text='Item 1', list=correct_list)
		Item.objects.create(text='Item 2', list=correct_list)
		other_list = List.objects.create()
		Item.objects.create(text='other item 1', list=other_list)
		Item.objects.create(text='other item 2', list=other_list)
		response = self.client.get('/lists/%d/' % (correct_list.id,))
		self.assertContains(response, 'Item 1')
		self.assertContains(response, 'Item 2')
		self.assertNotContains(response, 'other item 1')
		self.assertNotContains(response, 'other item 2')

	def test_passes_correct_list_to_template(self):
		other_list = List.objects.create()
		correct_list = List.objects.create()
		response = self.client.get('/lists/%d/'%correct_list.id)
		self.assertEqual(response.context['list'], correct_list)


class NewListTest(TestCase):
	def test_home_page_can_save_post_request(self):
		response = self.client.post('/lists/new',
			data = {'item_text': 'A new list item'}
		)
		self.assertEqual(Item.objects.count(), 1)
		new_item = Item.objects.first()
		self.assertEqual(new_item.text, 'A new list item')
		
	def test_home_page_redirects_after_post_request(self):
		response = self.client.post('/lists/new',
			data = {'item_text': 'A new list item'}
		)
		new_list = List.objects.first()
		self.assertRedirects(response, '/lists/%d/' % (new_list.id,))

	def test_can_save_a_post_request_to_an_existing_list(self):
		other_list = List.objects.create()
		correct_list = List.objects.create()
		self.client.post(
			'/lists/%d/add_item'%correct_list.id,
			data={'item_text': 'A new Item for existing list'}
		)
		self.assertEqual(Item.objects.count(), 1)
		new_item = Item.objects.first()
		self.assertEqual(new_item.text, 'A new Item for existing list')
		self.assertEqual(new_item.list, correct_list)

	def test_redirects_to_list_view(self):
		other_list = List.objects.create()
		correct_list = List.objects.create()
		response = self.client.post(
			'/lists/%d/add_item' % correct_list.id,
			data={'item_text': "A new Item for existing list"}
		)
		self.assertRedirects(response, '/lists/%d/' % correct_list.id)
