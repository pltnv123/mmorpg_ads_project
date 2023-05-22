from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from .filters import AdvertisementFilter, AdvFilter
from .models import Advertisement, Responses
from .forms import AdvertisementForm, ResponsesForm


# Create your views here.
class AdvertisementView(ListView):
    model = Advertisement
    template_name = 'Advertisement.html'
    context_object_name = 'advertisements'
    paginate_by = 10
    ordering = ['-dateCreation']

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = AdvertisementFilter(self.request.GET, queryset)

        return self.filterset.qs


class AdvertisementDetailView(DetailView):
    model = Advertisement
    template_name = 'AdvertisementPk.html'
    context_object_name = 'Adver'


class CreateAdvertisement(CreateView):  # PermissionRequiredMixin

    form_class = AdvertisementForm
    model = Advertisement
    template_name = 'CreateAdvertisement.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        print(form.instance.author)
        return super().form_valid(form)


class UpdateAdvertisement(UpdateView):
    form_class = AdvertisementForm
    model = Advertisement
    template_name = 'UpdateAdvertisement.html'


class DeleteAdvertisement(DeleteView):
    model = Advertisement
    template_name = 'DeleteAdvertisement.html'
    success_url = reverse_lazy('advertisement')


class ResponsesDetailView(DetailView):
    model = Responses
    template_name = 'ResponsesPk.html'
    context_object_name = 'Resp'
    ordering = ['-dateCreation']

    def get_object(self, queryset=None):
        advertisement = get_object_or_404(Advertisement, id=self.kwargs['pk'])
        response = get_object_or_404(Responses, id=self.kwargs['pk_res'], advertisement=advertisement)
        return response


class DeleteResponses(DeleteView):
    model = Responses
    template_name = 'DeleteResponses.html'
    success_url = '/'

    def get_object(self, queryset=None):
        advertisement = get_object_or_404(Advertisement, id=self.kwargs['pk'])
        response = get_object_or_404(Responses, id=self.kwargs['pk_res'], advertisement=advertisement)

        return response


class ResponseCreateView(CreateView):
    form_class = ResponsesForm
    model = Responses
    template_name = 'response_create.html'

    def get_success_url(self):
        advertisement_id = self.kwargs['pk']
        return reverse('advertisement_detail', kwargs={'pk': advertisement_id})

    def form_valid(self, form):
        form.instance.advertisement_id = self.kwargs['pk']
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.META.get('HTTP_REFERER')
        context['previous_url'] = previous_url
        return context

class ProfileView(ListView):
    model = Advertisement
    template_name = 'Profile.html'
    context_object_name = 'profile'
    ordering = ['-dateCreation']
    queryset = Advertisement.objects.all().select_related('author')

    def get_queryset(self):
        quaeryset = super().get_queryset()
        self.filterset = AdvFilter(self.request.GET, quaeryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

def activited_response(request, pk, pk_res):
    advertisement = get_object_or_404(Advertisement, id=pk)
    response = get_object_or_404(Responses, id=pk_res, advertisement=advertisement)
    text = response.text
    response.is_active = True
    response.save()
    previous_url = request.META.get('HTTP_REFERER')
    return render(request, 'activited_response.html', {'text': text, 'previous_url': previous_url})

def deactivited_response(request, pk, pk_res):
    advertisement = get_object_or_404(Advertisement, id=pk)
    response = get_object_or_404(Responses, id=pk_res, advertisement=advertisement)
    text = response.text
    response.is_active = False
    response.save()
    previous_url = request.META.get('HTTP_REFERER')
    return render(request, 'deactivited_response.html', {'text': text, 'previous_url': previous_url})
