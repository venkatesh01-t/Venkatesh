from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage

# Customize Admin Site Branding
admin.site.site_header = "Venkatesh Babu — Portfolio Dashboard"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Contact Messages & Site Administration"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'subject',
        'read_status_badge',
        'replied_status_badge',
        'created_at_formatted'
    )
    list_filter = ('is_read', 'replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message', 'ip_address')
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 'user_agent')
    ordering = ('-created_at',)
    list_per_page = 25
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_replied']

    fieldsets = (
        ("Sender Details", {
            'fields': ('name', 'email', 'ip_address', 'user_agent')
        }),
        ("Message Content", {
            'fields': ('subject', 'message')
        }),
        ("Status & Workflow", {
            'fields': ('is_read', 'replied', 'admin_notes')
        }),
        ("System Timestamps", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def read_status_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color: #10b981; font-weight: bold;">● Read</span>')
        return format_html('<span style="color: #ef4444; font-weight: bold; background: #fee2e2; padding: 2px 6px; border-radius: 4px;">● New</span>')
    read_status_badge.short_description = "Status"

    def replied_status_badge(self, obj):
        if obj.replied:
            return format_html('<span style="color: #06b6d4; font-weight: 600;">✓ Replied</span>')
        return format_html('<span style="color: #64748b;">Pending</span>')
    replied_status_badge.short_description = "Reply"

    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%b %d, %Y - %I:%M %p")
    created_at_formatted.short_description = "Received Date"

    # Custom Admin Actions
    @admin.action(description="Mark selected messages as Read")
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f"{count} message(s) marked as read.")

    @admin.action(description="Mark selected messages as Unread")
    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False)
        self.message_user(request, f"{count} message(s) marked as unread.")

    @admin.action(description="Mark selected messages as Replied")
    def mark_as_replied(self, request, queryset):
        count = queryset.update(replied=True, is_read=True)
        self.message_user(request, f"{count} message(s) marked as replied.")
