# coding: utf-8
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from clinic.animals.models import Pet, Customer
from clinic.animals.serializers import PetSerializer, CustomerPetSerializer, \
    CustomerSerializer


class PetViewSet(ModelViewSet):
    queryset = Pet.objects.all().select_related('customer')
    serializer_class = PetSerializer

    def get_serializer_context(self):
        ctx = super(PetViewSet, self).get_serializer_context()
        ctx['user'] = self.request.user
        return ctx

    def dispatch(self, request, *args, **kwargs):
        # Problem #5 solution.
        # This is an entry point to all "actions", you can do whatever you want
        # here.
        return super(PetViewSet, self).dispatch(request, *args, **kwargs)


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all().prefetch_related('pets')
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return super(CustomerViewSet, self).get_queryset().filter_for_user(
            self.request.user
        )


class MyNestedViewSetMixin(NestedViewSetMixin):

    # Possible generic solution to problem #2. This is a "drf-extensions"
    # library problem. Looks like the solution works.
    def perform_create(self, serializer):
        return serializer.save(**self.get_parents_query_dict())


class CustomerPetViewSet(MyNestedViewSetMixin, ModelViewSet):
    authentication_classes = [SessionAuthentication]
    serializer_class = CustomerPetSerializer
    queryset = Pet.objects.all()

    def get_queryset(self):
        # Possible non-generic solution to problem #4. This is a
        # "drf-extensions" library problem. Looks like the solution works.
        customer_id = self.get_parents_query_dict()['customer_id']

        if not Customer.objects.filter(id=customer_id).filter_for_user(
            self.request.user
        ):
            raise NotFound

        return super(CustomerPetViewSet, self).get_queryset()
