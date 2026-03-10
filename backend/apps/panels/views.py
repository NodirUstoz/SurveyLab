from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PanelMember, ResearchPanel
from .serializers import (
    PanelMemberBulkImportSerializer,
    PanelMemberCreateSerializer,
    PanelMemberSerializer,
    ResearchPanelCreateSerializer,
    ResearchPanelSerializer,
)


class ResearchPanelViewSet(viewsets.ModelViewSet):
    """CRUD for research panels."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.organization:
            return ResearchPanel.objects.filter(
                organization=user.organization
            )
        return ResearchPanel.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return ResearchPanelCreateSerializer
        return ResearchPanelSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Get panel statistics."""
        panel = self.get_object()
        members = panel.members.all()
        active = members.filter(is_active=True, opt_out=False)

        total_invited = sum(m.surveys_invited for m in active)
        total_completed = sum(m.surveys_completed for m in active)
        avg_response_rate = (
            total_completed / total_invited * 100 if total_invited > 0 else 0
        )

        return Response({
            "total_members": members.count(),
            "active_members": active.count(),
            "opted_out": members.filter(opt_out=True).count(),
            "total_invitations_sent": total_invited,
            "total_completions": total_completed,
            "average_response_rate": round(avg_response_rate, 1),
        })

    @action(detail=True, methods=["post"], url_path="bulk-import")
    def bulk_import(self, request, pk=None):
        """Bulk import members into a panel."""
        panel = self.get_object()
        serializer = PanelMemberBulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_count = 0
        skipped_count = 0
        for member_data in serializer.validated_data["members"]:
            _, created = PanelMember.objects.get_or_create(
                panel=panel,
                email=member_data["email"],
                defaults=member_data,
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        return Response({
            "created": created_count,
            "skipped": skipped_count,
            "total": created_count + skipped_count,
        })


class PanelMemberViewSet(viewsets.ModelViewSet):
    """CRUD for panel members within a research panel."""

    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["is_active", "opt_out"]
    search_fields = ["email", "first_name", "last_name"]

    def get_queryset(self):
        panel_id = self.kwargs.get("panel_pk")
        user = self.request.user
        return PanelMember.objects.filter(
            panel_id=panel_id,
            panel__organization=user.organization,
        )

    def get_serializer_class(self):
        if self.action == "create":
            return PanelMemberCreateSerializer
        return PanelMemberSerializer

    def perform_create(self, serializer):
        panel = ResearchPanel.objects.get(
            pk=self.kwargs["panel_pk"],
            organization=self.request.user.organization,
        )
        serializer.save(panel=panel)
