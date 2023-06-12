from django.shortcuts import render, redirect

def root_view(request):
    return redirect('student_list')

def not_found(request, route_not_found):
    return render(request, 'notfound.html', {})