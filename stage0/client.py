"""Stage0 API Client for runtime policy validation.

This client communicates with the Stage0 runtime policy authority
to validate execution intents before they are executed.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class Verdict(Enum):
    """Stage0 verdict types."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    DEFER = "DEFER"


@dataclass
class PolicyResponse:
    """Response from Stage0 policy check."""
    verdict: Verdict
    reason: str
    constraints_applied: list[str]
    raw_response: dict
    risk_score: int = 0
    issues: list[dict] = None
    clarifying_questions: list[str] = None
    cached: bool = False
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.issues is None:
            self.issues = []
        if self.clarifying_questions is None:
            self.clarifying_questions = []
    
    @classmethod
    def from_dict(cls, data: dict) -> "PolicyResponse":
        """Parse policy response from API response."""
        verdict_str = data.get("verdict", "DENY").upper()
        # Handle invalid verdict values gracefully
        try:
            verdict = Verdict(verdict_str)
        except ValueError:
            # Default to DENY for unknown verdicts (fail-safe)
            verdict = Verdict.DENY
        
        # Handle None or missing constraints_applied
        constraints = data.get("constraints_applied") or []
        
        # Parse issues list
        issues = data.get("issues") or []
        
        # Parse clarifying questions
        questions = data.get("clarifying_questions") or []
        
        # Build reason from issues if not provided
        reason = data.get("reason")
        if not reason and issues:
            # Build reason from the first issue or combine all issues
            issue_messages = [
                f"{i.get('code', 'UNKNOWN')}: {i.get('message', '')}" 
                for i in issues
            ]
            reason = "; ".join(issue_messages)
        elif not reason:
            reason = "No reason provided"
        
        return cls(
            verdict=verdict,
            reason=reason,
            constraints_applied=constraints,
            raw_response=data,
            risk_score=data.get("risk_score", 0),
            issues=issues,
            clarifying_questions=questions,
            cached=data.get("cached", False)
        )
    
    def has_issues(self) -> bool:
        """Check if there are any issues detected."""
        return len(self.issues) > 0
    
    def get_issue_severities(self) -> list[str]:
        """Get list of issue severity levels."""
        return [issue.get("severity", "UNKNOWN") for issue in self.issues]
    
    def has_high_severity_issues(self) -> bool:
        """Check if there are any HIGH severity issues."""
        return "HIGH" in self.get_issue_severities()


@dataclass
class ExecutionIntent:
    """Represents an execution intent to be validated."""
    goal: str
    success_criteria: list[str]
    constraints: list[str]
    tools: list[str]
    side_effects: list[str]
    pro: bool = False
    
    def to_request_body(self) -> dict:
        """Convert to API request body format."""
        return {
            "goal": self.goal,
            "success_criteria": self.success_criteria,
            "constraints": self.constraints,
            "tools": self.tools,
            "side_effects": self.side_effects,
            "pro": self.pro
        }


