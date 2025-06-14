from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    """
    Custom pagination for messages with 20 items per page
    and enhanced response format
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'total_items': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next_page': self.get_next_link(),
                'previous_page': self.get_previous_link(),
                'page_size': self.get_page_size(self.request)
            },
            'results': data
        })