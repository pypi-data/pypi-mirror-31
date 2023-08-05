# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection, models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

try:
    # use bulk_update if installed
    from django_bulk_update.helper import bulk_update
except ImportError:
    bulk_update = None

import json
import timeit


class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class TreeNodeModel(models.Model):

    """
    Usage:

    from __future__ import unicode_literals

    from django.db import models
    from django.utils.encoding import python_2_unicode_compatible

    from treenode.models import TreeNodeModel


    @python_2_unicode_compatible
    class MyModel(TreeNodeModel):

        name = models.CharField(max_length=50)

        class Meta(TreeNodeModel.Meta):
            verbose_name = 'My Model'
            verbose_name_plural = 'My Models'

        def __str__(self):
            return self.get_display_text(self.name)
    """

    tn_parent = models.ForeignKey('self',
        related_name='tn_children', on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name=_('Parent'), )

    tn_parents_pks = models.CharField(
        max_length=500, blank=True,
        default='', editable=False,
        verbose_name=_('Parents pks'), )

    tn_parents_count = models.PositiveSmallIntegerField(
        default=0, editable=False,
        verbose_name=_('Parents count'), )

    tn_children_pks = models.CharField(
        max_length=500, blank=True,
        default='', editable=False,
        verbose_name=_('Children pks'), )

    tn_children_count = models.PositiveSmallIntegerField(
        default=0, editable=False,
        verbose_name=_('Children count'), )

    tn_children_tree_pks = models.CharField(
        max_length=500, blank=True,
        default='', editable=False,
        verbose_name=_('Children tree pks'), )

    tn_siblings_pks = models.CharField(
        max_length=500, blank=True,
        default='', editable=False,
        verbose_name=_('Siblings pks'), )

    tn_siblings_count = models.PositiveSmallIntegerField(
        default=0, editable=False,
        verbose_name=_('Siblings count'), )

    tn_level = models.PositiveSmallIntegerField(
        default=0, editable=False,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Level'), )

    tn_index = models.PositiveSmallIntegerField(
        default=0, editable=False,
        verbose_name=_('Index'), )

    tn_depth = models.PositiveSmallIntegerField(
        default=0, editable=False,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Depth'), )

    tn_priority = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(9999)],
        verbose_name=_('Priority'), )

    tn_order = models.PositiveSmallIntegerField(
        default=0, editable=False,
        verbose_name=_('Order'), )

    @classproperty
    def tree(cls):
        return cls.get_tree()

    @classproperty
    def roots(cls):
        return cls.get_roots()

    @property
    def root(self):
        return self.get_root()

    @property
    def parent(self):
        return self.get_parent()

    @property
    def parents(self):
        return self.get_parents()

    @property
    def parents_count(self):
        return self.get_parents_count()

    @property
    def children(self):
        return self.get_children()

    @property
    def children_count(self):
        return self.get_children_count()

    @property
    def children_tree(self):
        return self.get_children_tree()

    @property
    def siblings(self):
        return self.get_siblings()

    @property
    def siblings_count(self):
        return self.get_siblings_count()

    @property
    def level(self):
        return self.get_level()

    @property
    def index(self):
        return self.get_index()

    @property
    def depth(self):
        return self.get_depth()

    @property
    def priority(self):
        return self.get_priority()

    @property
    def order(self):
        return self.get_order()

    @classmethod
    def get_tree(cls):
        return cls.__get_nodes_tree()

    @classmethod
    def get_roots(cls):
        return list(cls.get_roots_queryset())

    @classmethod
    def get_roots_queryset(cls):
        return cls.objects.filter(tn_parent=None)

    def get_root(self):
        root_pk = (self.split_pks(self.tn_parents_pks) + [self.pk])[0]
        root_obj = self.__class__.objects.get(pk=root_pk)
        return root_obj

    def get_parent(self):
        return self.tn_parent

    def get_parents(self):
        return list(self.get_parents_queryset())

    def get_parents_count(self):
        return self.tn_parents_count

    def get_parents_queryset(self):
        return self.queryset_pks(self.tn_parents_pks)

    def get_children(self):
        return list(self.get_children_queryset())

    def get_children_count(self):
        return self.tn_children_count

    def get_children_queryset(self):
        return self.queryset_pks(self.tn_children_pks)

    def get_children_tree(self):
        return self.__get_nodes_tree(self)

    def get_siblings(self):
        return list(self.get_siblings_queryset())

    def get_siblings_count(self):
        return self.tn_siblings_count

    def get_siblings_queryset(self):
        return self.queryset_pks(self.tn_siblings_pks)

    def get_level(self):
        return self.tn_level

    def get_index(self):
        return self.tn_index

    def get_depth(self):
        return self.tn_depth

    def get_priority(self):
        return self.tn_priority

    def get_order(self):
        return self.tn_order

    @classmethod
    def get_display(cls):
        objs = list(cls.objects.all())
        strs = [str(obj) for obj in objs]
        d = '\n'.join(strs)
        return d

    def get_display_text(self, text='', tab='— '):
        tabs = (tab * self.tn_parents_count)
        text = text or str(self.pk)
        return force_text(tabs + text)

    def is_first_child(self):
        return (self.tn_index == 0)

    def is_last_child(self):
        return (self.tn_index == (self.tn_siblings_count - 1))

    PKS_SEPARATOR = ','

    @classmethod
    def join_pks(cls, l):
        s = TreeNodeModel.PKS_SEPARATOR.join([str(v) for v in l])
        return s

    @classmethod
    def split_pks(cls, s):
        l = [int(v) for v in s.split(TreeNodeModel.PKS_SEPARATOR) if v]
        return l

    @classmethod
    def queryset_pks(cls, s):
        pks = cls.split_pks(s)
        qs = cls.objects.filter(pk__in=pks)
        return qs

    def __get_node_order_str(self):
        priority_max = 99999
        priority_len = len(str(priority_max))
        priority_val = priority_max - min(self.tn_priority, priority_max)
        priority_key = str(priority_val).zfill(priority_len)
        alphabetical_val = slugify(str(self))
        alphabetical_key = alphabetical_val.rjust(priority_len, str('z'))
        alphabetical_key = alphabetical_key[0:priority_len]
        pk_val = min(self.pk, priority_max)
        pk_key = str(pk_val).zfill(priority_len)
        s = '%s%s%s' % (priority_key, alphabetical_key, pk_key, )
        s = s.upper()
        return s

    def __get_node_data(self, objs):

        # retrieve parents
        parent_obj = self.tn_parent
        parents_list = []
        obj = parent_obj

        while obj:
            parents_list.insert(0, obj)
            obj = obj.tn_parent

        parents_pks = [obj.pk for obj in parents_list]
        parents_count = len(parents_list)

        obj_dict = {}

        # update parents
        obj_dict['tn_parents_pks'] = parents_pks
        obj_dict['tn_parents_count'] = parents_count

        # update children
        children_pks = [
            obj.pk for obj in objs \
            if obj.tn_parent == self]

        obj_dict['tn_children_pks'] = children_pks
        obj_dict['tn_children_count'] = len(children_pks)
        obj_dict['tn_children_tree_pks'] = []

        # update siblings
        siblings_pks = [
            obj.pk for obj in objs \
            if obj.tn_parent == self.tn_parent and obj.pk != self.pk]

        obj_dict['tn_siblings_pks'] = siblings_pks
        obj_dict['tn_siblings_count'] = len(siblings_pks)

        # update level
        obj_dict['tn_level'] = (parents_count + 1)

        # update depth
        obj_dict['tn_depth'] = 0

        # update order
        order_objs = list(parents_list) + [self]
        order_strs = [obj.__get_node_order_str() for obj in order_objs]
        order_str = ''.join(order_strs)[0:150]
        obj_dict['tn_order_str'] = order_str

        return obj_dict

    @classmethod
    def __get_nodes_data(cls):

        objs_qs = cls.objects.select_related('tn_parent')
        objs_list = list(objs_qs)
        objs_dict = {
            str(obj.pk):obj.__get_node_data(objs_list) \
            for obj in objs_list}

        # get sorted dict keys
        objs_dict_keys = list(objs_dict.keys())
        objs_dict_keys.sort(
            key=lambda obj_key: objs_dict[obj_key]['tn_order_str'])

        # get sorted dict values
        objs_dict_values = list(objs_dict.values())
        objs_dict_values.sort(
            key=lambda obj_value: obj_value['tn_order_str'])

        objs_sort_pks = lambda obj_pk: objs_dict_keys.index(str(obj_pk))

        # update order
        objs_order_cursor = 0
        for obj_data in objs_dict_values:
            obj_data.pop('tn_order_str', None)
            obj_data['tn_order'] = objs_order_cursor
            objs_order_cursor += 1

        # update index
        objs_index_cursors = {}
        objs_index_cursor = 0
        for obj_data in objs_dict_values:
            obj_parents_pks = str(obj_data['tn_parents_pks'])
            objs_index_cursor = objs_index_cursors.get(obj_parents_pks, 0)
            obj_data['tn_index'] = objs_index_cursor
            objs_index_cursor += 1
            objs_index_cursors[obj_parents_pks] = objs_index_cursor

        # update depth
        for obj_data in objs_dict_values:
            obj_children_count = obj_data['tn_children_count']
            if obj_children_count > 0:
                continue
            obj_parents_count = obj_data['tn_parents_count']
            if obj_parents_count == 0:
                continue
            obj_parents_pks = obj_data['tn_parents_pks']
            for obj_parent_pk in obj_parents_pks:
                obj_parent_key = str(obj_parent_pk)
                obj_parent_data = objs_dict[obj_parent_key]
                obj_parent_index = obj_parents_pks.index(obj_parent_pk)
                obj_parent_depth = (obj_parents_count - obj_parent_index)
                if obj_parent_data['tn_depth'] < obj_parent_depth:
                    obj_parent_data['tn_depth'] = obj_parent_depth

        # update children and siblings pks order
        for obj_data in objs_dict_values:
            # update children pks order
            if obj_data['tn_children_pks']:
                obj_data['tn_children_pks'].sort(key=objs_sort_pks)
            # update siblings pks order
            if obj_data['tn_siblings_pks']:
                obj_data['tn_siblings_pks'].sort(key=objs_sort_pks)

        # update tree pks
        objs_dict_values.sort(key=lambda obj: obj['tn_level'], reverse=True)
        for obj_data in objs_dict_values:
            if obj_data['tn_children_count'] == 0:
                continue
            obj_children_pks = obj_data['tn_children_pks']
            obj_children_tree_pks = list(obj_children_pks)
            for obj_child_pk in obj_children_pks:
                obj_child_key = str(obj_child_pk)
                obj_child_data = objs_dict[obj_child_key]
                obj_child_children_tree_pks = obj_child_data.get('tn_children_tree_pks', [])
                if obj_child_children_tree_pks:
                    obj_children_tree_pks += obj_child_children_tree_pks
            obj_data['tn_children_tree_pks'] = obj_children_tree_pks
            # update children tree pks order
            if obj_data['tn_children_tree_pks']:
                obj_data['tn_children_tree_pks'].sort(key=objs_sort_pks)

        # join all pks lists
        for obj_data in objs_dict_values:
            obj_data['tn_parents_pks'] = cls.join_pks(obj_data['tn_parents_pks'])
            obj_data['tn_siblings_pks'] = cls.join_pks(obj_data['tn_siblings_pks'])
            obj_data['tn_children_pks'] = cls.join_pks(obj_data['tn_children_pks'])
            obj_data['tn_children_tree_pks'] = cls.join_pks(obj_data['tn_children_tree_pks'])

        return (objs_list, objs_dict, )

    @classmethod
    def __get_nodes_tree(cls, instance=None):

        def __get_node_tree(obj):
            child_tree = { 'instance':obj, 'children':[] }
            # child_tree = { 'instance':str(obj.pk), 'children':[] }
            if obj.tn_children_pks:
                children_pks = obj.split_pks(obj.tn_children_pks)
                for child_pk in children_pks:
                    child_key = str(child_pk)
                    child_obj = objs_dict[child_key]
                    child_tree['children'].append(__get_node_tree(child_obj))
            return child_tree

        if instance:
            objs_list = instance.get_children()
            objs_dict = { str(obj.pk):obj for obj in objs_list }
            objs_tree = __get_node_tree(instance)['children']
        else:
            objs_list = list(cls.objects.all())
            objs_dict = { str(obj.pk):obj for obj in objs_list }
            objs_tree = [__get_node_tree(obj) for obj in objs_list if obj.level == 1]

        return objs_tree

    def __update_node_data(self, data):
        if data:
            for key, value in data.items():
                setattr(self, key, value)

    @staticmethod
    @receiver(post_delete, dispatch_uid='post_delete_treenode')
    @receiver(post_save, dispatch_uid='post_save_treenode')
    def __update_nodes_data(sender, instance, **kwargs):

        if not isinstance(instance, TreeNodeModel):
            return

        if settings.DEBUG:
            start_time = timeit.default_timer()
            start_queries = len(connection.queries)

        objs_list, objs_dict = sender.__get_nodes_data()

        # update instance data
        instance.__update_node_data(objs_dict.get(str(instance.pk)))

        # update db data
        if bulk_update:
            for obj in objs_list:
                obj.__update_node_data(objs_dict.get(str(obj.pk)))
            bulk_update(objs_list)
        else:
            with transaction.atomic():
                for obj_key, obj_data in objs_dict.items():
                    obj_pk = int(obj_key)
                    sender.objects.filter(pk=obj_pk).update(**obj_data)

        # print(json.dumps(instance.get_children_tree(), indent=4))
        # print(json.dumps(instance.get_tree(), indent=4))

        if settings.DEBUG:
            duration = timeit.default_timer() - start_time
            queries = len(connection.queries) - start_queries
            print('%s.__update_nodes_data in %ss with %s queries.' % (
                sender.__name__, duration, queries, ))

    class Meta:
        abstract = True
        ordering = ['tn_order']
