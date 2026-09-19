from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    subject = models.CharField(max_length=250, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.CharField(max_length=255, null=True, blank=True, verbose_name="Browser / Device")
    
    is_read = models.BooleanField(default=False, verbose_name="Is Read")
    is_starred = models.BooleanField(default=False, verbose_name="Starred")
    replied = models.BooleanField(default=False, verbose_name="Replied")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Replied At")
    
    reply_subject = models.CharField(max_length=250, blank=True, verbose_name="Last Reply Subject")
    reply_content = models.TextField(blank=True, verbose_name="Last Reply Message")
    admin_notes = models.TextField(blank=True, verbose_name="Admin Notes / Reply Log")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Received At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject} ({self.created_at.strftime('%b %d, %Y')})"
