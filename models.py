

class DialogsModel(mixins.TimeStampable):
    id = models.BigAutoField(primary_key=True, verbose_name="Id")
    user1 = models.ForeignKey("clients.Client", on_delete=models.CASCADE, verbose_name="User1",
                              related_name="+", db_index=True)
    user2 = models.ForeignKey("clients.Client", on_delete=models.CASCADE, verbose_name="User2",
                              related_name="+", db_index=True)

    class Meta:
        unique_together = (('user1', 'user2'), ('user2', 'user1'))
        verbose_name = "Dialog"
        verbose_name_plural = "Dialogs"

    def __str__(self):
        return f"Dialog between {self.user1_id}, {self.user2_id}"

    @staticmethod
    def dialog_exists(u1, u2):
        return DialogsModel.objects.filter(Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)).first()

    @staticmethod
    def create_if_not_exists(u1, u2):
        res = DialogsModel.dialog_exists(u1, u2)
        if not res:
            DialogsModel.objects.create(user1=u1, user2=u2)

    @staticmethod
    def get_dialogs_for_user(user):
        return DialogsModel.objects.filter(Q(user1=user) | Q(user2=user)).values_list('user1__pk', 'user2__pk')



class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey("clients.Client", on_delete=models.CASCADE, verbose_name="Uploaded_by",
                                    related_name='+', db_index=True)
    file = models.FileField(verbose_name="File", upload_to="s3_path_here")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Upload date")

    def __str__(self):
        return str(self.file.name)


class MessageModel(mixins.TimeStampable):
    id = models.BigAutoField(primary_key=True, verbose_name="Id")
    sender = models.ForeignKey("clients.Client", on_delete=models.CASCADE, verbose_name="Author",
                               related_name='from_user', db_index=True)
    recipient = models.ForeignKey("clients.Client", on_delete=models.CASCADE, verbose_name="Recipient",
                                  related_name='to_user', db_index=True)
    text = models.TextField("Text", blank=True)
    file = models.ForeignKey(UploadedFile, related_name='message', on_delete=models.DO_NOTHING,
                             verbose_name="File", blank=True, null=True)

    read = models.BooleanField(verbose_name="Read", default=False)
    all_objects = models.Manager()

    @staticmethod
    def get_unread_count_for_dialog_with_user(sender, recipient):
        return MessageModel.objects.filter(sender_id=sender, recipient_id=recipient, read=False).count()

    @staticmethod
    def get_last_message_for_dialog(sender, recipient):
        return MessageModel.objects.filter(
            Q(sender_id=sender, recipient_id=recipient) | Q(sender_id=recipient, recipient_id=sender)) \
            .select_related('sender', 'recipient').first()

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        DialogsModel.create_if_not_exists(self.sender, self.recipient)
