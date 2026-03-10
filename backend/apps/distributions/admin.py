from django.contrib import admin

from .models import DistributionChannel, EmailCampaign, EmbedConfiguration


class EmbedConfigurationInline(admin.StackedInline):
    model = EmbedConfiguration
    can_delete = False
    extra = 0


@admin.register(DistributionChannel)
class DistributionChannelAdmin(admin.ModelAdmin):
    list_display = [
        "name", "survey", "channel_type", "is_active",
        "click_count", "response_count", "conversion_rate",
        "created_at",
    ]
    list_filter = ["channel_type", "is_active", "created_at"]
    search_fields = ["name", "survey__title", "unique_token"]
    readonly_fields = [
        "id", "unique_token", "click_count", "response_count",
        "created_at", "updated_at",
    ]
    inlines = [EmbedConfigurationInline]


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = [
        "subject", "channel", "status", "total_sent",
        "total_opened", "open_rate", "scheduled_at", "sent_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["subject"]
    readonly_fields = [
        "id", "total_sent", "total_opened", "total_clicked",
        "total_bounced", "sent_at", "created_at",
    ]
