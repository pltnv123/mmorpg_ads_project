from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from .filters import AdvertisementFilter, AdvFilter
from .models import Advertisement, Responses
from .forms import AdvertisementForm, ResponsesForm
from .tasks import send_email_

# Create your views here.
class AdvertisementView(ListView):
    """
    Представление для отображения списка объявлений.
    """

    model = Advertisement
    template_name = 'Advertisement.html'
    context_object_name = 'advertisements'
    paginate_by = 30
    ordering = ['-dateCreation']

    def get_queryset(self):
        """
        Метод get_queryset возвращает отфильтрованный queryset, используя GET-параметры и класс фильтров
        AdvertisementFilter на страницу.
        """

        queryset = super().get_queryset()
        self.filterset = AdvertisementFilter(self.request.GET, queryset)

        return self.filterset.qs


class AdvertisementDetailView(DetailView):
    model = Advertisement
    template_name = 'AdvertisementPk.html'
    context_object_name = 'Adver'


class CreateAdvertisement(LoginRequiredMixin, CreateView):
    """
    Класс страницы создания объявления (Только для зарегистрированных пользователей)
    """

    form_class = AdvertisementForm
    model = Advertisement
    template_name = 'CreateAdvertisement.html'

    def form_valid(self, form):
        """
        Метод, который вызывается, когда форма прошла проверку валидации.
        Он устанавливает автора объявления используя `self.request.user` и сохраняет объявление в базе данных.
        Метод возвращает ответ успешной обработки формы.
        """

        form.instance.author = self.request.user
        print(form.instance.author)
        return super().form_valid(form)


class UpdateAdvertisement(LoginRequiredMixin, UpdateView):
    """
    Класс страницы изменения объявления (Только для залогиненого пользователя)
    """

    form_class = AdvertisementForm
    model = Advertisement
    template_name = 'UpdateAdvertisement.html'


class DeleteAdvertisement(LoginRequiredMixin, DeleteView):
    """
    Класс страницы удаления объявления (Только для зарегистрированного пользователя)
    """

    model = Advertisement
    template_name = 'DeleteAdvertisement.html'
    success_url = reverse_lazy('advertisement')


class ResponsesDetailView(DetailView):
    """
    Класс страницы описания отклика
    """
    model = Responses
    template_name = 'ResponsesPk.html'
    context_object_name = 'Resp'
    ordering = ['-dateCreation']

    def get_object(self, queryset=None):
        """
        Возвращает идентефикатор отклика  и объявления (pk, pk_res),
        который будет использоваться для отображения данных на странице.
        Метод использует GET-параметры для получения идентификаторов объявления и отклика.
        """

        advertisement = get_object_or_404(Advertisement, id=self.kwargs['pk'])
        response = get_object_or_404(Responses, id=self.kwargs['pk_res'], advertisement=advertisement)
        return response


class DeleteResponses(LoginRequiredMixin, DeleteView):
    """
    Класс удаления отлика (Для залогиненных пользователей)
    """

    model = Responses
    template_name = 'DeleteResponses.html'
    success_url = '/'

    def get_object(self, queryset=None):
        """
        Возвращает идентефикатор отклика  и объявления (pk, pk_res),
        который будет использоваться для отображения данных на странице.
        Метод использует GET-параметры для получения идентификаторов объявления и отклика.
        """

        advertisement = get_object_or_404(Advertisement, id=self.kwargs['pk'])
        response = get_object_or_404(Responses, id=self.kwargs['pk_res'], advertisement=advertisement)

        return response


class ResponseCreateView(LoginRequiredMixin, CreateView):
    """
    Класс страницы создания отклика на объявление
    """

    form_class = ResponsesForm
    model = Responses
    template_name = 'response_create.html'

    def get_success_url(self):
        """
        Метод, который возвращает URL-адрес страницы, куда пользователь будет перенаправлен после успешной отправки формы.
        Метод использует идентификатор объявления из GET-параметров для формирования URL-адреса страницы с деталями объявления.
        """

        advertisement_id = self.kwargs['pk']
        return reverse('advertisement_detail', kwargs={'pk': advertisement_id})

    def form_valid(self, form):
        """
        Метод, который вызывается, когда форма прошла проверку валидации.
        Метод устанавливает идентификатор объявления и пользователя для отклика, сохраняет отклик в базе данных
        и отправляет уведомление автору объявления.????
        """

        form.instance.advertisement_id = self.kwargs['pk']
        form.instance.user = self.request.user

        advertisement = Advertisement.objects.get(pk=self.kwargs['pk'])
        email = advertisement.author.email
        message = f"На ваше объявление \"{advertisement.heading}\" был оставлен новый отклик."
        text = 'Новый отклик на объявление'
        send_email_.delay(text, message, email)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Получение базового контекста данных.  Получение URL-адреса предыдущей страницы.
        Добавление URL-адреса предыдущей страницы в контекст данных.
        Возвращение расширенного контекста данных.
        """

        context = super().get_context_data(**kwargs)
        previous_url = self.request.META.get('HTTP_REFERER')
        context['previous_url'] = previous_url
        return context


class ProfileView(ListView):
    """
    Отображение СВОИХ постов во вкладке Профиль.
    """

    model = Advertisement
    template_name = 'Profile.html'
    context_object_name = 'profile'
    ordering = ['-dateCreation']

    def get_queryset(self):
        """
        Метод для получения списка объявлений, отфильтрованного по пользователю.
        Второй аргумент request=self.request - передается в Filters.py и обрабатывается
        методом ourBranches, после передается в AdvFilter и возвращается списком статей автора.
        """

        queryset = super().get_queryset()
        self.filterset = AdvFilter(self.request.GET, request=self.request,
                                   queryset=queryset.filter(author=self.request.user))
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        """
        Метод для получения контекста данных, который будет передан в шаблон.

        Методы get_queryset и get_context_data в классе связаны между собой,
        поскольку get_queryset фильтрует список объявлений и создает экземпляр фильтра объявлений,
        который затем передается в get_context_data в качестве атрибута filterset.
        """
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        print(self.filterset)
        print(self.filterset.qs)
        return context


def activited_response(request, pk, pk_res):
    """
    Принимает отклик на объявление и отправляет уведомление на email пользователю, который оставил отклик.

    :param request: объект запроса Django
    :param pk: первичный ключ объявления
    :param pk_res: первичный ключ отклика
    :return: объект ответа Django, который отображает шаблон 'activited_response.html'
    """

    advertisement = get_object_or_404(Advertisement, id=pk)
    response = get_object_or_404(Responses, id=pk_res, advertisement=advertisement)
    text = response.text
    response.is_active = True
    response.save()
    previous_url = request.META.get('HTTP_REFERER')
    email = response.user.email
    message = f"Ваш отклик \"{text}\" был принят!"
    text = f'На объявление \"{advertisement.heading}\"'
    send_email_.delay(text, message, email)
    return render(request, 'activited_response.html', {'text': text, 'previous_url': previous_url})


def deactivited_response(request, pk, pk_res):
    """
    Отклоняет отклик к объявлению.

    :param request: объект запроса Django
    :param pk: первичный ключ объявления
    :param pk_res: первичный ключ отклика
    :return: объект ответа Django, который отображает шаблон 'deactivited_response.html'
    """

    advertisement = get_object_or_404(Advertisement, id=pk)
    response = get_object_or_404(Responses, id=pk_res, advertisement=advertisement)
    text = response.text
    response.is_active = False
    response.save()
    previous_url = request.META.get('HTTP_REFERER')
    return render(request, 'deactivited_response.html', {'text': text, 'previous_url': previous_url})
