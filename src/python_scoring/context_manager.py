"""Cross-domain context manager for ABC Assessment.

Reference: abc-assessment-spec Section 7

Loads domain_contexts.yaml and provides context-specific labels,
descriptions, and prompts. The underlying measurement model (six
subscales, 0-10 scale) is identical across contexts. Only the item
wording, labels, and narrative framing change.

SDT foundation: Ambition = autonomy, Belonging = relatedness,
Craft = competence. These three needs are universal per
Ryan & Deci (2017).
"""

import os
from pathlib import Path

import yaml

_DEFAULT_CONFIG = os.path.join(
    Path(__file__).resolve().parent.parent.parent,
    "config",
    "domain_contexts.yaml",
)

DOMAINS = ("ambition", "belonging", "craft")


class DomainContextManager:
    """Load and serve context-specific domain labels and prompts.

    Reference: abc-assessment-spec Section 7

    Usage:
        ctx = DomainContextManager(context='professional')
        labels = ctx.get_labels()
        # {'ambition': 'Drive', 'belonging': 'Connection', 'craft': 'Mastery'}
    """

    def __init__(self, context: str = "sport", config_path: str | None = None):
        """Initialize the context manager.

        Reference: abc-assessment-spec Section 7

        Args:
            context: One of the contexts defined in domain_contexts.yaml
                (sport, professional, military, healthcare, transition).
            config_path: Path to the YAML config. Defaults to
                config/domain_contexts.yaml.
        """
        path = config_path or _DEFAULT_CONFIG
        with open(path) as f:
            raw = yaml.safe_load(f)

        self._contexts = raw.get("contexts", {})
        if context not in self._contexts:
            raise ValueError(
                f"Unknown context '{context}'. Available: {sorted(self._contexts.keys())}"
            )
        self._context_name = context
        self._context = self._contexts[context]

    @property
    def context_name(self) -> str:
        """Return the active context name."""
        return self._context_name

    def get_labels(self) -> dict[str, str]:
        """Return domain-to-label mapping for the active context.

        Reference: abc-assessment-spec Section 7

        Returns:
            Dict mapping domain name to its context-specific label,
            e.g. {'ambition': 'Drive', 'belonging': 'Connection',
            'craft': 'Mastery'} for the professional context.
        """
        domains = self._context.get("domains", {})
        return {d: domains[d]["label"] for d in DOMAINS}

    def get_descriptions(self) -> dict[str, str]:
        """Return domain-to-description mapping for the active context.

        Reference: abc-assessment-spec Section 7

        Returns:
            Dict mapping domain name to its context-specific description.
        """
        domains = self._context.get("domains", {})
        return {d: domains[d]["description"] for d in DOMAINS}

    def get_prompts(self) -> dict[str, dict[str, str]]:
        """Return satisfaction and frustration prompts per domain.

        Reference: abc-assessment-spec Section 7

        Returns:
            Dict mapping domain name to a dict with keys
            'satisfaction_prompt' and 'frustration_prompt'.
        """
        domains = self._context.get("domains", {})
        return {
            d: {
                "satisfaction_prompt": domains[d]["satisfaction_prompt"],
                "frustration_prompt": domains[d]["frustration_prompt"],
            }
            for d in DOMAINS
        }

    def available_contexts(self) -> list[str]:
        """Return sorted list of all context names in the config.

        Reference: abc-assessment-spec Section 7
        """
        return sorted(self._contexts.keys())
