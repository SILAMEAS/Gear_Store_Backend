from rest_framework.pagination import (PageNumberPagination)
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    page_query_param = 'page'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'hasNext': self.page.has_next(),
            'page': self.page.number,
            'total': self.page.paginator.count,
            'contents': data,
            'totalPages': self.page.paginator.num_pages,
            'pageSize': self.page.paginator.per_page,  # Corrected this
        })

    # pagination_class = LimitOffsetPagination    # http://localhost:8000/products/?limit=2&offset=8