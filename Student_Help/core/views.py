from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Post,Logement, Transport, Stage, Evenement, Recommandation, Commentaire, Like,Notification, Report, User, SiteSettings

from django.shortcuts import render, redirect
from .forms import LogementForm, TransportForm, StageForm, EvenementForm, RecommandationForm,CommentForm, ReportForm, ReportStatusForm, UserProfileForm


from django.views.generic import ListView,DeleteView,UpdateView,DetailView,View


from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


from django.shortcuts import render, redirect
from .forms import CommentForm



from django.urls import reverse
import json

from .decorators import staff_required




@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Commentaire, id=comment_id)

    if comment.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    comment.delete()
    return redirect('dashboard')


@login_required
def update_profile(request):
    # Retrieve the current user from the session
    profile_user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile_user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after updating
    else:
        form = UserProfileForm(instance=profile_user)
    return render(request, 'pages/update_profile.html', {'form': form, 'profile_user': profile_user})


def mark_all_notifications_as_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, f'Your Notfifications has been marked as read.')
        return redirect('dashboard')

    else:
        return JsonResponse({'error': 'User not authenticated'})

@staff_required
def user_update(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('modcp_users')  
    else:
        form = UserRegisterForm(instance=user)
    
    return render(request, 'modcp/update_user.html', {'form': form, 'user': user})

@staff_required
def update_report_status(request, report_id):
    report = Report.objects.get(id=report_id)
    if request.method == 'POST':
        form = ReportStatusForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return redirect('modcp_reports')
            
@staff_required
def modcp_reports(request):
    reports = Report.objects.all()  
    form = ReportStatusForm()  
    return render(request, 'modcp/reports.html', {'reports': reports, 'form': form})

@staff_required
def modcp_dashboard(request):
    users = User.objects.all()  
    reports = Report.objects.all()  

    site_settings = SiteSettings.objects.first()

    if request.method == 'POST':
        site_settings.registration_open = not site_settings.registration_open
        site_settings.save()
        return redirect('modcp_dashboard') 

    context = {
        'users': users,
        'reports': reports,
        'site_settings': site_settings,
    }
    return render(request, 'modcp/dashboard.html', context)


@staff_required
def modcp_users(request):
    users = User.objects.all()  
    form = UserRegisterForm()  
    return render(request, 'modcp/users.html', {'users': users, 'form': form})


def report_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            description = form.cleaned_data['description']
            # Set the reporter to the current authenticated user
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            messages.success(request, f'Your Report has been Sent successfully.')
            return redirect('dashboard')


    
def fetch_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user,is_read=False)
        notifications_data = [{'message': notification.message, 'link': notification.link} for notification in notifications]
        return JsonResponse({'notifications': notifications_data})
    else:
        return JsonResponse({'error': 'User not authenticated'})


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'  
    context_object_name = 'post'


class PostWithCommentDetailView(DetailView):
    model = Post
    template_name = 'components/postwithcomment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_id = self.kwargs.get('comment_id')
        context['comment'] = Commentaire.objects.get(id=comment_id)
        return context



# class PostWithCommentDetailView(DetailView):
#     model = Commentaire
#     template_name = 'components/post.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         post_id = self.kwargs.get('post_id')
#         comment_id = self.kwargs.get('comment_id')
#         comment = Commentaire.objects.get(id=comment_id)
#         context['post'] = comment.post
#         context['comment'] = comment
#         return context

# def create_comment(request, post_id):
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.author = request.user
#             comment.post_id = post_id
#             comment.save()
#             return redirect('dashboard')  


