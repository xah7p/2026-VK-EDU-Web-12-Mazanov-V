from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate(queryset_or_list, request, per_page=10):
    page_number = request.GET.get("page", 1)
    paginator = Paginator(queryset_or_list, per_page)
    try:
        return paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        return paginator.get_page(1)