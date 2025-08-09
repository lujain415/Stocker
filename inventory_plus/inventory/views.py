from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from .models import Product, Category, Supplier
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .utils import notify_manager
from django.db.models import Q, F 
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
import csv
from django.http import HttpResponse
from .models import Product
from django.db.models import Count, Sum
from .models import Supplier
from django.shortcuts import redirect
import io
def is_admin(user):
    return user.is_staff or user.is_superuser
# -------PRODUCT-------

def create_product_view(request: HttpRequest):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can add products", "alert-warning")
        return redirect("main:home_view")

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        try:
            new_product = Product(
                name=request.POST["name"],
                description=request.POST["description"],
                quantity=request.POST["quantity"],
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

@user_passes_test(is_admin)
def update_product_view(request: HttpRequest, product_id: int):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can update products", "alert-warning")
        return redirect("main:home_view")

    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        product.name = request.POST["name"]
        product.description = request.POST["description"]
        product.quantity = request.POST["quantity"]
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


def all_products_view(request: HttpRequest):
    products = Product.objects.all().order_by("-created_at")
    paginator = Paginator(products, 4)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "inventory/all_products.html", {"products": page_obj})


def search_products_view(request: HttpRequest):
    query = request.GET.get("search", "")
    products = []

    if len(query) >= 3:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    return render(request, "inventory/search_products.html", {"products": products})

# -------CATAGORY-------

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

# -------SUPPLIERS-------

def list_suppliers_view(request: HttpRequest):
    suppliers = Supplier.objects.all()
    return render(request, "inventory/suppliers_list.html", {"suppliers": suppliers})


def create_supplier_view(request: HttpRequest):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can add suppliers", "alert-warning")
        return redirect("inventory:list_suppliers_view")

    if request.method == "POST":
        try:
            new_supplier = Supplier(
                name=request.POST["name"],
                email=request.POST["email"],
                phone=request.POST["phone"],
                website=request.POST.get("website", ""),
                logo=request.FILES.get("logo")
            )
            new_supplier.save()
            messages.success(request, "Supplier created successfully", "alert-success")
            return redirect("inventory:list_suppliers_view")
        except Exception as e:
            print(e)
            messages.error(request, "Failed to create supplier", "alert-danger")

    return render(request, "inventory/create_supplier.html")


def update_supplier_view(request: HttpRequest, supplier_id: int):
    if not request.user.is_staff:
        messages.warning(request, "Only admin can update suppliers", "alert-warning")
        return redirect("inventory:list_suppliers_view")

    supplier = Supplier.objects.get(id=supplier_id)

    if request.method == "POST":
        supplier.name = request.POST["name"]
        supplier.email = request.POST["email"]
        supplier.phone = request.POST["phone"]
        supplier.website = request.POST.get("website", "")
        if "logo" in request.FILES:
            supplier.logo = request.FILES["logo"]
        supplier.save()
        messages.success(request, "Supplier updated successfully", "alert-success")
        return redirect("inventory:list_suppliers_view")

    return render(request, "inventory/update_supplier.html", {"supplier": supplier})


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

def update_stock_view(request: HttpRequest, product_id: int):
    product = Product.objects.get(id=product_id)

    # Allow logged-in users to update stock (per assignment)
    if not request.user.is_authenticated:
        messages.error(request, "Only registered users can update stock", "alert-danger")
        return redirect("accounts:sign_in")

    if request.method == "POST":
        try:
            # Two options: set absolute quantity or change by delta
            if "set_quantity" in request.POST and request.POST["set_quantity"] != "":
                product.quantity = int(request.POST["set_quantity"])
            elif "change_by" in request.POST and request.POST["change_by"] != "":
                delta = int(request.POST["change_by"])
                new_qty = product.quantity + delta
                product.quantity = max(0, new_qty)

            # optional: allow updating low_stock_threshold
            if "low_stock_threshold" in request.POST and request.POST["low_stock_threshold"] != "":
                product.low_stock_threshold = int(request.POST["low_stock_threshold"])

            product.save()
            messages.success(request, "Stock updated successfully", "alert-success")
        except Exception as e:
            print(e)
            messages.error(request, "Failed to update stock", "alert-danger")

        return redirect("inventory:product_detail_view", product_id=product.id)

    return render(request, "inventory/update_stock.html", {"product": product})

# ---- Stock status / overview
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
    low_stock_products = Product.objects.filter(quantity__lte=5)
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

def export_products_csv(request):
    # تحديد نوع الملف واسم التنزيل
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    # كتابة العناوين
    writer.writerow(['Name', 'Description', 'Quantity', 'Category', 'Suppliers'])

    # كتابة البيانات
    for product in Product.objects.all():
        suppliers_names = ", ".join(s.name for s in product.suppliers.all())
        writer.writerow([product.name, product.description, product.quantity, product.category.name, suppliers_names])

    return response

def supplier_report_view(request):
    suppliers = Supplier.objects.annotate(
        product_count=Count('product', distinct=True),
        total_qty=Sum('product__quantity')
    )
    return render(request, "inventory/supplier_reports.html", {"suppliers": suppliers})

def import_products_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Invalid file format", status=400)

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)  # تخطي العناوين

        for row in csv.reader(io_string, delimiter=',', quotechar="|"):
            name, description, quantity, category_name, suppliers_names = row
            from .models import Category, Supplier
            category, _ = Category.objects.get_or_create(name=category_name)
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={'description': description, 'quantity': int(quantity), 'category': category}
            )
            if not created:
                product.description = description
                product.quantity = int(quantity)
                product.category = category
                product.save()

            supplier_list = suppliers_names.split(",")
            for supplier_name in supplier_list:
                supplier, _ = Supplier.objects.get_or_create(name=supplier_name.strip())
                product.suppliers.add(supplier)

        return redirect("inventory:product_list")

    return HttpResponse("No file uploaded", status=400)

@staff_member_required
def import_products_page(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if csv_file.name.endswith('.csv'):
            data = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(data)
            for row in reader:
                Product.objects.create(
                    name=row['name'],
                    description=row['description'],
                    quantity=int(row['quantity']),
                    price=float(row['price'])
                )
            return redirect('inventory:all_products_view')
    return render(request, 'inventory/import_products.html')