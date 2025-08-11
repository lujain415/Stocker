from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from datetime import timedelta
from django.db.models import Count, Sum, F, Q
import json
from .models import Product, Category, Supplier
from .forms import SupplierForm


def is_admin(user):
    return user.is_staff or user.is_superuser

#-----PRODUCT-----

@login_required
def create_product_view(request: HttpRequest):
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        try:
            price_value = request.POST.get("price") or "0"
            new_product = Product(
                name=request.POST["name"],
                description=request.POST["description"],
                quantity=request.POST["quantity"],
                price=Decimal(price_value),
                expiry_date=request.POST.get("expiry_date"),
                category=Category.objects.get(id=request.POST["category"]),
                image=request.FILES.get("image")
            )
            new_product.save()
            new_product.suppliers.set(request.POST.getlist("suppliers"))
            messages.success(request, "Product created successfully", "alert-success")
            return redirect("inventory:all_products_view")
        except Exception as e:
            print("Error:", e)
            messages.error(request, "Failed to create product", "alert-danger")

    return render(request, "inventory/create_product.html", {
        "categories": categories,
        "suppliers": suppliers
    })


def product_detail_view(request: HttpRequest, product_id: int):
    product = Product.objects.get(id=product_id)
    return render(request, "inventory/product_detail.html", {"product": product})


@login_required
def update_product_view(request: HttpRequest, product_id: int):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        product.name = request.POST["name"]
        product.description = request.POST["description"]
        product.quantity = request.POST["quantity"]
        product.price = Decimal(request.POST.get("price") or "0")
        product.expiry_date = request.POST.get("expiry_date")
        product.category = Category.objects.get(id=request.POST["category"])
        if "image" in request.FILES:
            product.image = request.FILES["image"]
        product.save()
        product.suppliers.set(request.POST.getlist("suppliers"))
        messages.success(request, "Product updated successfully", "alert-success")
        return redirect("inventory:product_detail_view", product_id=product.id)

    return render(request, "inventory/update_product.html", {
        "product": product,
        "categories": categories,
        "suppliers": suppliers
    })


@user_passes_test(is_admin)
def delete_product_view(request: HttpRequest, product_id: int):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can delete products", "alert-warning")
        return redirect("main:home_view")

    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, "Product deleted successfully", "alert-success")
    except:
        messages.error(request, "Failed to delete product", "alert-danger")

    return redirect("inventory:all_products_view")


def all_products_view(request):
    products_qs = Product.objects.all().order_by('-id')

    total_products = low_stock_count = out_of_stock_count = available_count = 0
    if request.user.is_superuser:
        total_products = products_qs.count()
        low_stock_count = products_qs.filter(
            quantity__lt=F('low_stock_threshold'),
            quantity__gt=0
        ).count()
        out_of_stock_count = products_qs.filter(quantity=0).count()
        available_count = products_qs.filter(
            quantity__gte=F('low_stock_threshold')
        ).count()

    top_products = products_qs.order_by('-quantity')[:5]
    pie_labels = [p.name for p in top_products]
    pie_values = [p.quantity for p in top_products]

    paginator = Paginator(products_qs, 6)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'products': products_page,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'available_count': available_count,
        'pie_labels': mark_safe(json.dumps(pie_labels)),
        'pie_values': mark_safe(json.dumps(pie_values)),
    }
    return render(request, 'inventory/all_products.html', context)


def search_products_view(request: HttpRequest):
    query = request.GET.get("search", "")
    products = []

    if len(query) >= 3:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(suppliers__name__icontains=query)
        ).distinct()

    return render(request, "inventory/search_products.html", {"products": products})

#-----CATAGORY-----

def list_categories_view(request: HttpRequest):
    categories = Category.objects.all()
    return render(request, "inventory/categories_list.html", {"categories": categories})


def create_category_view(request: HttpRequest):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can add categories", "alert-warning")
        return redirect("inventory:list_categories_view")

    if request.method == "POST":
        try:
            Category.objects.create(name=request.POST["name"])
            messages.success(request, "Category created successfully", "alert-success")
            return redirect("inventory:list_categories_view")
        except Exception as e:
            print(e)
            messages.error(request, "Failed to create category", "alert-danger")

    return render(request, "inventory/create_category.html")


