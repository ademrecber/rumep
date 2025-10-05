# Mesajlaşma sistemi için models.py'ye eklenecek

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.subject[:50]}"

class MessageThread(models.Model):
    """Mesaj konuşma zinciri"""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='message_threads')
    last_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']