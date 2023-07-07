from django.shortcuts import render
from .models import *
from django.contrib.auth.views import logout_then_login
from .forms import *
from django.contrib import messages
from django.shortcuts import redirect
import request

# Create your views here.


def historial(request):
    if request.user.is_authenticated:
        redirect(to="login")
    compras = Venta.objects.filter(cliente=request.user)
    return render(request, "core/historial.html", {"compras":compras})


def detalle(request, id):
    try:
        venta = Venta.objects.get(id=id)
        detalles = DetalleVenta.objects.filter(venta=venta)
    except Venta.DoesNotExist:
        detalles = None
    return render(request, "core/detalle.html", {"detalles": detalles})
    
    
def comprar(request):
    if not request.user.is_authenticated:
        return redirect(to="login")
    carro = request.session.get("carro", [])
    total = 0
    for item in carro:
        total += item[5]
    venta = Venta()
    venta.cliente = request.user
    venta.total = total
    venta.save()
    for item in carro:
        detalle = DetalleVenta()
        producto = Producto.objects.get(codigo= item[0])
        detalle.producto = producto
        detalle.precio = item[3]
        detalle.cantidad = item[4]
        detalle.venta = venta
        detalle.save()
        
        producto.stock -= item[4]
        producto.save()
        
        request.session["carro"] = []
    return redirect(to="carrito")

def carrito(request):
    return render(request, 'core/carrito.html', {"carro":request.session.get("carro", [])})

def dropitem(request, codigo):
    carro = request.session.get("carro", [])
    for item in carro:
        if item[0] == codigo:
            if item[4] > 1:
                item[4] -= 1
                item[5] = item[3] * item [4]
                break
            else:
                carro.remove(item)
    request.session["carro"] = carro
    return redirect (to="carrito")

def addtocar(request, codigo):
    producto = Producto.objects.get(codigo=codigo)
    carro = request.session.get("carro", [])
    for item in carro:
        if item[0] == codigo:
            item[4] += 1
            item[5] = item[3] * item [4]
            break
    else:
        carro.append([codigo, producto.detalle, producto.imagen, producto.precio, 1, producto.precio])
    request.session["carro"] = carro
    return redirect (to="tienda")

def limpiar(request):
    request.session.flush()
    return redirect(to="home")

def home(request):
    comida = Producto.objects.all()
    return render(request, 'core/index.html', {'producto':comida, "carro":request.session.get("carro", [])})

def logout(request):
    return logout_then_login(request, login_url="home")

def registro(request):
    if request.method == "POST":
        form = Registro(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:        
        form = Registro()
    return render(request, 'core/registro.html', {'form':form})

def tienda(request):
    comida = Producto.objects.all()
    return render(request, 'core/tienda.html', {'producto':comida})

def nosotros(request):
    return render(request, 'core/nosotros.html')

def contacto(request):
    return render(request, 'core/contacto.html')

def suscribir(request): 
    context = {}

    if request.method == "POST":
       if request.user.is_authenticated:
        resp = request.get(f"http://127.0.0.1:8000/api/suscribir/{request.user,email}")
        context["mensaje"] = resp.json()["mensaje"]
        suscrito(request, context)
        return render(request, 'core/suscripcion.html', context)
    else:   
        suscrito(request, context)
        return render(request, 'core/suscripcion.html', context)

def suscrito(request):
    if request.user.is_authenticated:
        email = request.user.email
        resp = request.get(f"http://127.0.0.1:8000/api/suscribir/{email}")
        context["suscrito"] = resp.json()["suscrito"]            