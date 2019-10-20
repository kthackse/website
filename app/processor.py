from app.utils import get_substitutions_templates


def variables_processor(request=None):
    c = get_substitutions_templates()
    from event.utils.utils import get_next_or_past_event, get_application, is_application_to_review

    event = get_next_or_past_event()
    if event:
        c["event"] = event
        c["background_video"] = event.background.name[-4:] == ".mp4"
        c["background_image"] = event.background.name[-4:] in [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
        ]
        if request:
            application = get_application(event.id, request.user.id)
            if application:
                c["application"] = application
            if request.user.is_authenticated:
                c["to_review"] = is_application_to_review(request.user.id)
    return c
