from rest_framework import serializers

from .models import PanelMember, ResearchPanel


class PanelMemberSerializer(serializers.ModelSerializer):
    response_rate = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = PanelMember
        fields = [
            "id", "panel", "email", "first_name", "last_name", "full_name",
            "demographics", "tags", "is_active", "opt_out",
            "surveys_invited", "surveys_completed", "response_rate",
            "last_invited_at", "last_responded_at", "joined_at",
        ]
        read_only_fields = [
            "id", "surveys_invited", "surveys_completed",
            "last_invited_at", "last_responded_at", "joined_at",
        ]

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name or obj.email


class PanelMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanelMember
        fields = [
            "email", "first_name", "last_name",
            "demographics", "tags",
        ]


class PanelMemberBulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing panel members."""

    members = PanelMemberCreateSerializer(many=True)


class ResearchPanelSerializer(serializers.ModelSerializer):
    member_count = serializers.ReadOnlyField()
    active_member_count = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = ResearchPanel
        fields = [
            "id", "organization", "name", "description",
            "is_active", "member_count", "active_member_count",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "organization", "created_by",
            "created_at", "updated_at",
        ]


class ResearchPanelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchPanel
        fields = ["name", "description"]
