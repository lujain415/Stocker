from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from .models import Product, Category, Supplier
from django.core.paginator import Paginator
from django.db.models import Q

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
