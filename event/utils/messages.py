from event.models import Message


def save_message(event_id, recipient_id, title, content, type, attachment=None):
    message = Message(
        event_id=event_id,
        recipient_id=recipient_id,
        type=type.value,
        title=title,
        content=content,
        attachment=attachment,
    )
    message.save()
    return message


def save_message_with_email(event_id, email, title, content, type, attachment=None):
    message = Message(
        event_id=event_id,
        recipient_email=email,
        type=type.value,
        title=title,
        content=content,
        attachment=attachment,
    )
    message.save()
    print(message)
    return message


def get_message(message_id):
    return Message.objects.filter(id=message_id).first()
