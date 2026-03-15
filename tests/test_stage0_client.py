"""Unit tests for the Stage0 client contract adapter."""

from unittest import TestCase

from stage0.client import Decision, ExecutionIntent, PolicyResponse, Verdict


class PolicyResponseParsingTests(TestCase):
    def test_parses_extended_contract_fields(self) -> None:
        response = PolicyResponse.from_dict(
            {
                "decision": "DEFER",
                "verdict": "DEFER",
                "reason": "Human approval required",
                "risk_score": 63,
                "high_risk": True,
                "issues": [
                    {
                        "code": "CUSTOMER_VISIBLE_APPROVAL_REQUIRED",
                        "severity": "MEDIUM",
                        "message": "Approval is missing",
                    }
                ],
                "guardrail_checks": {"ai_saas": {"customer_visible": {"satisfied": False}}},
                "request_id": "req_123",
                "policy_pack_version": "2026-03-15",
                "decision_trace_summary": "Deferred pending approval evidence.",
            }
        )

        self.assertEqual(response.decision, Decision.DEFER)
        self.assertEqual(response.verdict, Verdict.DEFER)
        self.assertEqual(response.request_id, "req_123")
        self.assertEqual(response.policy_pack_version, "2026-03-15")
        self.assertTrue(response.high_risk)
        self.assertIn("ai_saas", response.guardrail_checks)

    def test_reason_falls_back_to_issue_messages(self) -> None:
        response = PolicyResponse.from_dict(
            {
                "decision": "NO_GO",
                "verdict": "DENY",
                "issues": [
                    {
                        "code": "RESOURCE_SCOPE_VIOLATION",
                        "severity": "HIGH",
                        "message": "Target resource is outside the allowed scope",
                    }
                ],
            }
        )

        self.assertIn("RESOURCE_SCOPE_VIOLATION", response.reason)
        self.assertTrue(response.has_high_severity_issues())


class ExecutionIntentTests(TestCase):
    def test_request_body_includes_context_and_contract_fields(self) -> None:
        intent = ExecutionIntent(
            goal="Deploy the payments service",
            success_criteria=["Deployment succeeds"],
            constraints=["approval required"],
            tools=["argo_cd"],
            side_effects=["deployment"],
            context={
                "actor_role": "platform_admin",
                "approval_status": "approved",
                "environment": "production",
                "run_id": "run_123",
            },
            pro=True,
            policy_pack_version="2026-03-15",
            debug_store_input=True,
        )

        payload = intent.to_request_body()

        self.assertEqual(payload["context"]["run_id"], "run_123")
        self.assertEqual(payload["policy_pack_version"], "2026-03-15")
        self.assertTrue(payload["debug_store_input"])
        self.assertTrue(payload["pro"])
