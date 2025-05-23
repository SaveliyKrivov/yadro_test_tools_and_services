import random
from django.views.generic import DetailView, ListView
from django.http import JsonResponse
from django.views.generic.edit import FormMixin

from .models import Profile
from .services import fetch_users, save_users_to_db
from .forms import ProfileCountForm


class ProfileListView(FormMixin, ListView):
    model = Profile
    ordering = "-id"
    paginate_by = 10
    template_name = "profile_list.html"
    form_class = ProfileCountForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        count = form.cleaned_data["count"]
        users_data = fetch_users(count)
        saved = save_users_to_db(users_data)
        return JsonResponse({"success": True, "saved": saved})

    def form_invalid(self, form):
        return JsonResponse(
            {
                "success": False,
                "errors": form.errors.as_json(),
                "message": "Invalid input",
            },
            status=400,
        )


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "profile_detail.html"
    context_object_name = "profile"
    pk_url_kwarg = "profile_id"


class RandomProfileView(DetailView):
    template_name = "profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        count = Profile.objects.count()
        if count == 0:
            users_data = fetch_users(1)
            save_users_to_db(users_data)
            return Profile.objects.first()

        random_id = random.randint(0, count - 1)
        return Profile.objects.all()[random_id]