def update_category_view(request: HttpRequest, category_id: int):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can update categories", "alert-warning")
        return redirect("inventory:list_categories_view")

    category = Category.objects.get(id=category_id)

    if request.method == "POST":
        try:
            category.name = request.POST["name"]
            category.save()
            messages.success(request, "Category updated successfully", "alert-success")
            return redirect("inventory:list_categories_view")
        except Exception as e:
            print(e)
            messages.error(request, "Failed to update category", "alert-danger")

    return render(request, "inventory/update_category.html", {"category": category})


def delete_category_view(request: HttpRequest, category_id: int):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can delete categories", "alert-warning")
        return redirect("inventory:list_categories_view")

    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, "Category deleted successfully", "alert-success")
    except Exception as e:
        print(e)
        messages.error(request, "Failed to delete category", "alert-danger")

    return redirect("inventory:list_categories_view")

#-----SUPPLIERS-----

def list_suppliers_view(request: HttpRequest):
    suppliers = Supplier.objects.all()
    return render(request, "inventory/suppliers_list.html", {"suppliers": suppliers})



def create_supplier_view(request: HttpRequest):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can add suppliers", "alert-warning")
        return redirect("inventory:list_suppliers_view")

    if request.method == "POST":
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier created successfully", "alert-success")
            return redirect("inventory:list_suppliers_view")
    else:
        form = SupplierForm()

    return render(request, "inventory/create_supplier.html", {"form": form})

def update_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("inventory:list_suppliers_view")
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'inventory/update_supplier.html', {'form': form})

def delete_supplier_view(request: HttpRequest, supplier_id: int):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can delete suppliers", "alert-warning")
        return redirect("inventory:list_suppliers_view")

    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.delete()
        messages.success(request, "Supplier deleted successfully", "alert-success")
    except Exception as e:
        print(e)
        messages.error(request, "Failed to delete supplier", "alert-danger")

    return redirect("inventory:list_suppliers_view")


def supplier_detail_view(request: HttpRequest, supplier_id: int):
    supplier = Supplier.objects.get(id=supplier_id)
    products = Product.objects.filter(suppliers=supplier)
    return render(request, "inventory/supplier_detail.html", {
        "supplier": supplier,
        "products": products
    })

#-----STOCK-----

def update_stock_view(request: HttpRequest, product_id: int):
    product = Product.objects.get(id=product_id)

    if not request.user.is_authenticated:
        return redirect("accounts:sign_in")

    if request.method == "POST":
        try:
            if request.POST.get("set_quantity", "").strip() != "":
                product.quantity = int(request.POST["set_quantity"])

            if request.POST.get("change_by", "").strip() != "":
                delta = int(request.POST["change_by"])
                product.quantity = max(0, product.quantity + delta)

            low_stock_value = request.POST.get("low_stock_threshold")
            if low_stock_value is not None and low_stock_value.strip() != "":
                product.low_stock_threshold = max(0, int(low_stock_value))

            product.save()
        except Exception as e:
            print("Stock update error:", e)

        return redirect("inventory:product_detail_view", product_id=product.id)

    return render(request, "inventory/update_stock.html", {"product": product})


def stock_status_view(request: HttpRequest):
    today = timezone.localdate()
    expiring_days = int(request.GET.get("expiring_days", 30))

    low_stock_products = Product.objects.filter(quantity__lte=F('low_stock_threshold')).order_by("quantity")
    expired_products = Product.objects.filter(expiry_date__isnull=False, expiry_date__lt=today).order_by("expiry_date")
    expiring_soon_products = Product.objects.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=expiring_days)
    ).order_by("expiry_date")

    return render(request, "inventory/stock_status.html", {
        "low_stock_products": low_stock_products,
        "expired_products": expired_products,
        "expiring_soon_products": expiring_soon_products,
        "expiring_days": expiring_days
    })


@staff_member_required
def low_stock_report_view(request):
    low_stock_products = Product.objects.filter(quantity__lte=F('low_stock_threshold'))
    for product in low_stock_products:
        send_low_stock_email(product)
    return render(request, "inventory/low_stock_report.html", {"products": low_stock_products})


@staff_member_required
def out_of_stock_view(request):
    products = Product.objects.filter(quantity=0)
    return render(request, 'inventory/out_of_stock.html', {'products': products})


def send_low_stock_email(product):
    subject = f"Low Stock Alert: {product.name}"
    message = f"The stock for product '{product.name}' is low. Only {product.quantity} left in inventory."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.MANAGER_EMAIL])


def supplier_report_view(request):
    suppliers = Supplier.objects.annotate(
        product_count=Count('product', distinct=True),
        total_qty=Sum('product__quantity')
    )
    return render(request, "inventory/supplier_reports.html", {"suppliers": suppliers})


