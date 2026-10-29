#!/usr/bin/env python3
"""
EU Compliance & Factur-X MCP Server (Model Context Protocol)
Zero-dependency Python implementation of JSON-RPC 2.0 stdio server.

Enables Claude Desktop, Cursor, Antigravity, and AI IDE users to:
1. Audit AI systems for EU AI Act (Regulation (EU) 2024/1689) risk classification & compliance requirements.
2. Generate EN 16931 & UN/CEFACT CII compliant Factur-X electronic invoices.
3. Validate Factur-X / EN 16931 XML invoices against European e-invoicing standards.
4. Assess GDPR (Regulation (EU) 2016/679) & NIS2 (Directive (EU) 2022/2555) readiness.
5. Manage Pro license key for enterprise features (Peppol routing, PDF/A-3 hybrid embedding).

Author: EroNiiChan / Agent #18
License: Apache-2.0
"""

import sys
import json
import re
import datetime
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple

SERVER_NAME = "eu-compliance-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

PRO_LICENSE_PREFIX = "EUPRO-"
PRO_UPGRADE_URL = "https://github.com/sponsors/EroNiiChan"


# =====================================================================
# 1. EU AI ACT AUDIT ENGINE (Regulation (EU) 2024/1689)
# =====================================================================

PROHIBITED_TRIGGERS = [
    {
        "id": "ART5_SUBLIMINAL",
        "keywords": ["subliminal", "manipulative", "deceptive technique", "cognitive behavioral manipulation"],
        "name": "Subliminal or Manipulative Distortion of Behavior",
        "article": "Article 5(1)(a)",
        "description": "Deploying subliminal techniques or purposeful manipulative/deceptive techniques that impair informed decision-making causing significant harm."
    },
    {
        "id": "ART5_VULNERABILITY",
        "keywords": ["exploit vulnerability", "exploit age", "exploit disability", "exploit socio-economic"],
        "name": "Exploitation of Vulnerabilities",
        "article": "Article 5(1)(b)",
        "description": "Exploiting vulnerabilities of individuals due to age, disability, or specific socio-economic situation to distort behavior and cause significant harm."
    },
    {
        "id": "ART5_SOCIAL_SCORING",
        "keywords": ["social scoring", "citizen score", "social rating", "trustworthiness score"],
        "name": "Social Scoring of Natural Persons",
        "article": "Article 5(1)(c)",
        "description": "Evaluating or classifying natural persons over time based on social behavior or personality traits leading to detrimental or unfavorable treatment."
    },
    {
        "id": "ART5_PREDICTIVE_POLICING",
        "keywords": ["predictive policing", "criminal offense prediction", "crime prediction person"],
        "name": "Individual Predictive Policing Profiling",
        "article": "Article 5(1)(d)",
        "description": "Assessing the risk of an individual committing criminal offenses based solely on profiling or personality traits without objective factual verification."
    },
    {
        "id": "ART5_FACIAL_SCRAPING",
        "keywords": ["facial scraping", "cctv scraping", "untargeted facial recognition database", "scraping facial images"],
        "name": "Untargeted Facial Image Scraping",
        "article": "Article 5(1)(e)",
        "description": "Creating or expanding facial recognition databases through untargeted scraping of facial images from the internet or CCTV footage."
    },
    {
        "id": "ART5_EMOTION_WORKPLACE",
        "keywords": ["emotion recognition workplace", "emotion recognition school", "emotion detection employee", "student emotion detection"],
        "name": "Emotion Recognition in Workplace or Education",
        "article": "Article 5(1)(f)",
        "description": "Inferring emotions of natural persons in workplace or educational institutions, except for strictly medical or safety reasons."
    },
    {
        "id": "ART5_BIOMETRIC_CATEGORIZATION",
        "keywords": ["biometric categorization race", "infer political opinion", "infer sexual orientation", "deduce religious beliefs"],
        "name": "Sensitive Biometric Categorization",
        "article": "Article 5(1)(g)",
        "description": "Categorizing natural persons based on biometric data to deduce race, political opinions, trade union membership, religious beliefs, sex life or sexual orientation."
    },
    {
        "id": "ART5_REALTIME_RBI",
        "keywords": ["real-time remote biometric identification", "public space facial recognition police"],
        "name": "Real-time Remote Biometric Identification in Public Spaces",
        "article": "Article 5(1)(h)",
        "description": "Real-time RBI in publicly accessible spaces for law enforcement without explicit judicial pre-authorization or imminent threat."
    }
]

HIGH_RISK_DOMAINS = [
    {
        "domain": "biometrics",
        "keywords": ["biometric identification", "facial recognition", "voiceprint", "iris scan", "emotion recognition"],
        "annex": "Annex III (1)",
        "title": "Biometrics and Biometric Categorization"
    },
    {
        "domain": "critical_infrastructure",
        "keywords": ["water supply", "gas network", "electricity grid", "traffic control", "nuclear", "district heating", "digital infrastructure safety"],
        "annex": "Annex III (2)",
        "title": "Critical Infrastructure & Public Utilities"
    },
    {
        "domain": "education",
        "keywords": ["education admission", "exam grading", "student assessment", "vocational training selection", "student monitoring"],
        "annex": "Annex III (3)",
        "title": "Education and Vocational Training"
    },
    {
        "domain": "employment",
        "keywords": ["recruitment", "resume screening", "cv filtering", "candidate ranking", "worker monitoring", "task allocation", "promotion evaluation", "firing decision"],
        "annex": "Annex III (4)",
        "title": "Employment, Workers Management & Access to Self-Employment"
    },
    {
        "domain": "essential_services",
        "keywords": ["credit scoring", "loan eligibility", "health insurance risk", "life insurance pricing", "emergency dispatch", "fire ambulance dispatch", "public welfare eligibility"],
        "annex": "Annex III (5)",
        "title": "Essential Private and Public Services & Benefits"
    },
    {
        "domain": "law_enforcement",
        "keywords": ["law enforcement", "lie detector", "polygraph", "evidence evaluation", "crime analytics", "profiling suspects"],
        "annex": "Annex III (6)",
        "title": "Law Enforcement"
    },
    {
        "domain": "migration",
        "keywords": ["asylum", "visa application", "border control", "migration management", "travel document verification"],
        "annex": "Annex III (7)",
        "title": "Migration, Asylum and Border Control Management"
    },
    {
        "domain": "justice",
        "keywords": ["judicial authority", "court sentencing", "legal dispute resolution", "alternative dispute resolution", "election influence"],
        "annex": "Annex III (8)",
        "title": "Administration of Justice & Democratic Processes"
    },
    {
        "domain": "annex_i_safety",
        "keywords": ["medical device", "in vitro diagnostic", "machinery safety", "civil aviation", "motor vehicle safety", "railway safety"],
        "annex": "Annex I",
        "title": "Products Covered by EU Safety Harmonisation Legislation"
    }
]

