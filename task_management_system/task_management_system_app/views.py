from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from django.utils import timezone

from .models import Task, Category

# Create your views here.
def is_admin(user):
    return user.is_superuser

# Helper Decorator
admin_required = user_passes_test(lambda user: user.is_superuser)

# Auth views
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser:
                return redirect('category_list')

            return redirect('user_tasks_list')

    else:
        form = AuthenticationForm()

    return render(
        request,
        'task_management_system_app/login.html',
        {'form': form}
    )

@login_required
def user_tasks_list(request):
    tasks = request.user.tasks.all()
    return render(request, 'task_management_system_app/user_tasks_list.html', {'tasks': tasks})

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'task_management_system_app/register.html', {'form': form})

def LogoutPage(request):
    logout(request)
    return redirect("login")

@login_required
@admin_required
def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.delete()
    return redirect(reverse('category_list'))

# Admin Views
@login_required
@admin_required
def create_task(request):
    if request.method == 'POST':
        # retrieve data from the POST request
        category_id = request.POST.get('category')
        assigned_to_id = request.POST.get('assigned_to')

        category = get_object_or_404(Category, pk=category_id)

        Task.objects.create(
            name=request.POST.get('name'),
            category = category,
            start_date = request.POST.get('start_date'),
            end_date = request.POST.get('end_date'),
            priority = request.POST.get('priority'),
            description = request.POST.get('description'),
            location = request.POST.get('location'),
            organizer = request.POST.get('organizer'),
            assigned_to_id = int(assigned_to_id) if assigned_to_id else None
        )
        # Redirect to the task list page
        return redirect('category_list')

    categories = Category.objects.all()
    users = User.objects.all()
    return render(request, 'task_management_system_app/create_task.html', {'categories': categories, 'users': users})

@login_required
@admin_required
def update_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        # update task fields based on form data
        category_id = request.POST.get('category')
        assigned_to_id = request.POST.get('assigned_to')

        task.name = request.POST.get('name')
        task.start_date = request.POST.get('start_date')
        task.end_date = request.POST.get('end_date')
        task.priority = request.POST.get('priority')
        task.description = request.POST.get('description')
        task.location = request.POST.get('location')
        task.organizer = request.POST.get('organizer')

        if category_id:
            task.category_id = int(category_id)

        # Only update if a valid assigned_to_id was selected in the form
        if assigned_to_id:
            task.assigned_to_id = int(assigned_to_id) if assigned_to_id else None

        task.save()

        return redirect('category_list')

    # render update task page with task data
    categories = Category.objects.all()
    users = User.objects.all()
    return render(request, 'task_management_system_app/update_task.html', {'task': task, 'categories': categories, 'users': users})

@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'task_management_system_app/category_list.html', {'categories': categories})

@login_required
@admin_required
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
        return redirect('category_list')

    return render(request, 'task_management_system_app/create_category.html')

@login_required
@admin_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if category.task_set.exists():
        messages.error(request, "You cannot delete this category as it contains tasks.")
    else:
        category.delete()
        messages.success(request, "Category deleted successfully.")
    return redirect('category_list')

@login_required
@admin_required
def category_tasks(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    tasks = category.task_set.all()
    return render(request, 'task_management_system_app/category_tasks.html', {'category': category ,'tasks': tasks})

@login_required
@admin_required
def task_chart(request):
    categories = Category.objects.all()
    pending_counts = {}
    for category in categories:
        pending_counts[category.name] = Task.objects.filter(
            category=category,
            start_date__gt=timezone.now()
        ).count()
    return render(request, 'task_management_system_app/task_chart.html', {'pending_counts': pending_counts})