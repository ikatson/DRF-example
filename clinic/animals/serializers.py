# coding: utf-8
from rest_framework import serializers
from clinic.animals.models import Customer, Pet


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = (
            'id',
            'name',
        )


class BasePetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ('id', 'name',)


class PetSerializer(BasePetSerializer):
    """Serializer for /pets/"""

    # Problem #1 solution
    # 2 separate fields for reading and writing
    # I can come up with other ways to do it, but this one feels the easiest.
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)

    def validate_customer_id(self, value):
        if not Customer.objects.filter(id=value).exists():
            raise serializers.ValidationError('No such customer')
        return value

    def to_representation(self, instance):
        """Hide customer data, if the user is not allowed to see it."""

        # You did not have a problem like this in the Google Doc, but I assumed
        # you might.

        representation = super(PetSerializer, self).to_representation(instance)

        # Hide the customer data, if the user was passed through the context,
        # and the user cannot see the customer.
        user = self.context.get('user')
        if user and not instance.customer.can_be_seen_by(user):
            representation['customer'] = {'id': instance.customer_id}
        return representation

    class Meta(BasePetSerializer.Meta):
        fields = BasePetSerializer.Meta.fields + (
            'customer',
            'customer_id'
        )


class CustomerPetSerializer(BasePetSerializer):
    """Serializer for /customers/ID/pets/"""
