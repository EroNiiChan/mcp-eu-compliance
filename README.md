# 🇪🇺 EU Compliance & Factur-X MCP Server & GitHub Action

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-Marketplace-purple.svg?logo=githubactions)](https://github.com/EroNiiChan/mcp-eu-compliance)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-brightgreen.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-JSON--RPC%202.0-purple.svg)](https://modelcontextprotocol.io/)
[![Zero-Dependency](https://img.shields.io/badge/dependencies-0%20external-success.svg)](mcp_eu_compliance.py)
[![EU AI Act](https://img.shields.io/badge/Regulation-EU%202024%2F1689-orange.svg)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
[![EN 16931](https://img.shields.io/badge/Standard-EN%2016931%20%2F%20Factur--X-blueviolet.svg)](https://fnfe-mpe.org/factur-x/)
[![Sponsors](https://img.shields.io/badge/sponsor-EroNiiChan-pink.svg)](https://github.com/sponsors/EroNiiChan)

> **Zero-dependency Model Context Protocol (MCP) server & GitHub Action** empowering AI coding environments (**Claude Desktop, Cursor, Antigravity**) and **CI/CD pipelines** to validate **EN 16931 / Factur-X electronic invoices**, audit AI systems against the **EU AI Act**, and evaluate **GDPR & NIS2 readiness** directly in your workflow.

---

## 🚀 Quick Start: GitHub Actions CI/CD

Automatically validate Factur-X XML invoices in your billing, e-commerce, or ERP repo:

```yaml
name: Validate Factur-X E-Invoices

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  validate-invoices:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Validate Factur-X / EN 16931 Invoices
        uses: EroNiiChan/mcp-eu-compliance@v1
        with:
          mode: 'validate-facturx'
          path: './invoices'
          fail-on-error: 'true'
          output-file: 'facturx-compliance-report.md'
```

*Outputs markdown summary into `$GITHUB_STEP_SUMMARY` and sets `$GITHUB_OUTPUT` variables (`compliance-status`, `issues-count`, `report-path`).*

---

---

## ⚡ Why This Matters in 2025–2027

European regulation is fundamentally changing software development and B2B commerce:
1. **EU AI Act (Regulation (EU) 2024/1689)**:
   - Prohibited AI systems face immediate market bans and fines up to **€35,000,000 or 7% of worldwide annual turnover**.
   - High-risk systems (HR, credit, education, biometrics, critical infrastructure) require continuous risk management, data bias testing, technical documentation, human oversight, and CE marking.
2. **Mandatory B2B Electronic Invoicing (EN 16931 & Factur-X)**:
   - France, Germany (e-Rechnung), Poland, and EU member states are making structured electronic invoices mandatory for B2B transactions. Traditional PDFs are no longer compliant.
3. **NIS2 Directive & GDPR**:
   - Stringent 24h early warning incident reporting and €10M+ penalties for supply chain security oversights.

With `mcp-eu-compliance`, your LLM agent acts as an in-IDE European regulatory officer and electronic invoicing engine.

---

## 📦 Features

- **Zero External Dependencies**: Pure Python standard library (`sys`, `json`, `xml.etree.ElementTree`, `datetime`). Runs on any machine with Python 3.9+ without `pip install` headaches.
- **EU AI Act Risk Auditor (`audit_eu_ai_act`)**:
  - Classifies AI systems: *Unacceptable / Prohibited (Art 5)*, *High Risk (Annex III & Annex I)*, *GPAI Systemic Risk (FLOPs ≥ 10²⁵)*, *Transparency (Art 50)*, or *Minimal Risk*.
  - Generates Article 9–15 mandatory checklists, enforcement deadlines, and maximum penalty exposure.
- **Factur-X / EN 16931 Generator (`generate_facturx_invoice`)**:
  - Emits compliant UN/CEFACT CII (`CrossIndustryInvoice`) XML.
  - Supports `MINIMUM`, `BASIC`, and `EN16931` (Comfort) profiles with line items, multi-rate VAT breakdown, and SEPA payment details.
- **Factur-X XML Validator (`validate_facturx_xml`)**:
  - Validates XML structure, namespaces, profile identifiers, and verifies arithmetic summation across line net totals, VAT bases, and gross payable amounts.
- **GDPR & NIS2 Readiness Evaluator (`check_gdpr_nis2_readiness`)**:
  - Scans organizational size and sector to detect Essential vs Important Entity status under NIS2, missing incident response plans, and GDPR DPO triggers.
- **Enterprise Pro Licensing (`get_compliance_status_and_pro_license`)**:
  - Seamless in-IDE verification of Pro licenses for Peppol routing and automated hybrid PDF/A-3 compilation.

---

## 🚀 Quick Setup

### 1. Claude Desktop

Add to your `claude_desktop_config.json`:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "eu-compliance": {
      "command": "python",
      "args": [
        "C:\\Users\\Ender\\Documents\\Money\\swarm\\agent18_mcp_server\\mcp_eu_compliance.py"
      ]
    }
  }
}
```

### 2. Cursor IDE

In Cursor Settings → Features → MCP:

- **Name**: `eu-compliance`
- **Type**: `command`
- **Command**: `python c:\path\to\mcp_eu_compliance.py`

### 3. Google Antigravity / AGY

In your `agy` MCP configuration or agent configuration:

```json
{
  "mcpServers": {
    "eu_compliance": {
      "command": "python",
      "args": ["c:/path/to/mcp_eu_compliance.py"]
    }
  }
}
```

---

## 🛠️ Tool Specifications & Prompts

### 1. `audit_eu_ai_act`

**Example Prompt in IDE:**
> *"Audit our new automated candidate resume screening and interview scoring tool under the EU AI Act."*

**Arguments:**
- `system_name` *(str)*: System name.
- `description` *(str)*: Architecture and functionality summary.
- `intended_purpose` *(str)*: Use case (e.g. CV screening, credit evaluation, bot).
- `sector` *(str, optional)*: Industry sector (e.g. `employment`, `finance`, `healthcare`).
- `biometrics_used` *(bool, optional)*: Uses biometric data or facial processing.
- `affects_fundamental_rights` *(bool, optional)*: Potential rights impact.
- `is_gpai` *(bool, optional)*: Is it a general-purpose AI / foundation model.
- `training_flops` *(float, optional)*: Total compute FLOPs (≥ 1e25 designates systemic risk).

**Output Preview:**
```json
{
  "classification": "HIGH_RISK",
  "risk_level": "HIGH RISK (Annex III / Annex I)",
  "matched_high_risk_domains": [
    {
      "domain": "employment",
      "annex": "Annex III (4)",
      "title": "Employment, Workers Management & Access to Self-Employment"
    }
  ],
  "mandatory_requirements": [
    {"code": "ART_9_RMS", "title": "Risk Management System"},
    {"code": "ART_10_DATA_GOV", "title": "Data Governance & Bias Mitigation"},
    {"code": "ART_11_TECH_DOC", "title": "Technical Documentation & Annex IV"},
    {"code": "ART_14_HUMAN_OVERSIGHT", "title": "Human Oversight (HITL / HOTL)"},
    {"code": "ART_48_CE_MARK", "title": "CE Marking of Conformity"},
    {"code": "ART_71_EU_DATABASE", "title": "EU Database Registration"}
  ],
  "penalties": {
    "High-Risk Non-Compliance (Arts 9-15)": "Up to €15,000,000 or 3% of total worldwide annual turnover."
  }
}
```

---

### 2. `generate_facturx_invoice`

**Example Prompt in IDE:**
> *"Generate a Factur-X EN 16931 invoice for 500 EUR consulting services with 20% French VAT."*

**Arguments:**
- `invoice_number` *(str)*: e.g. `"INV-2026-001"`
- `issue_date` *(str)*: `"YYYY-MM-DD"`
- `seller` *(object)*: `name`, `country_code`, `vat_id`, `siret`, `iban`, `bic`, address.
- `buyer` *(object)*: `name`, `country_code`, `vat_id`, `siret`, address.
- `items` *(array)*: `name`, `quantity`, `unit_price`, `vat_rate`.
- `currency` *(str, default 'EUR')*
- `profile` *(str, default 'EN16931')*: `MINIMUM`, `BASIC`, `EN16931`, `EXTENDED`.

**Output:**
Returns pure UN/CEFACT CII XML ready to be saved as `factur-x.xml` or embedded into PDF/A-3.

---

### 3. `validate_facturx_xml`

**Example Prompt in IDE:**
> *"Verify if this Factur-X XML complies with the EN 16931 standard."*

**Arguments:**
- `xml_content` *(str)*: XML string to validate.

**Output:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "details": {
    "invoice_number": "INV-2026-001",
    "profile_name": "EN16931",
    "profile_urn": "urn:cen.eu:en16931:2017",
    "grand_total_amount": 600.0,
    "seller_name": "Hexagon Software SAS",
    "buyer_name": "Acme Consulting GmbH"
  },
  "standards_compliance": "EN 16931-1:2017 & UN/CEFACT CII D16B"
}
```

---

## 💎 Community vs. Pro Enterprise Tier

| Feature | Community Edition (Free) | Pro Enterprise Tier |
| :--- | :---: | :---: |
| **EU AI Act Risk Classification & Checklist** | ✅ Full Art 5–15 | ✅ Full Art 5–15 |
| **Factur-X / EN 16931 XML Generation** | ✅ All Profiles | ✅ All Profiles |
| **Monetary & XML Schema Validation** | ✅ Included | ✅ Included |
| **GDPR & NIS2 Rapid Auditor** | ✅ Included | ✅ Included |
| **Zero-Dependency Local StdIO Execution** | ✅ Yes | ✅ Yes |
| **Automated PDF/A-3 Hybrid Compilation** | Manual | ⚡ **Automated (X.509 Signed)** |
| **Direct Peppol AS4 & Chorus Pro Routing** | — | ⚡ **Automated API Dispatch** |
| **CI/CD Continuous AI Act RegWatch Scanner**| — | ⚡ **Automated PR Checks** |
| **Signed EU Conformity Assessment Dossier**| — | ⚡ **Automated PDF Export** |

### Upgrading to Pro:
- **Price**: $49/month or $299 lifetime license.
- **Sponsor / Purchase**: [GitHub Sponsors @EroNiiChan](https://github.com/sponsors/EroNiiChan) or [Polar.sh](https://polar.sh/EroNiiChan).
- Enter key via IDE: Call `get_compliance_status_and_pro_license(pro_license_key="EUPRO-XXXX-XXXX-XXXX")`.

---

## 🧪 Testing

Run the included automated test suite (10/10 tests covering AI Act classifications, XML arithmetic, schema validation, and JSON-RPC 2.0 stdio pipes):

```bash
python test_mcp_server.py
```

Expected output:
```text
..........
----------------------------------------------------------------------
Ran 10 tests in 0.093s

OK
```

---

## 📜 Regulatory Reference

- **Regulation (EU) 2024/1689** (Artificial Intelligence Act): [Official Journal L, 12.07.2024](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
- **Directive (EU) 2022/2555** (NIS2 Directive): [EUR-Lex](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)
- **Directive 2014/55/EU** on electronic invoicing in public procurement & **EN 16931-1:2017**
- **Factur-X / ZUGFeRD 2.2**: [FNFE-MPE & FeRD Specifications](https://fnfe-mpe.org/factur-x/)

---

## 🤝 Contributing & Support

Issues, PRs, and suggestions are welcome!
- **Author**: [@EroNiiChan](https://github.com/EroNiiChan)
- **Sponsorship**: [Support on GitHub Sponsors](https://github.com/sponsors/EroNiiChan)
- **License**: [Apache-2.0](LICENSE)
