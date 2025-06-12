import django_filters
from .models import Message
from django.utils import timezone
from datetime import timedelta

class MessageFilter(django_filters.FilterSet):
    conversation = django_filters.NumberFilter(field_name='conversation__id')
    sender = django_filters.NumberFilter(field_name='sender__id')
    recipient = django_filters.NumberFilter(field_name='recipient__id')
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    last_24h = django_filters.BooleanFilter(method='filter_last_24h')

    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'recipient', 'start_date', 'end_date']

    def filter_last_24h(self, queryset, name, value):
        if value:
            return queryset.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24)
            )
        return queryset