from django.shortcuts import render, redirect
import requests
from requests.exceptions import ConnectionError

def student_list(request):
    try:
        response = requests.get('http://flask-app:5000/students')
        students = response.json()
        return render(request, 'students/student_list.html', {'students': students})
    except ConnectionError as e:
        print(f'Error de conexión: {e}')
        return render(request, 'students/connection_error.html')

def create_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        age = request.POST['age']
        email = request.POST['email']

        data = {
            'name': name,
            'age': age,
            'email': email
        }

        try:
            response = requests.post('http://flask-app:5000/students', json=data)
            return redirect('student_list')
        except ConnectionError as e:
            print(f'Error de conexión: {e}')

    return render(request, 'students/create_student.html')

def edit_student(request, student_id):
    try:
        if request.method == 'GET':
            response = requests.get(f'http://flask-app:5000/students/{student_id}')

            if response.status_code == 200:
                student = response.json()
                return render(request, 'students/edit_student.html', {'student': student})
            else:
                return redirect('student_list')

        elif request.method == 'POST':
            name = request.POST.get('name')
            age = request.POST.get('age')
            email = request.POST.get('email')

            data = {
                'name': name,
                'age': age,
                'email': email
            }

            response = requests.put(f'http://flask-app:5000/students/{student_id}', json=data)

            if response.status_code == 200:
                return redirect('student_list')
            else:
                return redirect('student_list')
    except ConnectionError as e:
        print(f'Error de conexión: {e}')

    return redirect('student_list')

def delete_student(request, student_id):
    try:
        response = requests.delete(f'http://flask-app:5000/students/{student_id}')
        if response.status_code == 200:
            return redirect('student_list')
        else:
            return redirect('student_list')

    except ConnectionError as e:
        print(f'Error de conexión: {e}')
