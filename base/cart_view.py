from django.shortcuts import render
#from login_view import login_required



# Create your views here.
def admin_view_cart(request):
    return render(request, 'admin/viewCart.html')


