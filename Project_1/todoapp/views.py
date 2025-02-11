from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, TaskForm

from django.contrib.auth import login
from .models import Task
# Create your views here.
def index(request):
    return render(request, 'todoapp/index.html')
    # return HttpResponse("This is homepage")

# def login(request):
#     if request.method == "POST":
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             # return redirect("task_list")
#             return redirect('dashboard')
#     else:
#         form = UserRegistrationForm()
#     return render(request, "todoapp/register.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
            # return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, "todoapp/register.html", {"form": form})

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "todoapp/dashboard.html", {"tasks": tasks})
    # return HttpResponse('Login Success')
    # return HttpResponse("This is dashboard")

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, "todoapp/create_task.html", {"form": form})
@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todoapp/create_task.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
    return redirect('dashboard')