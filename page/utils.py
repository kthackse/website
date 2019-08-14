from page.models import Page


def get_page(category, code, published=True, user=None):
    if user.is_authenticated:
        return Page.objects.filter(
            category__code=category, code=code, published=published
        ).first()
    return Page.objects.filter(
        category__code=category, code=code, published=published, public=True
    ).first()