def create_comment(request, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post_id = post_id
            comment.save()
            cid = comment.id
            post = Post.objects.get(pk=post_id)
            commenter = request.user
            message = f"{commenter.username} commented on your post: {comment.content}"
            create_notification_for_comment(post, commenter, message,cid)
            messages.success(request, f'Your comment has been added successfully.')
            return redirect('dashboard')

def create_notification_for_Like(post, commenter, message):
    Notification.objects.create(
        user=post.creator, 
        message=message, 
        link=f"/post/{post.id}/"
    )

def create_notification_for_comment(post, commenter,message,cid):
    #if commenter != post.creator:  # Disabled for now 
        Notification.objects.create(user=post.creator, message=message, link=f"/post/{post.id}/comment/{cid}")



@csrf_exempt
def like_post(request):
    if request.method == 'POST' and request.user.is_authenticated:
        post_id = request.POST.get('post_id')
        user = request.user
        try:
            like = Like.objects.get(user=user, post_id=post_id)
            like.delete()
            return JsonResponse({'success': True, 'action': 'unliked'})
        except Like.DoesNotExist:
            Like.objects.create(user=user, post_id=post_id)
            post = Post.objects.get(id=post_id)
            create_notification_for_Like(post, user, f"{user.username} liked your post.")
            return JsonResponse({'success': True, 'action': 'liked'})
    return JsonResponse({'success': False})

# @csrf_exempt
# def like_post(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         post_id = request.POST.get('post_id')
#         user = request.user        
#         try:
#             like = Like.objects.get(user=user, post_id=post_id)
#             like.delete()
            


#             return JsonResponse({'success': True, 'action': 'unliked'})
#         except Like.DoesNotExist:
#             Like.objects.create(user=user, post_id=post_id)

#             return JsonResponse({'success': True, 'action': 'liked'})
#     return JsonResponse({'success': False})

# def like_post(request):
#     if request.method == 'POST':
#         post_id = request.POST.get('post_id')
#         post = get_object_or_404(Post, pk=post_id)
#         user = request.user
#         # Check if the user has already liked the post
#         already_liked = Like.objects.filter(user=user, post=post).exists()
#         if already_liked:
#             # Unlike the post
#             Like.objects.filter(user=user, post=post).delete()
#         else:
#             # Like the post
#             Like.objects.create(user=user, post=post)
#         # Get the updated like count for the post
#         likes_count = post.likes.count()
#         return JsonResponse({'success': True, 'likes_count': likes_count})
#     else:
#         return JsonResponse({'success': False})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    success_url = reverse_lazy('dashboard')  

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if hasattr(post, 'recommandation'):
            return post.recommandation
        elif hasattr(post, 'transport'):
            return post.transport
        elif hasattr(post, 'stage'):
            return post.stage
        elif hasattr(post, 'evenement'):
            return post.evenement
        elif hasattr(post, 'logement'):
            return post.logement
        else:
            return None

    def get_form_class(self):
        post = self.object
        if hasattr(post, 'recommandation'):
            return RecommandationForm
        elif hasattr(post, 'transport'):
            return TransportForm
        elif hasattr(post, 'stage'):
            return StageForm
        elif hasattr(post, 'evenement'):
            return EvenementForm
        elif hasattr(post, 'logement'):
            return LogementForm
        else:
            return None


    # def get_object(self, queryset=None):
    #     post = super().get_object(queryset)
    #     if post.recommandation:
    #         return post.recommandation
    #     elif post.transport:
    #         return post.transport
    #     elif post.stage:
    #         return post.stage
    #     elif post.evenement:
    #         return post.evenement
    #     elif post.logement:
    #         return post.logement
    #     else:
    #         return None

    # def get_form_class(self):
    #     post = self.object
    #     if post.recommandation:
    #         return RecommandationForm
    #     elif post.transport:
    #         return TransportForm
    #     elif post.stage:
    #         return StageForm
    #     elif post.evenement:
    #         return EvenementForm
    #     elif post.logement:
    #         return LogementForm
    #     else:
    #         return None

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(creator=self.request.user)


# class PostUpdateView(LoginRequiredMixin, UpdateView):
#     model = Post
#     fields = ['title', 'description', 'image']  # Specify the fields you want to allow users to edit
#     success_url = reverse_lazy('dashboard')  # URL to redirect after successful update

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if self.object.creator == self.request.user:
#             return super().get(request, *args, **kwargs)
#         else:
#             return HttpResponseForbidden("You are not allowed to edit this post.")

#     def form_valid(self, form):
#         form.instance.creator = self.request.user  # Set the creator of the post to the current user
#         return super().form_valid(form)



class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.creator == self.request.user:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You are not allowed to delete this post.")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.creator == self.request.user:
            return super().delete(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You are not allowed to delete this post.")



class PostListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard.html'
    context_object_name = 'posts'
    form_class = CommentForm  


    def get_queryset(self):
        queryset = Post.objects.select_related('logement', 'transport', 'stage', 'evenement', 'recommandation').order_by('-created_at')
        user = self.request.user
        for post in queryset:
            post.is_liked = post.is_liked_by_user(user)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = self.form_class()  
        context['report_form'] = ReportForm()  

        return context

def get_liked_status(request, post_id):
    if request.method == 'GET':
        try:
            post = Post.objects.get(pk=post_id)
            user = request.user
            if user.is_authenticated:
                is_liked = post.is_liked_by_user(user)
                return JsonResponse({'success': True, 'is_liked': is_liked})
            else:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


# class PostListView(ListView):
#     template_name = 'dashboard.html'
#     context_object_name = 'posts'

#     def get_queryset(self):

#         #return Post.objects.select_related('logement', 'transport', 'stage', 'evenement', 'recommandation').all()
#         return Post.objects.select_related('logement', 'transport', 'stage', 'evenement', 'recommandation').order_by('-created_at')


def create_post(request):
    form_type = request.GET.get('type')  

    if request.method == 'POST':
        if form_type == 'logement':
            form = LogementForm(request.POST, request.FILES)
        elif form_type == 'transport':
            form = TransportForm(request.POST, request.FILES)
        elif form_type == 'stage':
            form = StageForm(request.POST, request.FILES)
        elif form_type == 'evenement':
            form = EvenementForm(request.POST, request.FILES)
        elif form_type == 'recommandation':
            form = RecommandationForm(request.POST, request.FILES)
        else:
            return render(request, 'components/create_post.html', {'error': 'Invalid form type'})

        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()

            # Additional logic for specific post types (optional)
            # ...
            messages.success(request, f'Your post has been created successfully.')
            return redirect('dashboard')
        else:
            return render(request, 'components/create_post.html', {'form': form})

    # Initialize the form based on the selected form type
    form = {
        'logement': LogementForm(),
        'transport': TransportForm(),
        'stage': StageForm(),
        'evenement': EvenementForm(),
        'recommandation': RecommandationForm()
    }.get(form_type)

    # If form_type is missing or invalid, handle it gracefully
    if not form:
        return render(request, 'components/create_post.html', {'error': 'Please select a form type'})

    return render(request, 'components/create_post.html', {'form': form})


# def create_post(request):
#     if request.method == 'POST':
#         # Check for hidden form field indicating post type
#         if 'logement' in request.POST:
#             form = LogementForm(request.POST)
#         elif 'transport' in request.POST:
#             form = TransportForm(request.POST)
#         elif 'stage' in request.POST:
#             form = StageForm(request.POST)
#         elif 'evenement' in request.POST:
#             form = EvenementForm(request.POST)
#         elif 'recommandation' in request.POST:
#             form = RecommandationForm(request.POST)
#         else:
#             # Handle invalid or missing form type
#             return render(request, 'components/create_post.html', {'error': 'Invalid form type'})

#         if form.is_valid():
#             # Save the form data to the database (common for all types)
#             post = form.save(commit=False)
#             post.creator = request.user  # Assuming user is authenticated
#             post.save()

#             # Additional logic for specific post types (optional)
#             if isinstance(post, Logement):
#                 # Do something specific for Logement posts
#                 pass
#             elif isinstance(post, Transport):
#                 # Do something specific for Transport posts
#                 pass
#             elif isinstance(post, stage):
#                 # Do something specific for Transport posts
#                 pass
#             elif isinstance(post, evenement):
#                 # Do something specific for Transport posts
#                 pass
#             elif isinstance(post, recommandation):
#                 # Do something specific for Transport posts
#                 pass
#             return redirect('home')  #replace this with a notification in the headaer
#         else:
#             return render(request, 'components/create_post.html', {'form': form})

#     form_dict = {'logement': LogementForm(), 'transport': TransportForm(),
#                  'stage': StageForm(), 'evenement': EvenementForm(),
#                  'recommandation': RecommandationForm()}
#     form = form_dict.get(request.GET.get('type'))  # Allow GET param to pre-select form type (optional)
#     if not form:
#         form = "null"  # Set default form (optional)
#     return render(request, 'components/create_post.html', {'form': form})


def  home(request):
    return render (request, 'home.html')

@login_required
def Dashboard(request):
    return render(request, 'dashboard.html')
  

def  layout(request):
    return render (request, 'layout.html')

@login_required
def  profile(request):
    return render (request, 'pages/myprofile.html')

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'profile_user': user,
        'last_login': user.last_login,
        'joined_date': user.date_joined,
    }
    return render(request, 'pages/profile.html', context)

def register(request):
    site_settings = SiteSettings.objects.first()
    if site_settings and getattr(site_settings, 'registration_open', True):
        if request.method == "POST":
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Hi {username}, your account was created successfully')
                return redirect('dashboard')
        else:
            form = UserRegisterForm()

        return render(request, 'registration/register.html', {'form': form})
    else:
        return HttpResponseForbidden("You are not authorized to access this page, Registration has been temporary Disabled.");

def  login(request):
    return render (request, 'registration/login.html')

