from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import CreateView

from .models import Product, Purchase

# Create your views here.
def index(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/index.html', context)


class PurchaseCreate(CreateView):
    model = Purchase
    fields = ['product', 'person', 'address']

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(f'Спасибо за покупку, {self.object.person}!')

from django.shortcuts import redirect, get_object_or_404
from django.contrib.sessions.models import Session
from .models import CartItem

def _get_session_key(request):
    """Возвращает session_key, создавая сессию при необходимости."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def add_to_cart(request, product_id):
    """Добавляет товар в корзину или увеличивает количество."""
    product = get_object_or_404(Product, pk=product_id)
    session_key = _get_session_key(request)
    
    item, created = CartItem.objects.get_or_create(
        session_key=session_key,
        product=product,
        defaults={'quantity': 1},
    )
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart_detail')

def cart_detail(request):
    """Показывает корзину и общее количество товаров."""
    session_key = _get_session_key(request)
    items = CartItem.objects.filter(session_key=session_key).select_related('product')
    total_quantity = sum(item.quantity for item in items)
    context = {
        'items': items,
        'total_quantity': total_quantity,
    }
    return render(request, 'shop/cart.html', context)

def remove_from_cart(request, item_id):
    """Удаляет позицию из корзины."""
    session_key = _get_session_key(request)
    item = get_object_or_404(CartItem, pk=item_id, session_key=session_key)
    item.delete()
    return redirect('cart_detail')