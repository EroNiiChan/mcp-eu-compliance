#!/usr/bin/env python3
"""
Comprehensive Test Suite for EU Compliance & Factur-X MCP Server.
Verifies pure Python logic, XML generation/validation, AI Act rules, and JSON-RPC 2.0 stdio loop.
"""

import subprocess
import json
import sys
import os
import unittest

# Import directly for unit testing internal methods
import mcp_eu_compliance as mcp


class TestEUComplianceEngine(unittest.TestCase):

    def test_ai_act_high_risk_hr(self):
        """HR recruitment screening must be classified as High Risk Annex III (4)."""
        res = mcp.audit_eu_ai_act(
            system_name="TalentFilter AI",
            description="Automated candidate CV screening and ranking algorithm for tech hiring.",
            intended_purpose="Rank job applicants based on resume parsing and candidate suitability scores.",
            sector="employment"
        )
        self.assertEqual(res["classification"], "HIGH_RISK")
        self.assertIn("Annex III (4)", [h["annex"] for h in res["matched_high_risk_domains"]])
        self.assertTrue(any(req["code"] == "ART_9_RMS" for req in res["mandatory_requirements"]))
        self.assertTrue(any(req["code"] == "ART_14_HUMAN_OVERSIGHT" for req in res["mandatory_requirements"]))

    def test_ai_act_prohibited_social_scoring(self):
        """Social scoring must trigger Article 5 prohibition."""
        res = mcp.audit_eu_ai_act(
            system_name="CivicScore Pro",
            description="Monitors public social media and payment records to compute citizen score for welfare perks.",
            intended_purpose="Social scoring based on natural person social behavior.",
            sector="public_services"
        )
        self.assertEqual(res["classification"], "UNACCEPTABLE_RISK_PROHIBITED")
        self.assertTrue(len(res["matched_prohibitions"]) > 0)
        self.assertTrue(any(req["code"] == "HALT_DEPLOYMENT" for req in res["mandatory_requirements"]))

    def test_ai_act_gpai_systemic_risk(self):
        """GPAI with > 10^25 FLOPs compute must be classified as GPAI Systemic Risk."""
        res = mcp.audit_eu_ai_act(
            system_name="Titan-Omni-1",
            description="Frontier multimodal foundation model trained across massive web corpora.",
            intended_purpose="General purpose reasoning, code generation, and translation.",
            is_gpai=True,
            training_flops=1.5e25
        )
        self.assertEqual(res["classification"], "GPAI_SYSTEMIC_RISK")
        self.assertTrue(res["is_systemic_gpai"])

    def test_ai_act_transparency_chatbot(self):
        """Chatbot interacting with users must trigger Article 50 transparency disclosure."""
        res = mcp.audit_eu_ai_act(
            system_name="E-Shop Assistant",
            description="Customer support bot answering FAQ queries for clothing retail.",
            intended_purpose="Interactive chatbot helping shoppers find clothing sizes.",
            sector="retail"
        )
        self.assertEqual(res["classification"], "SPECIFIC_TRANSPARENCY_RISK")
        self.assertTrue(any(t["id"] == "ART50_DIRECT_INTERACTION" for t in res["matched_transparency_obligations"]))

    def test_ai_act_minimal_risk(self):
        """Spam filter or video game NPC must be minimal risk."""
        res = mcp.audit_eu_ai_act(
            system_name="SpamShield",
            description="Heuristic Bayesian classifier filtering unsolicited marketing emails.",
            intended_purpose="Spam detection in email inbox.",
            sector="cybersecurity"
        )
        self.assertEqual(res["classification"], "MINIMAL_RISK")

    def test_facturx_invoice_generation_and_validation(self):
        """Generates Factur-X XML and verifies it passes self-validation."""
        seller = {
            "name": "Hexagon Software SAS",
            "country_code": "FR",
            "address_line1": "42 Rue de Rivoli",
            "city": "Paris",
            "postcode": "75004",
            "vat_id": "FR12345678901",
            "siret": "12345678900014",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPPXXX"
        }
        buyer = {
            "name": "Acme Consulting GmbH",
            "country_code": "DE",
            "address_line1": "Friedrichstrasse 10",
            "city": "Berlin",
            "postcode": "10117",
            "vat_id": "DE987654321"
        }
        items = [
            {
                "name": "EU AI Act Compliance Audit API License",
                "quantity": 1,
                "unit_price": 500.00,
                "vat_rate": 20.0
            },
            {
                "name": "Factur-X Invoicing SDK Support",
                "quantity": 2,
                "unit_price": 150.00,
                "vat_rate": 20.0
            }
        ]

        inv = mcp.generate_facturx_invoice(
            invoice_number="INV-2026-TEST-001",
            issue_date="2026-10-29",
            seller=seller,
            buyer=buyer,
            items=items,
            currency="EUR",
            profile="EN16931"
        )

        self.assertIn("xml_content", inv)
        xml = inv["xml_content"]
        self.assertIn("CrossIndustryInvoice", xml)
        self.assertIn("urn:cen.eu:en16931:2017", xml)
        self.assertIn("INV-2026-TEST-001", xml)

        # Check math
        # 500 + 2 * 150 = 800 net. 20% vat = 160. gross = 960
        self.assertEqual(inv["totals"]["net_amount"], 800.0)
        self.assertEqual(inv["totals"]["tax_amount"], 160.0)
        self.assertEqual(inv["totals"]["gross_amount"], 960.0)

        # Validate with validator
        val_res = mcp.validate_facturx_xml(xml)
        self.assertTrue(val_res["is_valid"], f"Validation failed with errors: {val_res.get('errors')}")
        self.assertEqual(val_res["details"]["invoice_number"], "INV-2026-TEST-001")
        self.assertEqual(val_res["details"]["grand_total_amount"], 960.0)
        self.assertEqual(val_res["details"]["seller_name"], "Hexagon Software SAS")
        self.assertEqual(val_res["details"]["buyer_name"], "Acme Consulting GmbH")

    def test_facturx_validator_catches_errors(self):
        """Validator must report parsing errors and arithmetic mismatches."""
        # Broken XML
        bad_xml = "<invalid>xml without close tag"
        res = mcp.validate_facturx_xml(bad_xml)
        self.assertFalse(res["is_valid"])

        # XML with mismatched totals
        tampered_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice
    xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
    xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
    xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>urn:cen.eu:en16931:2017</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>INV-ERR-01</ram:ID>
    <ram:IssueDateTime><udt:DateTimeString>20261029</udt:DateTimeString></ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:ApplicableHeaderTradeAgreement>
      <ram:SellerTradeParty><ram:Name>Seller</ram:Name></ram:SellerTradeParty>
      <ram:BuyerTradeParty><ram:Name>Buyer</ram:Name></ram:BuyerTradeParty>
    </ram:ApplicableHeaderTradeAgreement>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>100.00</ram:LineTotalAmount>
        <ram:TaxBasisTotalAmount>100.00</ram:TaxBasisTotalAmount>
        <ram:TaxTotalAmount>20.00</ram:TaxTotalAmount>
        <ram:GrandTotalAmount>999.00</ram:GrandTotalAmount> <!-- MISMATCH -->
        <ram:DuePayableAmount>999.00</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""
        res_tampered = mcp.validate_facturx_xml(tampered_xml)
        self.assertFalse(res_tampered["is_valid"])
        self.assertTrue(any("Arithmetic mismatch" in err for err in res_tampered["errors"]))

    def test_gdpr_nis2_readiness(self):
        """Tests NIS2 essential entity detection and score."""
        res = mcp.check_gdpr_nis2_readiness(
            company_name="PowerGrid EU Corp",
            headquarters_country="FR",
            sector="energy",
            employee_count=500,
            annual_turnover_eur=120_000_000.0,
            has_incident_response_plan=True,
            has_mfa_implemented=True,
            has_designated_dpo=True
        )
        self.assertEqual(res["nis2_classification"], "ESSENTIAL_ENTITY")
        self.assertTrue(res["is_nis2_in_scope"])
        self.assertGreaterEqual(res["readiness_score_percent"], 50)

    def test_pro_license_tier(self):
        """Verifies Pro license key activation."""
        free_status = mcp.verify_and_get_license_status(None)
        self.assertFalse(free_status["is_pro_active"])
        self.assertIn("Community", free_status["current_tier"])

        pro_status = mcp.verify_and_get_license_status("EUPRO-2026-ENTERPRISE-KEY-XYZ")
        self.assertTrue(pro_status["is_pro_active"])
        self.assertIn("Enterprise Pro", pro_status["current_tier"])


