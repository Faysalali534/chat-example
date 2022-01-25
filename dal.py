from channels.db import database_sync_to_async
from .models import MessageModel, DialogsModel, UploadedFile
from django.core.exceptions import ValidationError


@database_sync_to_async
def get_groups_to_add(user):
    l = DialogsModel.get_dialogs_for_user(user)
    return set(list(sum(l, ())))


@database_sync_to_async
def get_user_by_pk(pk):
    return Client.objects.filter(pk=pk).first()


@database_sync_to_async
def get_file_by_id(file_id):
    try:
        f = UploadedFile.objects.filter(id=file_id).first()
    except ValidationError:
        f = None
    return f


@database_sync_to_async
def get_message_by_id(mid):
    msg = MessageModel.objects.filter(id=mid).first()
    if msg:
        return str(msg.recipient.pk), str(msg.sender.pk)
    else:
        return None


@database_sync_to_async
def mark_message_as_read(mid):
    return MessageModel.objects.filter(id=mid).update(read=True)


@database_sync_to_async
def get_unread_count(sender, recipient):
    return int(MessageModel.get_unread_count_for_dialog_with_user(sender, recipient))


@database_sync_to_async
def save_text_message(text, from_, to):
    return MessageModel.objects.create(text=text, sender=from_, recipient=to)


@database_sync_to_async
def save_file_message(file, from_, to):
    return MessageModel.objects.create(file=file, sender=from_, recipient=to)

# As these methods are async, they will be called in consmers with await keyword.
# e.g  await get_user_by_pk(user_pk)
