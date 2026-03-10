from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Organization

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id", "name", "slug", "logo", "website", "plan",
            "max_surveys", "max_responses_per_survey", "is_active",
            "member_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "member_count"]

    def get_member_count(self, obj):
        return obj.members.count()


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "organization", "organization_id", "role", "avatar", "phone",
            "preferred_language", "timezone", "email_notifications",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "email", "created_at", "updated_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    organization_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "email", "username", "password", "password_confirm",
            "first_name", "last_name", "organization_name",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        organization_name = validated_data.pop("organization_name", None)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)

        if organization_name:
            from django.utils.text import slugify
            org = Organization.objects.create(
                name=organization_name,
                slug=slugify(organization_name),
            )
            user.organization = org
            user.role = "owner"

        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
