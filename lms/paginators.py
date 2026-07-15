from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Позволяет клиенту менять размер страницы (?page_size=10)
    max_page_size = 20  # Максимальный размер страницы