class TestMCPServerStdio(unittest.TestCase):
    """Subprocess integration tests for JSON-RPC 2.0 stdio loop."""

    def setUp(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "mcp_eu_compliance.py")
        self.proc = subprocess.Popen(
            [sys.executable, self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def tearDown(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.proc.stdin:
            self.proc.stdin.close()
        if self.proc.stdout:
            self.proc.stdout.close()
        if self.proc.stderr:
            self.proc.stderr.close()

    def _rpc_call(self, method: str, params: dict = None, req_id: int = 1) -> dict:
        msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            msg["params"] = params
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line)

    def test_mcp_handshake_and_tools_call(self):
        # 1. Initialize
        init_res = self._rpc_call("initialize", {"protocolVersion": "2024-11-05"}, req_id=1)
        self.assertEqual(init_res["id"], 1)
        self.assertEqual(init_res["result"]["serverInfo"]["name"], "eu-compliance-mcp")

        # 2. Ping
        ping_res = self._rpc_call("ping", req_id=2)
        self.assertEqual(ping_res["id"], 2)

        # 3. List tools
        tools_res = self._rpc_call("tools/list", req_id=3)
        tools = tools_res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("audit_eu_ai_act", tool_names)
        self.assertIn("generate_facturx_invoice", tool_names)
        self.assertIn("validate_facturx_xml", tool_names)
        self.assertIn("check_gdpr_nis2_readiness", tool_names)
        self.assertIn("get_compliance_status_and_pro_license", tool_names)

        # 4. Call audit_eu_ai_act
        call_res = self._rpc_call(
            "tools/call",
            {
                "name": "audit_eu_ai_act",
                "arguments": {
                    "system_name": "CreditScorerAI",
                    "description": "Evaluates consumer creditworthiness and loan applications.",
                    "intended_purpose": "Credit scoring",
                    "sector": "finance"
                }
            },
            req_id=4
        )
        self.assertFalse(call_res["result"]["isError"])
        text_content = call_res["result"]["content"][0]["text"]
        parsed = json.loads(text_content)
        self.assertEqual(parsed["classification"], "HIGH_RISK")

        # 5. Call generate_facturx_invoice and then validate it via MCP
        gen_res = self._rpc_call(
            "tools/call",
            {
                "name": "generate_facturx_invoice",
                "arguments": {
                    "invoice_number": "MCP-TEST-001",
                    "issue_date": "2026-10-29",
                    "seller": {"name": "Vendor EU", "country_code": "FR"},
                    "buyer": {"name": "Client EU", "country_code": "DE"},
                    "items": [{"name": "API Service", "quantity": 1, "unit_price": 100.0, "vat_rate": 20.0}]
                }
            },
            req_id=5
        )
        self.assertFalse(gen_res["result"]["isError"])
        gen_data = json.loads(gen_res["result"]["content"][0]["text"])
        xml = gen_data["xml_content"]

        val_res = self._rpc_call(
            "tools/call",
            {
                "name": "validate_facturx_xml",
                "arguments": {"xml_content": xml}
            },
            req_id=6
        )
        self.assertFalse(val_res["result"]["isError"])
        val_data = json.loads(val_res["result"]["content"][0]["text"])
        self.assertTrue(val_data["is_valid"])


if __name__ == "__main__":
    unittest.main()
