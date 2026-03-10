from rest_framework import serializers

from .models import DistributionChannel, EmailCampaign, EmbedConfiguration


class EmbedConfigurationSerializer(serializers.ModelSerializer):
    embed_code = serializers.SerializerMethodField()

    class Meta:
        model = EmbedConfiguration
        fields = [
            "id", "embed_type", "width", "height",
            "allowed_domains", "trigger_delay_seconds",
            "trigger_scroll_percent", "show_close_button",
            "custom_css", "embed_code",
        ]
        read_only_fields = ["id", "embed_code"]

    def get_embed_code(self, obj):
        return obj.generate_embed_code()


class DistributionChannelSerializer(serializers.ModelSerializer):
    conversion_rate = serializers.ReadOnlyField()
    embed_config = EmbedConfigurationSerializer(read_only=True)

    class Meta:
        model = DistributionChannel
        fields = [
            "id", "survey", "channel_type", "name", "is_active",
            "unique_token", "click_count", "response_count",
            "conversion_rate", "config", "embed_config",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "unique_token", "click_count", "response_count",
            "conversion_rate", "created_by", "created_at", "updated_at",
        ]


class DistributionChannelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionChannel
        fields = ["survey", "channel_type", "name", "config"]

    def validate_survey(self, value):
        user = self.context["request"].user
        if value.owner != user:
            raise serializers.ValidationError("You do not own this survey.")
        return value


class EmailCampaignSerializer(serializers.ModelSerializer):
    open_rate = serializers.ReadOnlyField()

    class Meta:
        model = EmailCampaign
        fields = [
            "id", "channel", "subject", "body_html", "body_text",
            "from_name", "from_email", "reply_to",
            "recipient_list", "status", "scheduled_at", "sent_at",
            "total_sent", "total_opened", "total_clicked",
            "total_bounced", "open_rate", "created_at",
        ]
        read_only_fields = [
            "id", "total_sent", "total_opened", "total_clicked",
            "total_bounced", "open_rate", "sent_at", "created_at",
        ]


class EmailCampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailCampaign
        fields = [
            "channel", "subject", "body_html", "body_text",
            "from_name", "from_email", "reply_to",
            "recipient_list", "scheduled_at",
        ]
