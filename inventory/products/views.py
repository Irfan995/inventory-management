from django.db.models.query import QuerySet
from django.shortcuts import render
from .serializers import ProductSerializer
from django.views.generic import ListView, View, CreateView, TemplateView
from core.models import Product
from rest_framework.views import APIView
from django.http import JsonResponse
from django.db.models import Q


# Create your views here.
class ProductListView(ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.all()


class AddProductView(TemplateView):
    template_name = 'products/add_product.html'
    queryset = Product.objects.all()


class ManageStockView(TemplateView):
    template_name = 'products/manage_stock.html'


class FetchProductList(View):
    def get(self, request):
        # From datatable pipeline function
        draw = int(request.GET.get('draw', 0))
        order_col_i = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', None)
        start_i = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 0))
        search_key = request.GET.get('search[value]', '')

        recordsTotal = Product.objects.all().count()
        products, recordsFiltered = self.get_filtered_product(start_i, length, order_col_i, order_dir, search_key)

        data = []
        for product in products:
            data.append({'id': product.id, 'product_name': product.product_name, 'product_code': product.product_code, 'unit_price': product.unit_price})

        return JsonResponse({'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsFiltered, 'data': data})

    def get_filtered_product(self, start_i, length, order_col_i, order_dir, search_key):
        """
        Parameters:
            start_i: int
                Row start index
            length: int
                Number of rows to fetch
            order_col_i: int
                Column index by which ordering will be done
            order_dir: str
                Order direction (asc or desc)
            search_key: str
                Search keyword
        """

        columns = ['id']
        order_col = columns[order_col_i]
        if order_dir == 'desc':
            order_col = '-' + order_col

        if search_key:
            products = Product.objects.filter(Q(product_name__icontains=search_key) |
                                                Q(product_code__icontains=search_key) |
                                                Q(stock_management__unit_price__icontains=search_key) |
                                                Q(stock_management__stock__icontains=search_key)).order_by(order_col)
            filter_length = products.count()
        else:
            products = Product.objects.all().order_by(order_col)
            filter_length = products.count()

        products = products[start_i:start_i+length]

        return products, filter_length