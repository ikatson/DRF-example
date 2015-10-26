# coding: utf-8

from django.conf import settings
from django.db import models


class CustomerQueryset(models.QuerySet):

    def filter_for_user(self, user):
        """Filter only customers visible to user."""

        # this is just for simplicity, not to get a 500 when an anonnymous
        # user logs in, of course you need to set-up real authentication in
        # real code.
        if not user.is_authenticated():
            return self.none()

        # superusers will have this permission by default
        if user.has_perm('view_all_customers'):
            return self

        return self.filter(users__id=user.id)


class Customer(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    objects = CustomerQueryset.as_manager()

    def can_be_seen_by(self, user):
        # You can do it more efficiently, but this one-liner is very simple.
        return Customer.objects.filter(pk=self.pk).filter_for_user(user).exists()

    class Meta:
        # example permission to allow a user see every customer without being
        # superuser
        permissions = (
            ('view_all_customers', u'Can view all customers'),
        )


class Pet(models.Model):
    name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, related_name='pets')



