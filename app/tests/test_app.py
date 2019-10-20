from unittest import mock

import pytest
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from app.enums import FileStatus, FileVerificationStatus
from app.models import FileVerified
from app.tests.factories import FileFactory, FileVerifiedFactory


@pytest.mark.django_db
def test_verification():
    # Create a file
    file = FileFactory()

    # File is valid by default and has verification information
    assert file.status == FileStatus.VALID
    assert file.verification_control
    assert file.verification_code

    # Create a failed verification
    file_verified = FileVerifiedFactory(
        ip="127.0.0.1", verification_control="1234", verification_code="1234ABCD"
    )

    # Verification incorrect
    assert file_verified.status == FileVerificationStatus.FAILED

    # Create a correct verification
    file_verified2 = FileVerifiedFactory(
        ip="127.0.0.1",
        verification_control=file.verification_control,
        verification_code=file.verification_code,
    )

    # Verification correct
    assert file_verified2.status == FileVerificationStatus.SUCCESS

    # Create a client
    client = Client()

    # Post verification incorrect
    request = client.post(
        reverse("app_verify"),
        dict(
            control=file.verification_control[:7] + "X",
            verification=file.verification_code,
        ),
    )
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert (
        "The data control and verification numbers do not correspond to any valid document."
        in content
    )

    # Two failed verifications have been performed
    assert (
        FileVerified.objects.filter(status=FileVerificationStatus.FAILED).count() == 2
    )
    assert (
        FileVerified.objects.order_by("-verified_at").first().status
        == FileVerificationStatus.FAILED
    )
    assert FileVerified.objects.order_by("-verified_at").first().ip == "127.0.0.1"

    # Post verification correct
    request = client.post(
        reverse("app_verify"),
        dict(control=file.verification_control, verification=file.verification_code),
    )
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert '<embed src="/files/" type="application/pdf" />' in content

    # Two successful verifications have been performed
    assert (
        FileVerified.objects.filter(status=FileVerificationStatus.SUCCESS).count() == 2
    )
    assert (
        FileVerified.objects.order_by("-verified_at").first().status
        == FileVerificationStatus.SUCCESS
    )
    assert FileVerified.objects.order_by("-verified_at").first().ip == "127.0.0.1"

    # Attempt to verify 7 documents more (11 in total)
    for _ in range(7):
        request = client.post(
            reverse("app_verify"),
            dict(
                control=file.verification_control[:7] + "X",
                verification=file.verification_code,
            ),
        )
        assert isinstance(request, HttpResponse)
        assert request.status_code == 200
        content = request.content.decode("utf-8")

    # Last verification failed as maximum documents verified per hour is 10
    assert (
        "You have verified or attempted to verify 10 documents in the last hour, please wait some time before trying again."
        in content
    )
    assert FileVerified.objects.count() == 10

    with mock.patch(
        "django.utils.timezone.now",
        return_value=timezone.now() + timezone.timedelta(hours=1),
    ):
        # Verify another document after one hour
        request = client.post(
            reverse("app_verify"),
            dict(
                control=file.verification_control, verification=file.verification_code
            ),
        )
        assert isinstance(request, HttpResponse)
        assert request.status_code == 200
        content = request.content.decode("utf-8")
        assert '<embed src="/files/" type="application/pdf" />' in content

        # Eleven verifications have been performed
        assert FileVerified.objects.count() == 11
