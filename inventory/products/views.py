from django.db.models.query import QuerySet
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import ProductSerializer, ProductTypeSerializer
from django.views.generic import ListView, View, CreateView, TemplateView
from core.models import Product, ProductManagement, ProductType, StockManagement
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q
import strings
from checkdigit import isbn


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


class ProductTypeListView(ListView):
    template_name = 'products/product_type_list.html'
    context_object_name = 'product_types'

    def get_queryset(self):
        return ProductType.objects.all()


class ProductList(APIView):
    permission_classes = []

    def post(self, request):
        code = request.POST.get('code')
        name = request.POST.get('name')
        category = request.POST.get('category')
        type = request.POST.get('type')
        unit_price = request.POST.get('unit_price')
        size_list = request.POST.getlist('size_list[]', None)

        if code:
            if not Product.objects.filter(product_code=code):
                product = Product.objects.create(
                    product_code=code,
                    product_name=name,
                    category=category,
                    type=ProductType.objects.get(id=type)
                )

                for size in size_list:
                    StockManagement.objects.create(
                        product=product,
                        size=size,
                        unit_price=unit_price
                    )

                data = {
                    'status': status.HTTP_201_CREATED
                }
            else:
                data = {
                    'status': status.HTTP_409_CONFLICT
                }
        else:
            data = {
                'status': status.HTTP_400_BAD_REQUEST
            }

        return JsonResponse(data, safe=False)

    def get(self, request):
        # From datatable pipeline function
        draw = int(request.GET.get('draw', 0))
        order_col_i = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', None)
        start_i = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 0))
        search_key = request.GET.get('search[value]', '')

        recordsTotal = Product.objects.all().count()
        products, recordsFiltered = self.get_filtered_product(
            start_i, length, order_col_i, order_dir, search_key)

        data = []
        for product in products:
            data.append({'id': product.id, 'product_name': product.product_name, 'type': product.type.type_name, 'category': product.category,
                        'product_code': product.product_code, 'stock': product.total_stock, 'unit_price': product.unit_price})

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

        columns = ['product_name', 'product_code', 'unit_price', 'total_stock']
        order_col = columns[order_col_i]
        if order_dir == 'desc':
            order_col = '-' + order_col

        if search_key:
            products = Product.objects.filter(Q(product_name__icontains=search_key) |
                                              Q(product_code__icontains=search_key) |
                                              Q(unit_price__icontains=search_key) |
                                              Q(total_stock__icontains=search_key)).distinct().order_by(order_col)
            filter_length = products.count()
        else:
            products = Product.objects.all().order_by(order_col)
            filter_length = products.count()

        products = products[start_i:start_i+length]

        return products, filter_length