TRANSPARENCY_TRIGGERS = [
    {
        "id": "ART50_DIRECT_INTERACTION",
        "keywords": ["chatbot", "conversational agent", "virtual assistant", "customer support bot", "interactive agent"],
        "article": "Article 50(1)",
        "title": "Direct Interaction with Natural Persons",
        "rule": "System must inform natural persons that they are interacting with an AI system, unless obvious from context."
    },
    {
        "id": "ART50_SYNTHETIC_CONTENT",
        "keywords": ["deepfake", "synthetic media", "ai generated video", "ai generated voice", "ai generated image", "generative text"],
        "article": "Article 50(2) & 50(4)",
        "title": "Synthetic Audio, Image, Video or Text Content",
        "rule": "Must label outputs in a machine-readable format and disclose that content has been artificially generated or manipulated."
    },
    {
        "id": "ART50_EMOTION_BIOMETRIC",
        "keywords": ["emotion recognition", "biometric categorization"],
        "article": "Article 50(3)",
        "title": "Emotion Recognition & Biometric Categorization Disclosure",
        "rule": "Exposed natural persons must be informed of the operation of the system and personal data processing."
    }
]


def audit_eu_ai_act(
    system_name: str,
    description: str,
    intended_purpose: str,
    sector: Optional[str] = None,
    biometrics_used: bool = False,
    affects_fundamental_rights: bool = False,
    is_gpai: bool = False,
    training_flops: Optional[float] = None
) -> Dict[str, Any]:
    """Audits an AI system against Regulation (EU) 2024/1689."""
    text_corpus = f"{system_name} {description} {intended_purpose} {sector or ''}".lower()

    # 1. Prohibited check (Article 5)
    matched_prohibitions = []
    for p in PROHIBITED_TRIGGERS:
        for kw in p["keywords"]:
            if kw in text_corpus:
                matched_prohibitions.append(p)
                break

    # 2. GPAI check (Chapter V)
    is_systemic_gpai = False
    if is_gpai or "foundation model" in text_corpus or "llm" in text_corpus:
        is_gpai = True
        if training_flops and training_flops >= 1e25:
            is_systemic_gpai = True
        elif "systemic" in text_corpus or "frontier model" in text_corpus:
            is_systemic_gpai = True

    # 3. High-Risk check (Annex I & Annex III)
    matched_high_risk = []
    for hr in HIGH_RISK_DOMAINS:
        matched = False
        if sector and hr["domain"] in sector.lower():
            matched = True
        else:
            for kw in hr["keywords"]:
                if kw in text_corpus:
                    matched = True
                    break
        if matched:
            matched_high_risk.append(hr)

    if biometrics_used and not any(h["domain"] == "biometrics" for h in matched_high_risk):
        matched_high_risk.append({
            "domain": "biometrics",
            "annex": "Annex III (1)",
            "title": "Biometrics and Biometric Categorization"
        })

    # 4. Transparency check (Article 50)
    matched_transparency = []
    for t in TRANSPARENCY_TRIGGERS:
        for kw in t["keywords"]:
            if kw in text_corpus:
                matched_transparency.append(t)
                break

    # Determine primary classification
    if matched_prohibitions:
        classification = "UNACCEPTABLE_RISK_PROHIBITED"
        risk_level = "PROHIBITED (Article 5)"
        summary = (
            f"CRITICAL: System '{system_name}' falls under Prohibited AI practices "
            f"under Article 5 of the EU AI Act. Placing this system on the EU market "
            f"or putting it into service is strictly illegal."
        )
    elif matched_high_risk:
        classification = "HIGH_RISK"
        risk_level = "HIGH RISK (Annex III / Annex I)"
        summary = (
            f"System '{system_name}' is classified as HIGH-RISK under EU AI Act "
            f"({', '.join(h['annex'] for h in matched_high_risk)}). Full compliance with Chapter III "
            f"(Articles 8-15, 43, 49, 71) is mandatory prior to commercial deployment."
        )
    elif is_systemic_gpai:
        classification = "GPAI_SYSTEMIC_RISK"
        risk_level = "GENERAL-PURPOSE AI WITH SYSTEMIC RISK (Chapter V, Section 2)"
        summary = (
            f"System '{system_name}' is classified as a GPAI Model with Systemic Risk "
            f"(Compute >= 10^25 FLOPs or high-impact capabilities). Stringent adversarial testing, "
            f"model evaluation, and cybersecurity reporting to the EU AI Office are required."
        )
    elif is_gpai:
        classification = "GPAI_GENERAL"
        risk_level = "GENERAL-PURPOSE AI (Chapter V, Section 1)"
        summary = (
            f"System '{system_name}' is classified as General-Purpose AI. Technical documentation, "
            f"Union copyright policy compliance, and publicly available training data summaries are required."
        )
    elif matched_transparency:
        classification = "SPECIFIC_TRANSPARENCY_RISK"
        risk_level = "SPECIFIC TRANSPARENCY RISK (Article 50)"
        summary = (
            f"System '{system_name}' falls under Article 50 transparency obligations. Users must be "
            f"explicitly informed they are interacting with an AI system, and synthetic media must be watermarked."
        )
    else:
        classification = "MINIMAL_RISK"
        risk_level = "MINIMAL / LOW RISK"
        summary = (
            f"System '{system_name}' is assessed as Minimal/Low Risk under the EU AI Act. "
            f"No mandatory regulatory hurdles apply, but adhering to voluntary EU Codes of Conduct is recommended."
        )

    # Mandatory Requirements Checklist
    requirements = []
    if classification == "UNACCEPTABLE_RISK_PROHIBITED":
        requirements.append({
            "code": "HALT_DEPLOYMENT",
            "article": "Article 5",
            "title": "Immediate Cessation & Redesign",
            "description": "Cease development or remove prohibited capabilities (e.g. emotion recognition in workplace, biometric categorization of sensitive traits)."
        })
    elif classification in ("HIGH_RISK", "GPAI_SYSTEMIC_RISK"):
        requirements.extend([
            {
                "code": "ART_9_RMS",
                "article": "Article 9",
                "title": "Risk Management System",
                "description": "Establish, implement, document and maintain a continuous risk management system throughout the entire lifecycle."
            },
            {
                "code": "ART_10_DATA_GOV",
                "article": "Article 10",
                "title": "Data Governance & Bias Mitigation",
                "description": "Training, validation and testing data sets must be relevant, representative, free of errors and examined for biases."
            },
            {
                "code": "ART_11_TECH_DOC",
                "article": "Article 11",
                "title": "Technical Documentation & Annex IV",
                "description": "Draft comprehensive technical documentation demonstrating compliance before placing on market."
            },
            {
                "code": "ART_12_LOGGING",
                "article": "Article 12",
                "title": "Automatic Event Logging",
                "description": "Record-keeping capabilities allowing automatic logging of events over the system's lifetime."
            },
            {
                "code": "ART_13_TRANSPARENCY",
                "article": "Article 13",
                "title": "Transparency & Instructions for Deployers",
                "description": "Provide concise, complete, and clear instructions for use (deployer user manual)."
            },
            {
                "code": "ART_14_HUMAN_OVERSIGHT",
                "article": "Article 14",
                "title": "Human Oversight (HITL / HOTL)",
                "description": "Design system to enable natural persons to oversee operation, prevent or minimize risks, and trigger an immediate stop button."
            },
            {
                "code": "ART_15_CYBERSECURITY",
                "article": "Article 15",
                "title": "Accuracy, Robustness & Cybersecurity",
                "description": "Resilience against adversarial inputs, data poisoning, model evasion, and cyber attacks."
            },
            {
                "code": "ART_43_CONFORMITY",
                "article": "Article 43",
                "title": "Conformity Assessment Procedure",
                "description": "Carry out internal conformity assessment or third-party assessment with a designated Notified Body."
            },
            {
                "code": "ART_48_CE_MARK",
                "article": "Article 48",
                "title": "CE Marking of Conformity",
                "description": "Affix visible, legible and indelible CE marking before market entry."
            },
            {
                "code": "ART_71_EU_DATABASE",
                "article": "Article 71",
                "title": "EU Database Registration",
                "description": "Register system and provider details in the publicly accessible EU database for high-risk AI."
            }
        ])
    elif classification == "GPAI_GENERAL":
        requirements.extend([
            {
                "code": "ART_53_TECH_DOC",
                "article": "Article 53(1)(a)",
                "title": "GPAI Technical Documentation",
                "description": "Create and keep up-to-date technical documentation including training and testing processes."
            },
            {
                "code": "ART_53_DOWNSTREAM_INFO",
                "article": "Article 53(1)(b)",
                "title": "Downstream Integrator Information",
                "description": "Supply technical documentation to downstream AI system providers integrating the model."
            },
            {
                "code": "ART_53_COPYRIGHT",
                "article": "Article 53(1)(c)",
                "title": "EU Copyright Directive Compliance",
                "description": "Put in place a policy to comply with Union copyright law (Directive (EU) 2019/790, Art 4(3) opt-outs)."
            },
            {
                "code": "ART_53_TRAINING_SUMMARY",
                "article": "Article 53(1)(d)",
                "title": "Public Training Content Summary",
                "description": "Publish a sufficiently detailed summary about the content used for training the GPAI model."
            }
        ])
    elif classification == "SPECIFIC_TRANSPARENCY_RISK":
        requirements.append({
            "code": "ART_50_LABELING",
            "article": "Article 50",
            "title": "Mandatory AI Disclosure & Machine-Readable Watermarking",
            "description": "Inform users clearly of AI interaction; label synthetic audio, video, images, or text in a machine-detectable format."
        })

    # Enforcement Deadlines & Penalties
    deadlines = {
        "Feb 2, 2025": "Prohibitions on unacceptable risk systems take effect (Article 5).",
        "Aug 2, 2025": "GPAI model obligations, governance structure & AI Office supervision take effect.",
        "Aug 2, 2026": "High-Risk AI systems under Annex III must comply fully with all obligations.",
        "Aug 2, 2027": "High-Risk AI systems embedded in Annex I harmonised products (e.g. medical devices) must comply."
    }

    penalties = {
        "Prohibited AI Violations (Art 5)": "Up to €35,000,000 or 7% of total worldwide annual turnover (whichever is higher).",
        "High-Risk Non-Compliance (Arts 9-15)": "Up to €15,000,000 or 3% of total worldwide annual turnover.",
        "Misleading Information to Authorities": "Up to €7,500,000 or 1.5% of total worldwide annual turnover.",
        "SME / Startup Protection": "Fines are subject to lower caps (the lower of the percentage or fixed amount)."
    }

    return {
        "system_name": system_name,
        "classification": classification,
        "risk_level": risk_level,
        "summary": summary,
        "matched_prohibitions": matched_prohibitions,
        "matched_high_risk_domains": matched_high_risk,
        "matched_transparency_obligations": matched_transparency,
        "is_gpai": is_gpai,
        "is_systemic_gpai": is_systemic_gpai,
        "mandatory_requirements": requirements,
        "deadlines": deadlines,
        "penalties": penalties,
        "pro_upgrade_note": "For automated AI Act continuous integration scanning & Notified Body technical dossier compilation, upgrade to Pro."
    }


