from django.shortcuts import render


# Create your views here.
def admin_view_feedback(request):
    return render(request, 'admin/viewFeedback.html')
