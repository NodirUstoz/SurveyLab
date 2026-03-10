import secrets

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.surveys.models import Survey
from .models import DistributionChannel, EmailCampaign, EmbedConfiguration
from .serializers import (
    DistributionChannelCreateSerializer,
    DistributionChannelSerializer,
    EmailCampaignCreateSerializer,
    EmailCampaignSerializer,
    EmbedConfigurationSerializer,
)


class DistributionChannelViewSet(viewsets.ModelViewSet):
    """Manage distribution channels for surveys."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DistributionChannel.objects.filter(
            survey__owner=self.request.user
        ).select_related("embed_config")

    def get_serializer_class(self):
        if self.action in ("create",):
            return DistributionChannelCreateSerializer
        return DistributionChannelSerializer

    def perform_create(self, serializer):
        token = secrets.token_urlsafe(32)
        serializer.save(
            created_by=self.request.user,
            unique_token=token,
        )

    @action(detail=True, methods=["post"], url_path="track-click")
    def track_click(self, request, pk=None):
        """Track a click on this distribution channel."""
        channel = self.get_object()
        channel.click_count += 1
        channel.save(update_fields=["click_count"])
        return Response({"click_count": channel.click_count})

    @action(detail=True, methods=["get", "put", "patch"])
    def embed(self, request, pk=None):
        """Get or update embed configuration for this channel."""
        channel = self.get_object()

        if request.method == "GET":
            try:
                config = channel.embed_config
            except EmbedConfiguration.DoesNotExist:
                return Response(
                    {"detail": "No embed configuration found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(EmbedConfigurationSerializer(config).data)

        config, _ = EmbedConfiguration.objects.get_or_create(channel=channel)
        serializer = EmbedConfigurationSerializer(
            config, data=request.data, partial=(request.method == "PATCH")
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SurveyDistributionChannelsView(generics.ListAPIView):
    """List all distribution channels for a specific survey."""

    serializer_class = DistributionChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        survey_id = self.kwargs["survey_id"]
        return DistributionChannel.objects.filter(
            survey_id=survey_id,
            survey__owner=self.request.user,
        ).select_related("embed_config")


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """Manage email campaigns for distribution channels."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmailCampaign.objects.filter(
            channel__survey__owner=self.request.user
        )

    def get_serializer_class(self):
        if self.action in ("create",):
            return EmailCampaignCreateSerializer
        return EmailCampaignSerializer

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """Queue an email campaign for sending."""
        campaign = self.get_object()
        if campaign.status not in ("draft", "scheduled"):
            return Response(
                {"detail": "Campaign cannot be sent in its current state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        campaign.status = EmailCampaign.Status.SENDING
        campaign.save(update_fields=["status"])

        from .tasks import send_email_campaign
        send_email_campaign.delay(str(campaign.id))

        return Response(
            {"detail": "Campaign queued for sending."},
            status=status.HTTP_202_ACCEPTED,
        )


class PublicChannelTrackView(APIView):
    """Public endpoint to track channel visits and redirect to survey."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        try:
            channel = DistributionChannel.objects.select_related("survey").get(
                unique_token=token, is_active=True
            )
        except DistributionChannel.DoesNotExist:
            return Response(
                {"detail": "Invalid or inactive link."},
                status=status.HTTP_404_NOT_FOUND,
            )

        channel.click_count += 1
        channel.save(update_fields=["click_count"])

        return Response({
            "survey_slug": channel.survey.slug,
            "survey_id": str(channel.survey.id),
            "channel_type": channel.channel_type,
        })
