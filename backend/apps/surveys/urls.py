from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from . import views

app_name = "surveys"

router = DefaultRouter()
router.register(r"", views.SurveyViewSet, basename="survey")

# Nested routes: /surveys/{survey_pk}/pages/
survey_router = nested_routers.NestedDefaultRouter(router, r"", lookup="survey")
survey_router.register(r"pages", views.SurveyPageViewSet, basename="survey-pages")
survey_router.register(
    r"branching-rules", views.BranchingRuleViewSet, basename="survey-branching-rules"
)

# Nested routes: /surveys/{survey_pk}/pages/{page_pk}/questions/
page_router = nested_routers.NestedDefaultRouter(
    survey_router, r"pages", lookup="page"
)
page_router.register(r"questions", views.QuestionViewSet, basename="page-questions")

# Nested routes: /surveys/.../questions/{question_pk}/options/
question_router = nested_routers.NestedDefaultRouter(
    page_router, r"questions", lookup="question"
)
question_router.register(
    r"options", views.QuestionOptionViewSet, basename="question-options"
)

urlpatterns = [
    path("public/<slug:slug>/", views.PublicSurveyView.as_view(), name="public-survey"),
    path("", include(router.urls)),
    path("", include(survey_router.urls)),
    path("", include(page_router.urls)),
    path("", include(question_router.urls)),
]
