import uuid

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
import urllib.request

from page.enums import PageContentType


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.ForeignKey("Category", on_delete=models.PROTECT)
    code = models.CharField(max_length=31)
    content_plain = models.TextField(blank=True, null=True)
    content_html = models.TextField(blank=True, null=True)
    content_markdown = models.TextField(blank=True, null=True)
    content_markdown_url = models.CharField(max_length=255, blank=True, null=True)
    published = models.BooleanField(default=False)

    @property
    def content(self):
        if self.content_plain:
            return self.content_plain, PageContentType.PLAIN
        elif self.content_html:
            return self.content_html, PageContentType.HTML
        elif self.content_markdown:
            return self.content_markdown, PageContentType.MARKDOWN
        return urllib.request.urlopen(self.content_markdown_url).read().decode("utf-8"), PageContentType.MARKDOWN

    class Meta:
        unique_together = ("category", "code")

    def clean(self):
        messages = dict()
        if (
            sum(
                [
                    (1 if content else 0)
                    for content in [
                        self.content_plain,
                        self.content_html,
                        self.content_markdown,
                        self.content_markdown_url,
                    ]
                ]
            )
            != 1
        ):
            message = "You must ONLY FILL ONE plain, HTML, markdown content or markdown URL"
            messages["content_plain"] = message
            messages["content_html"] = message
            messages["content_markdown"] = message
            messages["content_url"] = message
        if messages:
            raise ValidationError(messages)


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=31, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"
