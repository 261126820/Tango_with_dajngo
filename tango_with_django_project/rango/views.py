from django.shortcuts import render
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import HttpResponse


def show_category(request, category_name_slug):
    # 创建上下文字典，稍后传给模板渲染引擎
    context_dict = {}
    try:
        # 能通过传入的分类别名找到对应的分类吗？
        # 如果找不到，.get() 方法抛出 DoesNotExist 异常
        # 因此 .get() 方法返回一个模型实例或抛出异常
        category = Category.objects.get(slug=category_name_slug)
        # 检索关联的所有网页
        # 注意，filter() 返回一个网页对象列表或空列表
        pages = Page.objects.filter(category=category)
        # 把得到的列表赋值给模板上下文中名为 pages 的键
        context_dict['pages'] = pages
        # 也把从数据库中获取的 category 对象添加到上下文字典中
        # 我们将在模板中通过这个变量确认分类是否存在
        context_dict['category'] = category
    except Category.DoesNotExist:
        # 没找到指定的分类时执行这里
        # 什么也不做
        # 模板会显示消息，指明分类不存在
        context_dict['category'] = None
        context_dict['pages'] = None
    # 渲染响应，返回给客户端
    return render(request, 'rango/category.html', context_dict)
    
def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context_dict)
    return response

def back_main(request):
    return render(request, 'rango/index.html', {})

def about(request):
    print(request.method)
    print(request.user)
    # return HttpResponse("Abouuuuuuuuuuuuut!")
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    return render(request, 'rango/about.html', {})

def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
    # Have we been provided with a valid form?
    if form.is_valid():
        # Save the new category to the database.
        form.save(commit=True)
        # Now that the category is saved
        # We could give a confirmation message
        # But since the most recent category added is on the index page
        # Then we can direct the user back to the index page.
        return index(request)
    else:
        # The supplied form contained errors -
        # just print them to the terminal.
        print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request):
    form = PageForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = PageForm(request.POST)
    # Have we been provided with a valid form?
    if form.is_valid():
        # Save the new category to the database.
        form.save(commit=True)
        # Now that the category is saved
        # We could give a confirmation message
        # But since the most recent category added is on the index page
        # Then we can direct the user back to the index page.
        return index(request)
    else:
        # The supplied form contained errors -
        # just print them to the terminal.
        print(form.errors)

    return render(request, 'rango/add_page.html', {'form': form})

def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and
            # put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            # Now we save the UserProfile model instance.
            profile.save()
            # Update our variable to indicate that the template
            # registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()
    # Render the template depending on the context.
    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html')


@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


# Use the login_required() decorator to ensure only those logged in can
# access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))


# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


# Updated the function definition
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits
                

