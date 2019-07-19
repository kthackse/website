from page.models import Page


def get_page(category, code, published=True):
    return Page.objects.filter(category__code=category, code=code, published=published).first()