class ProductTypeList(APIView):
    permission_classes = []

    def post(self, request):
        type_name = request.POST.get('type_name')

        if type_name:
            if not ProductType.objects.filter(type_name=type_name).exists():
                ProductType.objects.create(
                    type_name=type_name
                )
                data = {
                    'status': status.HTTP_201_CREATED
                }

            else:
                data = {
                    'status': status.HTTP_409_CONFLICT
                }
        else:
            data = {
                'status': status.HTTP_400_BAD_REQUEST
            }

        return JsonResponse(data, safe=False)

    def get(self, request):
        # From datatable pipeline function
        draw = int(request.GET.get('draw', 0))
        order_col_i = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', None)
        start_i = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 0))
        search_key = request.GET.get('search[value]', '')

        recordsTotal = ProductType.objects.all().count()
        product_types, recordsFiltered = self.get_filtered_product_type(
            start_i, length, order_col_i, order_dir, search_key)

        data = []
        for product_type in product_types:
            if Product.objects.filter(type=product_type.id).exists():
                product = Product.objects.get(type=product_type.id)
                if StockManagement.objects.filter(product=product).exists():
                    stock_managements = StockManagement.objects.filter(
                        product=product)
                    stock = 0
                    sold = 0
                    for stock_management in stock_managements:
                        stock += stock_management.stock
                        sold += stock_management.sold
            else:
                stock = 0
                sold = 0

            data.append(
                {'id': product_type.id, 'type_name': product_type.type_name, 'stock': stock, 'sold': sold})

        return JsonResponse({'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsFiltered, 'data': data})

    def get_filtered_product_type(self, start_i, length, order_col_i, order_dir, search_key):
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
            product_types = ProductType.objects.filter(Q(product_name__icontains=search_key) |
                                                       Q(product_code__icontains=search_key) |
                                                       Q(stock_management__unit_price__icontains=search_key) |
                                                       Q(stock_management__stock__icontains=search_key)).order_by(order_col)
            filter_length = product_types.count()
        else:
            product_types = ProductType.objects.all().order_by(order_col)
            filter_length = product_types.count()

        product_types = product_types[start_i:start_i+length]

        return product_types, filter_length


class FetchProductType(APIView):
    permission_classes = []

    def get(self, request):
        types = ProductType.objects.all()
        serializer = ProductTypeSerializer(types, many=True)

        return JsonResponse(serializer.data, safe=False)


class FetchProductCode(APIView):
    permission_classes = []

    def get(self, request):
        term = request.GET.get('term')

        if term:
            if term.isdigit():
                products = Product.objects.filter(product_code=term)
            else:
                return JsonResponse({'status': status.HTTP_404_NOT_FOUND})
        else:
            products = Product.objects.all()

        data = []
        for product in products:
            data.append(
                {'id': product.id, 'product_code': product.product_code})

        return JsonResponse(data, safe=False)


class FetchProductInformation(APIView):
    permission_classes = []

    def get(self, request):
        product_code = request.GET.get('product_code')

        if product_code:
            if Product.objects.filter(product_code=product_code).exists():
                product = Product.objects.get(product_code=product_code)
                product_name = product.product_name
                category = product.category
                type = product.type.type_name
                size_list = []
                stock_managements = StockManagement.objects.filter(
                    product=product)
                for stock_management in stock_managements:
                    size_list.append(stock_management.size)
                data = {
                    'product_name': product_name,
                    'category': category,
                    'type': type,
                    'size_list': size_list,
                    'status': status.HTTP_200_OK
                }
            else:
                data = {
                    'status': status.HTTP_404_NOT_FOUND
                }
        else:
            data = {
                'status': status.HTTP_400_BAD_REQUEST
            }

        return JsonResponse(data, safe=False)


class AddProductStock(APIView):
    permission_classes = []

    def post(self, request):
        product_code = request.POST.get('product_code')
        size = request.POST.get('size')
        quantity = request.POST.get('quantity')

        if product_code:
            product = Product.objects.get(product_code=product_code)
            if StockManagement.objects.filter(product=product.id, size=size).exists():
                asset = product.asset
                total_stock = product.total_stock
                product.asset = asset + int(quantity)
                product.total_stock = total_stock + int(quantity)
                product.save()

                stock_management = StockManagement.objects.get(product=product.id, size=size)
                stock = stock_management.stock
                stock_management.stock = stock + int(quantity)
                stock_management.save()

                for i in range(1, int(quantity)+1):
                    index = int(asset) + i
                    if index < 10:
                        product_unit_code = '000' + str(index)
                    elif index < 100:
                        product_unit_code = '00' + str(index)
                    elif index < 1000:
                        product_unit_code = '0' + str(index)
                    elif index < 10000:
                        product_unit_code = str(index)
                    else:
                        print('Code limit exceed') 
                    
                    stock_keeping_unit = strings.COUNTRY_CODE + '00' + product_code + product_unit_code
                    check_digit = isbn.calculate(stock_keeping_unit)
                    bar_code = stock_keeping_unit + check_digit
                    
                    ProductManagement.objects.create(
                        product=product,
                        stock_keeping_unit=stock_keeping_unit,
                        bar_code=bar_code
                    )
                data ={
                    'status': status.HTTP_201_CREATED
                }
            else:
                data = {
                    'status': status.HTTP_404_NOT_FOUND
                }
        else:
            data = {
                'status': status.HTTP_400_BAD_REQUEST
            }

            
        return JsonResponse(data, safe=False)