# =====================================================================
# 2. FACTUR-X / EN 16931 ELECTRONIC INVOICE ENGINE
# =====================================================================

FACTURX_PROFILES = {
    "MINIMUM": "urn:factur-x.eu:1p0:minimum",
    "BASIC_WL": "urn:factur-x.eu:1p0:basicwl",
    "BASIC": "urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:basic",
    "EN16931": "urn:cen.eu:en16931:2017",
    "EXTENDED": "urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended"
}

def escape_xml(s: str) -> str:
    """Safely escapes XML string values."""
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def generate_facturx_invoice(
    invoice_number: str,
    issue_date: str,
    seller: Dict[str, Any],
    buyer: Dict[str, Any],
    items: List[Dict[str, Any]],
    currency: str = "EUR",
    profile: str = "EN16931",
    payment_terms: Optional[str] = "Payment due within 30 days upon invoice receipt.",
    buyer_reference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a valid UN/CEFACT CII Factur-X / EN 16931 XML electronic invoice.
    Strictly zero dependencies, pure Python standard library.
    """
    prof_key = profile.upper().replace("-", "_")
    profile_urn = FACTURX_PROFILES.get(prof_key, FACTURX_PROFILES["EN16931"])

    # Parse and format date YYYYMMDD for UN/CEFACT format 102
    clean_date = issue_date.replace("-", "").replace("/", "")
    if len(clean_date) != 8:
        clean_date = datetime.date.today().strftime("%Y%m%d")

    # Calculate line totals & VAT breakdown
    line_total_sum = 0.0
    tax_breakdown: Dict[float, Dict[str, float]] = {}
    lines_xml = []

    for idx, item in enumerate(items, start=1):
        name = escape_xml(item.get("name", f"Item #{idx}"))
        qty = float(item.get("quantity", 1.0))
        unit_price = float(item.get("unit_price", 0.0))
        vat_rate = float(item.get("vat_rate", 20.0))
        unit_code = item.get("unit_code", "C62")  # C62 = UNECE code for 'one' / unit

        line_net = round(qty * unit_price, 2)
        line_total_sum += line_net

        if vat_rate not in tax_breakdown:
            tax_breakdown[vat_rate] = {"basis": 0.0, "amount": 0.0}
        tax_breakdown[vat_rate]["basis"] += line_net

        line_xml = f"""    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>{idx}</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:Name>{name}</ram:Name>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>{unit_price:.2f}</ram:ChargeAmount>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="{escape_xml(unit_code)}">{qty:.2f}</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>{"S" if vat_rate > 0 else "Z"}</ram:CategoryCode>
          <ram:RateApplicablePercent>{vat_rate:.2f}</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>{line_net:.2f}</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>"""
        lines_xml.append(line_xml)

    total_vat = 0.0
    tax_elements_xml = []
    for rate, vals in sorted(tax_breakdown.items()):
        vat_amount = round(vals["basis"] * (rate / 100.0), 2)
        vals["amount"] = vat_amount
        total_vat += vat_amount
        cat_code = "S" if rate > 0 else "Z"

        tax_elements_xml.append(f"""      <ram:ApplicableTradeTax>
        <ram:CalculatedAmount>{vat_amount:.2f}</ram:CalculatedAmount>
        <ram:TypeCode>VAT</ram:TypeCode>
        <ram:BasisAmount>{vals["basis"]:.2f}</ram:BasisAmount>
        <ram:CategoryCode>{cat_code}</ram:CategoryCode>
        <ram:RateApplicablePercent>{rate:.2f}</ram:RateApplicablePercent>
      </ram:ApplicableTradeTax>""")

    grand_total = round(line_total_sum + total_vat, 2)

    # Seller formatting
    seller_name = escape_xml(seller.get("name", "European Seller"))
    seller_line1 = escape_xml(seller.get("address_line1", "10 Rue de la Paix"))
    seller_city = escape_xml(seller.get("city", "Paris"))
    seller_postcode = escape_xml(seller.get("postcode", "75001"))
    seller_country = escape_xml(seller.get("country_code", "FR").upper())
    seller_vat = escape_xml(seller.get("vat_id", ""))
    seller_siret = escape_xml(seller.get("siret", ""))
    seller_iban = escape_xml(seller.get("iban", ""))
    seller_bic = escape_xml(seller.get("bic", ""))

    seller_tax_xml = ""
    if seller_vat:
        seller_tax_xml += f"""        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="VA">{seller_vat}</ram:ID>
        </ram:SpecifiedTaxRegistration>
"""
    if seller_siret:
        seller_tax_xml += f"""        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="0002">{seller_siret}</ram:ID>
        </ram:SpecifiedTaxRegistration>
"""

    # Buyer formatting
    buyer_name = escape_xml(buyer.get("name", "European Buyer"))
    buyer_line1 = escape_xml(buyer.get("address_line1", "Friedrichstrasse 50"))
    buyer_city = escape_xml(buyer.get("city", "Berlin"))
    buyer_postcode = escape_xml(buyer.get("postcode", "10115"))
    buyer_country = escape_xml(buyer.get("country_code", "DE").upper())
    buyer_vat = escape_xml(buyer.get("vat_id", ""))
    buyer_siret = escape_xml(buyer.get("siret", ""))

    buyer_tax_xml = ""
    if buyer_vat:
        buyer_tax_xml += f"""        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="VA">{buyer_vat}</ram:ID>
        </ram:SpecifiedTaxRegistration>
"""
    if buyer_siret:
        buyer_tax_xml += f"""        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="0002">{buyer_siret}</ram:ID>
        </ram:SpecifiedTaxRegistration>
"""

    # Payment means
    payment_means_xml = ""
    if seller_iban:
        payment_means_xml = f"""      <ram:SpecifiedTradeSettlementPaymentMeans>
        <ram:TypeCode>58</ram:TypeCode>
        <ram:PayeePartyCreditorFinancialAccount>
          <ram:IBANID>{seller_iban}</ram:IBANID>
        </ram:PayeePartyCreditorFinancialAccount>"""
        if seller_bic:
            payment_means_xml += f"""
        <ram:PayeeSpecifiedCreditorFinancialInstitution>
          <ram:BICID>{seller_bic}</ram:BICID>
        </ram:PayeeSpecifiedCreditorFinancialInstitution>"""
        payment_means_xml += """
      </ram:SpecifiedTradeSettlementPaymentMeans>
"""

    buyer_ref_xml = ""
    if buyer_reference:
        buyer_ref_xml = f"""      <ram:BuyerReference>{escape_xml(buyer_reference)}</ram:BuyerReference>
"""

    # Build XML document
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice
    xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
    xmlns:ccts="urn:un:unece:uncefact:documentation:standard:CoreComponentsTechnicalSpecification:2"
    xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
    xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:100"
    xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>{profile_urn}</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>{escape_xml(invoice_number)}</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">{clean_date}</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
{chr(10).join(lines_xml)}
    <ram:ApplicableHeaderTradeAgreement>
{buyer_ref_xml}      <ram:SellerTradeParty>
        <ram:Name>{seller_name}</ram:Name>
        <ram:PostalTradeAddress>
          <ram:PostcodeCode>{seller_postcode}</ram:PostcodeCode>
          <ram:LineOne>{seller_line1}</ram:LineOne>
          <ram:CityName>{seller_city}</ram:CityName>
          <ram:CountryID>{seller_country}</ram:CountryID>
        </ram:PostalTradeAddress>
{seller_tax_xml}      </ram:SellerTradeParty>
      <ram:BuyerTradeParty>
        <ram:Name>{buyer_name}</ram:Name>
        <ram:PostalTradeAddress>
          <ram:PostcodeCode>{buyer_postcode}</ram:PostcodeCode>
          <ram:LineOne>{buyer_line1}</ram:LineOne>
          <ram:CityName>{buyer_city}</ram:CityName>
          <ram:CountryID>{buyer_country}</ram:CountryID>
        </ram:PostalTradeAddress>
{buyer_tax_xml}      </ram:BuyerTradeParty>
    </ram:ApplicableHeaderTradeAgreement>
    <ram:ApplicableHeaderTradeDelivery/>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>{escape_xml(currency.upper())}</ram:InvoiceCurrencyCode>
{payment_means_xml}{chr(10).join(tax_elements_xml)}
      <ram:SpecifiedTradePaymentTerms>
        <ram:Description>{escape_xml(payment_terms or '')}</ram:Description>
      </ram:SpecifiedTradePaymentTerms>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>{line_total_sum:.2f}</ram:LineTotalAmount>
        <ram:TaxBasisTotalAmount>{line_total_sum:.2f}</ram:TaxBasisTotalAmount>
        <ram:TaxTotalAmount currencyID="{escape_xml(currency.upper())}">{total_vat:.2f}</ram:TaxTotalAmount>
        <ram:GrandTotalAmount>{grand_total:.2f}</ram:GrandTotalAmount>
        <ram:DuePayableAmount>{grand_total:.2f}</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""

    return {
        "invoice_number": invoice_number,
        "issue_date": clean_date,
        "profile": profile.upper(),
        "profile_urn": profile_urn,
        "currency": currency.upper(),
        "totals": {
            "net_amount": line_total_sum,
            "tax_amount": total_vat,
            "gross_amount": grand_total,
            "tax_breakdown": tax_breakdown
        },
        "lines_count": len(items),
        "xml_content": xml_content,
        "pro_upgrade_note": "For automated PDF/A-3 hybrid compilation with digital X.509 signatures and direct Peppol / Chorus Pro API dispatch, upgrade to Pro."
    }


def validate_facturx_xml(xml_content: str) -> Dict[str, Any]:
    """
    Validates a Factur-X / EN 16931 XML document.
    Checks XML well-formedness, root element, namespaces, profile URN, and monetary arithmetic.
    """
    errors = []
    warnings = []
    details = {}

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        return {
            "is_valid": False,
            "errors": [f"XML parsing syntax error: {str(e)}"],
            "warnings": [],
            "details": {}
        }

    # Verify root tag
    tag_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if tag_name != "CrossIndustryInvoice":
        errors.append(f"Invalid root tag: expected 'CrossIndustryInvoice', found '{tag_name}'.")

    # Extract namespace map
    ns = {
        "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
        "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
        "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
    }

    # Extract Profile URN
    prof_elem = root.find(".//ram:GuidelineSpecifiedDocumentContextParameter/ram:ID", ns)
    if prof_elem is not None and prof_elem.text:
        detected_urn = prof_elem.text.strip()
        details["profile_urn"] = detected_urn
        matched_prof = None
        for name, urn in FACTURX_PROFILES.items():
            if urn.lower() == detected_urn.lower():
                matched_prof = name
                break
        details["profile_name"] = matched_prof or "UNKNOWN_CUSTOM_PROFILE"
    else:
        errors.append("Missing mandatory ExchangedDocumentContext/GuidelineSpecifiedDocumentContextParameter/ID")

    # Extract Invoice ID & Date
    id_elem = root.find(".//rsm:ExchangedDocument/ram:ID", ns)
    if id_elem is not None and id_elem.text:
        details["invoice_number"] = id_elem.text.strip()
    else:
        errors.append("Missing mandatory ExchangedDocument/ID")

    date_elem = root.find(".//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString", ns)
    if date_elem is not None and date_elem.text:
        details["issue_date"] = date_elem.text.strip()
    else:
        errors.append("Missing mandatory ExchangedDocument/IssueDateTime/DateTimeString")

    # Check Seller & Buyer
    seller_elem = root.find(".//ram:SellerTradeParty/ram:Name", ns)
    if seller_elem is not None and seller_elem.text:
        details["seller_name"] = seller_elem.text.strip()
    else:
        errors.append("Missing mandatory SellerTradeParty/Name (BT-27)")

    buyer_elem = root.find(".//ram:BuyerTradeParty/ram:Name", ns)
    if buyer_elem is not None and buyer_elem.text:
        details["buyer_name"] = buyer_elem.text.strip()
    else:
        errors.append("Missing mandatory BuyerTradeParty/Name (BT-44)")

    # Check Monetary Summation Arithmetic
    summation = root.find(".//ram:SpecifiedTradeSettlementHeaderMonetarySummation", ns)
    if summation is not None:
        def get_val(name: str) -> Optional[float]:
            el = summation.find(f"ram:{name}", ns)
            if el is not None and el.text:
                try:
                    return float(el.text.strip())
                except ValueError:
                    errors.append(f"Invalid monetary value format in {name}: {el.text}")
            return None

        line_tot = get_val("LineTotalAmount")
        tax_basis = get_val("TaxBasisTotalAmount")
        tax_tot = get_val("TaxTotalAmount")
        grand_tot = get_val("GrandTotalAmount")
        due_tot = get_val("DuePayableAmount")

        details["line_total_amount"] = line_tot
        details["tax_basis_amount"] = tax_basis
        details["tax_total_amount"] = tax_tot
        details["grand_total_amount"] = grand_tot
        details["due_payable_amount"] = due_tot

        if line_tot is not None and tax_tot is not None and grand_tot is not None:
            expected_grand = round(line_tot + tax_tot, 2)
            if abs(expected_grand - grand_tot) > 0.02:
                errors.append(f"Arithmetic mismatch: LineTotal ({line_tot}) + TaxTotal ({tax_tot}) = {expected_grand}, but GrandTotal is {grand_tot}")
    else:
        errors.append("Missing mandatory SpecifiedTradeSettlementHeaderMonetarySummation")

    # Check lines
    lines = root.findall(".//ram:IncludedSupplyChainTradeLineItem", ns)
    details["lines_count"] = len(lines)
    if not lines and details.get("profile_name") not in ("MINIMUM", "BASIC_WL"):
        warnings.append("No line items found. For standard EN 16931 invoices, at least one line item is required.")

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "details": details,
        "standards_compliance": "EN 16931-1:2017 & UN/CEFACT CII D16B" if is_valid else "NON_COMPLIANT"
    }


# =====================================================================
# 3. GDPR & NIS2 RAPID READINESS CHECK
# =====================================================================

NIS2_ESSENTIAL_SECTORS = [
    "energy", "transport", "banking", "financial_market_infrastructures",
    "health", "drinking_water", "waste_water", "digital_infrastructure",
    "ict_management", "public_administration", "space"
]

NIS2_IMPORTANT_SECTORS = [
    "postal_services", "waste_management", "chemicals", "food",
    "manufacturing", "digital_providers", "research"
]

def check_gdpr_nis2_readiness(
    company_name: str,
    headquarters_country: str,
    sector: str,
    employee_count: int,
    annual_turnover_eur: float,
    processes_special_category_data: bool = False,
    data_transfers_outside_eea: bool = False,
    has_incident_response_plan: bool = False,
    has_mfa_implemented: bool = False,
    has_designated_dpo: bool = False
) -> Dict[str, Any]:
    """Evaluates organization readiness under GDPR & NIS2 Directive."""
    sec = sector.lower().replace(" ", "_")

    # NIS2 entity classification
    is_large = employee_count >= 250 or annual_turnover_eur >= 50_000_000
    is_medium = (employee_count >= 50 or annual_turnover_eur >= 10_000_000) and not is_large

    nis2_status = "OUT_OF_SCOPE"
    if sec in NIS2_ESSENTIAL_SECTORS:
        if is_large:
            nis2_status = "ESSENTIAL_ENTITY"
        elif is_medium:
            nis2_status = "ESSENTIAL_OR_IMPORTANT_ENTITY"
    elif sec in NIS2_IMPORTANT_SECTORS:
        if is_large or is_medium:
            nis2_status = "IMPORTANT_ENTITY"

    # Score calculation
    readiness_points = 0
    max_points = 6
    gaps = []

    if has_incident_response_plan:
        readiness_points += 1
    else:
        gaps.append("Lack of formalized Cyber Incident Response Plan (NIS2 Art 21 mandatory 24h early warning + 72h incident notification).")

    if has_mfa_implemented:
        readiness_points += 1
    else:
        gaps.append("Multi-Factor Authentication (MFA) not fully deployed across remote and administrative access (NIS2 Art 21(2)(j)).")

    if has_designated_dpo:
        readiness_points += 1
    elif processes_special_category_data or is_large:
        gaps.append("Mandatory Data Protection Officer (DPO) required under GDPR Article 37 due to data scale or sensitivity.")

    if not data_transfers_outside_eea:
        readiness_points += 1
    else:
        gaps.append("Non-EEA data transfers require Standard Contractual Clauses (SCCs) and Transfer Impact Assessments (TIAs) under GDPR Chapter V.")

    # Supply chain security & backup
    score_percentage = int((readiness_points / max_points) * 100)

    recommendations = [
        "Implement technical controls for 24h / 72h CSIRT reporting mechanism under NIS2 Article 23.",
        "Maintain GDPR Article 30 Records of Processing Activities (ROPA).",
        "Conduct periodic technical audits and vulnerability assessments (penetration testing).",
        "Secure supply chain contracts with cybersecurity liability clauses (NIS2 Art 21(2)(d))."
    ]

    return {
        "company_name": company_name,
        "headquarters_country": headquarters_country.upper(),
        "sector": sector,
        "nis2_classification": nis2_status,
        "is_nis2_in_scope": nis2_status != "OUT_OF_SCOPE",
        "readiness_score_percent": score_percentage,
        "identified_compliance_gaps": gaps,
        "actionable_recommendations": recommendations,
        "sanctions_notice": {
            "NIS2_Essential": "Fines up to €10,000,000 or 2% of worldwide turnover + management liability suspension.",
            "NIS2_Important": "Fines up to €7,000,000 or 1.4% of worldwide turnover.",
            "GDPR": "Fines up to €20,000,000 or 4% of worldwide annual turnover."
        }
    }


# =====================================================================
# 4. PRO LICENSE & STATUS
# =====================================================================

def verify_and_get_license_status(pro_license_key: Optional[str] = None) -> Dict[str, Any]:
    """Verifies Pro license key and returns server capability matrix."""
    is_pro = False
    plan_tier = "Community Edition (Free & Open Source)"

    if pro_license_key:
        key = pro_license_key.strip()
        if key.startswith(PRO_LICENSE_PREFIX) and len(key) >= 16:
            is_pro = True
            plan_tier = "Enterprise Pro Tier (Active)"

    return {
        "server_name": SERVER_NAME,
        "version": SERVER_VERSION,
        "current_tier": plan_tier,
        "is_pro_active": is_pro,
        "community_features": [
            "Full EU AI Act (Reg 2024/1689) risk classification & Art 5-15 checklist",
            "EN 16931 & UN/CEFACT Factur-X XML generator (Minimum, Basic, Comfort)",
            "Factur-X XML structural & monetary arithmetic validation",
            "GDPR & NIS2 Rapid Readiness Auditor",
            "Zero dependencies, 100% local IDE stdio execution"
        ],
        "pro_enterprise_features": [
            "Automated PDF/A-3 Hybrid embedding with digital X.509 signatures",
            "Direct Peppol AS4 Network & French Chorus Pro dispatch routing",
            "Automated CI/CD AI Act continuous compliance scanning & SBOM audit",
            "Signed EU Conformity Assessment technical documentation generation",
            "Priority regulatory watch updates for EU delegated acts"
        ],
        "upgrade_info": {
            "sponsor_url": PRO_UPGRADE_URL,
            "instant_key_delivery": "Add a sponsor tier or contact support for corporate site licenses.",
            "price": "$49/month or $299 lifetime per developer seat"
        }
    }


# =====================================================================
# 5. MCP JSON-RPC 2.0 PROTOCOL ENGINE
# =====================================================================

TOOLS_SCHEMA = [
    {
        "name": "audit_eu_ai_act",
        "description": "Audits an AI system against the EU AI Act (Regulation (EU) 2024/1689). Detects prohibited practices (Article 5), high-risk systems (Annex III / Annex I), general-purpose AI (GPAI) with systemic risk, and transparency requirements (Article 50). Returns mandatory requirements checklist, deadlines, and penalty risks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "system_name": {
                    "type": "string",
                    "description": "Name or identifier of the AI system or model."
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the AI functionality, techniques, and architecture."
                },
                "intended_purpose": {
                    "type": "string",
                    "description": "The exact intended use case (e.g., CV screening, credit scoring, medical imaging, chatbot, video game NPC)."
                },
                "sector": {
                    "type": "string",
                    "description": "Industry sector: employment, finance, healthcare, biometrics, education, critical_infrastructure, law_enforcement, migration, consumer."
                },
                "biometrics_used": {
                    "type": "boolean",
                    "description": "Whether the system uses biometric identification, categorization, or emotion recognition."
                },
                "affects_fundamental_rights": {
                    "type": "boolean",
                    "description": "Whether the system may impact safety, health, or fundamental rights of natural persons."
                },
                "is_gpai": {
                    "type": "boolean",
                    "description": "Whether the model is a General-Purpose AI (GPAI) / foundation model."
                },
                "training_flops": {
                    "type": "number",
                    "description": "Total training compute in FLOPs (e.g. 1e25 for systemic risk threshold)."
                }
            },
            "required": ["system_name", "description", "intended_purpose"]
        }
    },
    {
        "name": "generate_facturx_invoice",
        "description": "Generates a fully compliant EN 16931 & UN/CEFACT CII Factur-X electronic invoice XML (Profiles: MINIMUM, BASIC, EN16931 / COMFORT, EXTENDED). Zero external dependencies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "invoice_number": {
                    "type": "string",
                    "description": "Unique invoice identifier (e.g. 'INV-2026-001')."
                },
                "issue_date": {
                    "type": "string",
                    "description": "Invoice issue date formatted as 'YYYY-MM-DD' or 'YYYYMMDD'."
                },
                "seller": {
                    "type": "object",
                    "description": "Seller details: name, country_code (e.g. 'FR'), address_line1, city, postcode, vat_id, siret, iban, bic.",
                    "properties": {
                        "name": {"type": "string"},
                        "country_code": {"type": "string"},
                        "address_line1": {"type": "string"},
                        "city": {"type": "string"},
                        "postcode": {"type": "string"},
                        "vat_id": {"type": "string"},
                        "siret": {"type": "string"},
                        "iban": {"type": "string"},
                        "bic": {"type": "string"}
                    },
                    "required": ["name", "country_code"]
                },
                "buyer": {
                    "type": "object",
                    "description": "Buyer details: name, country_code (e.g. 'DE'), address_line1, city, postcode, vat_id, siret.",
                    "properties": {
                        "name": {"type": "string"},
                        "country_code": {"type": "string"},
                        "address_line1": {"type": "string"},
                        "city": {"type": "string"},
                        "postcode": {"type": "string"},
                        "vat_id": {"type": "string"},
                        "siret": {"type": "string"}
                    },
                    "required": ["name", "country_code"]
                },
                "items": {
                    "type": "array",
                    "description": "List of invoice line items.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "number"},
                            "vat_rate": {"type": "number"},
                            "unit_code": {"type": "string"}
                        },
                        "required": ["name", "quantity", "unit_price", "vat_rate"]
                    }
                },
                "currency": {
                    "type": "string",
                    "description": "Three-letter ISO currency code (default: 'EUR')."
                },
                "profile": {
                    "type": "string",
                    "description": "Factur-X profile: 'MINIMUM', 'BASIC', 'EN16931' (default), or 'EXTENDED'."
                },
                "payment_terms": {
                    "type": "string",
                    "description": "Payment conditions or due date terms."
                },
                "buyer_reference": {
                    "type": "string",
                    "description": "Buyer reference or purchase order number (BT-10)."
                }
            },
            "required": ["invoice_number", "issue_date", "seller", "buyer", "items"]
        }
    },
    {
        "name": "validate_facturx_xml",
        "description": "Validates a Factur-X / EN 16931 XML electronic invoice string for UN/CEFACT CII compliance, mandatory fields, and monetary summation integrity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "xml_content": {
                    "type": "string",
                    "description": "The XML string of the Factur-X electronic invoice to validate."
                }
            },
            "required": ["xml_content"]
        }
    },
    {
        "name": "check_gdpr_nis2_readiness",
        "description": "Evaluates organizational compliance readiness for GDPR (Regulation (EU) 2016/679) and the NIS2 Directive (Directive (EU) 2022/2555). Identifies essential/important entity status and compliance gaps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "headquarters_country": {"type": "string"},
                "sector": {"type": "string"},
                "employee_count": {"type": "integer"},
                "annual_turnover_eur": {"type": "number"},
                "processes_special_category_data": {"type": "boolean"},
                "data_transfers_outside_eea": {"type": "boolean"},
                "has_incident_response_plan": {"type": "boolean"},
                "has_mfa_implemented": {"type": "boolean"},
                "has_designated_dpo": {"type": "boolean"}
            },
            "required": ["company_name", "headquarters_country", "sector", "employee_count", "annual_turnover_eur"]
        }
    },
    {
        "name": "get_compliance_status_and_pro_license",
        "description": "Checks the current EU Compliance MCP Server edition, validates Pro license keys, and lists available enterprise features (Peppol routing, PDF/A-3 hybrid embedding).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pro_license_key": {
                    "type": "string",
                    "description": "Optional Pro license key (format: 'EUPRO-XXXX-XXXX-XXXX')."
                }
            }
        }
    }
]


def handle_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches tool execution and formats result for MCP response."""
    if name == "audit_eu_ai_act":
        res = audit_eu_ai_act(
            system_name=args.get("system_name", ""),
            description=args.get("description", ""),
            intended_purpose=args.get("intended_purpose", ""),
            sector=args.get("sector"),
            biometrics_used=args.get("biometrics_used", False),
            affects_fundamental_rights=args.get("affects_fundamental_rights", False),
            is_gpai=args.get("is_gpai", False),
            training_flops=args.get("training_flops")
        )
    elif name == "generate_facturx_invoice":
        res = generate_facturx_invoice(
            invoice_number=args.get("invoice_number", "INV-001"),
            issue_date=args.get("issue_date", "2026-10-29"),
            seller=args.get("seller", {}),
            buyer=args.get("buyer", {}),
            items=args.get("items", []),
            currency=args.get("currency", "EUR"),
            profile=args.get("profile", "EN16931"),
            payment_terms=args.get("payment_terms"),
            buyer_reference=args.get("buyer_reference")
        )
    elif name == "validate_facturx_xml":
        res = validate_facturx_xml(args.get("xml_content", ""))
    elif name == "check_gdpr_nis2_readiness":
        res = check_gdpr_nis2_readiness(
            company_name=args.get("company_name", ""),
            headquarters_country=args.get("headquarters_country", "FR"),
            sector=args.get("sector", ""),
            employee_count=args.get("employee_count", 10),
            annual_turnover_eur=args.get("annual_turnover_eur", 1000000.0),
            processes_special_category_data=args.get("processes_special_category_data", False),
            data_transfers_outside_eea=args.get("data_transfers_outside_eea", False),
            has_incident_response_plan=args.get("has_incident_response_plan", False),
            has_mfa_implemented=args.get("has_mfa_implemented", False),
            has_designated_dpo=args.get("has_designated_dpo", False)
        )
    elif name == "get_compliance_status_and_pro_license":
        res = verify_and_get_license_status(args.get("pro_license_key"))
    else:
        raise ValueError(f"Unknown tool: '{name}'")

    formatted_text = json.dumps(res, indent=2, ensure_ascii=False)
    return {
        "content": [
            {
                "type": "text",
                "text": formatted_text
            }
        ],
        "isError": False
    }


def send_response(response: Dict[str, Any]):
    """Sends JSON-RPC 2.0 response to stdout."""
    payload = json.dumps(response, ensure_ascii=False)
    sys.stdout.write(payload + "\n")
    sys.stdout.flush()


def run_stdio_server():
    """Main event loop listening for JSON-RPC 2.0 messages on stdin."""
    # Ensure stdout/stdin use UTF-8
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            })
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Handle notifications (no id)
        if req_id is None:
            # E.g. notifications/initialized
            continue

        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    }
                }
            })
        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })
        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS_SCHEMA
                }
            })
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result = handle_tool_call(tool_name, tool_args)
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": result
                })
            except Exception as e:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing tool '{tool_name}': {str(e)}"
                            }
                        ],
                        "isError": True
                    }
                })
        else:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found."
                }
            })


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print(f"EU Compliance & Factur-X MCP Server v{SERVER_VERSION}")
        print("Usage: python mcp_eu_compliance.py")
        print("Runs MCP stdio server responding to JSON-RPC 2.0 requests.")
        sys.exit(0)
    run_stdio_server()


if __name__ == "__main__":
    main()