class Stage0Client:
    """Client for Stage0 runtime policy validation.
    
    Stage0 is the runtime policy authority and MUST be treated as
    the final decision maker. All execution intents must be validated
    through this client before execution.
    
    API Behavior:
    - HIGH severity issues (e.g., SIDE_EFFECTS_NEED_GUARDRAILS) → DENY
    - MEDIUM severity issues → DENY only with pro=true, otherwise ALLOW
    - DEFER verdict for low-value/under-specified tasks
    
    The free tier provides full DENY functionality for HIGH severity issues.
    Pro plan unlocks MEDIUM severity DENY and advanced features.
    """
    
    API_BASE_URL = "https://api.signalpulse.org"
    CHECK_ENDPOINT = "/check"
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        risk_threshold: int = 100,
        deny_on_issues: bool = False
    ):
        """Initialize Stage0 client.
        
        Args:
            api_key: Stage0 API key. If not provided, reads from STAGE0_API_KEY env var.
            risk_threshold: Auto-deny if risk_score >= threshold. Default 100 (disabled).
                           Set lower (e.g., 20) to deny risky operations on free tier.
            deny_on_issues: If True, auto-deny when any issues are detected.
        """
        self.api_key = api_key or os.getenv("STAGE0_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Stage0 API key is required. Set STAGE0_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.risk_threshold = risk_threshold
        self.deny_on_issues = deny_on_issues
    
    def check(self, intent: ExecutionIntent) -> PolicyResponse:
        """Validate an execution intent with Stage0.
        
        This method MUST be called before every execution step.
        The agent cannot self-approve actions - all validation
        must go through Stage0.
        
        Args:
            intent: The execution intent to validate.
            
        Returns:
            PolicyResponse containing the verdict and reasoning.
            
        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"{self.API_BASE_URL}{self.CHECK_ENDPOINT}"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        try:
            response = requests.post(
                url,
                json=intent.to_request_body(),
                headers=headers,
                timeout=30
            )
            
            # Handle 402 Payment Required (Pro feature)
            if response.status_code == 402:
                return self._handle_pro_required(response, intent)
            
            response.raise_for_status()
            policy_response = PolicyResponse.from_dict(response.json())
            
            # Apply local risk-based denial for free tier
            if policy_response.verdict == Verdict.ALLOW:
                policy_response = self._apply_local_rules(policy_response, intent)
            
            return policy_response
            
        except requests.RequestException as e:
            # If Stage0 is unavailable, deny by default (fail-safe)
            return PolicyResponse(
                verdict=Verdict.DENY,
                reason=f"Stage0 validation failed: {str(e)}",
                constraints_applied=[],
                raw_response={"error": str(e)}
            )
    
    def _handle_pro_required(self, response: requests.Response, intent: ExecutionIntent) -> PolicyResponse:
        """Handle 402 Payment Required response for Pro features."""
        try:
            error_data = response.json()
            reason = error_data.get("detail", "Pro checks require a paid plan")
        except:
            reason = "Pro checks require a paid plan"
        
        return PolicyResponse(
            verdict=Verdict.DENY,
            reason=f"Stage0 Pro required: {reason}",
            constraints_applied=[],
            raw_response={"status_code": 402, "intent": intent.to_request_body()},
            issues=[{
                "code": "PRO_PLAN_REQUIRED",
                "severity": "HIGH",
                "message": reason
            }]
        )
    
    def _apply_local_rules(self, response: PolicyResponse, intent: ExecutionIntent) -> PolicyResponse:
        """Apply local validation rules.
        
        This method can enforce additional local rules based on
        risk_score and issues. The API already handles DENY for
        HIGH severity issues, but these local rules provide
        extra protection layers.
        
        Args:
            response: The API response.
            intent: The original execution intent.
            
        Returns:
            Potentially modified PolicyResponse.
        """
        # Check risk threshold
        if response.risk_score >= self.risk_threshold:
            return PolicyResponse(
                verdict=Verdict.DENY,
                reason=f"Risk score ({response.risk_score}) exceeds threshold ({self.risk_threshold})",
                constraints_applied=response.constraints_applied,
                raw_response=response.raw_response,
                risk_score=response.risk_score,
                issues=response.issues,
                clarifying_questions=response.clarifying_questions
            )
        
        # Check for issues if deny_on_issues is enabled
        if self.deny_on_issues and response.has_issues():
            high_severity = any(
                issue.get("severity") == "HIGH" 
                for issue in response.issues
            )
            if high_severity:
                return PolicyResponse(
                    verdict=Verdict.DENY,
                    reason=f"High severity issues detected: {response.issues[0].get('message', 'Unknown issue')}",
                    constraints_applied=response.constraints_applied,
                    raw_response=response.raw_response,
                    risk_score=response.risk_score,
                    issues=response.issues,
                    clarifying_questions=response.clarifying_questions
                )
        
        return response
    
    def check_goal(
        self,
        goal: str,
        success_criteria: Optional[list[str]] = None,
        constraints: Optional[list[str]] = None,
        tools: Optional[list[str]] = None,
        side_effects: Optional[list[str]] = None,
        pro: bool = False
    ) -> PolicyResponse:
        """Convenience method to check a goal directly.
        
        Args:
            goal: Single clear execution intent.
            success_criteria: Measurable conditions for success.
            constraints: Constraints to apply (e.g., "informational only").
            tools: Tools that will be used.
            side_effects: Expected side effects.
            pro: Whether this is a pro-tier request.
            
        Returns:
            PolicyResponse containing the verdict and reasoning.
        """
        intent = ExecutionIntent(
            goal=goal,
            success_criteria=success_criteria or [],
            constraints=constraints or [],
            tools=tools or [],
            side_effects=side_effects or [],
            pro=pro
        )
        return self.check(intent)
