from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LlmEvaluationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "feder.llm_evaluation"
    verbose_name = _("LLM Evaluation")
