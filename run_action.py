#!/usr/bin/env python3
"""
CI/CD Runner and GitHub Action Adapter for EU Compliance & Factur-X Engine.
Enables headless validation in GitHub Actions, GitLab CI, and local pre-commit hooks.
"""

import os
import sys
import argparse
import glob
from typing import Dict, Any, List

# Import core compliance engines
from mcp_eu_compliance import (
    validate_facturx_xml,
    audit_eu_ai_act,
    check_gdpr_nis2_readiness,
    SERVER_VERSION
)


def export_github_outputs(outputs: Dict[str, str]):
    """Appends key-value pairs to $GITHUB_OUTPUT if running inside GitHub Actions."""
    gh_output_path = os.environ.get("GITHUB_OUTPUT")
    if gh_output_path and os.path.exists(gh_output_path):
        try:
            with open(gh_output_path, "a", encoding="utf-8") as f:
                for k, v in outputs.items():
                    f.write(f"{k}={v}\n")
        except Exception as e:
            sys.stderr.write(f"Notice: Failed to write to GITHUB_OUTPUT: {e}\n")


def export_step_summary(markdown_text: str):
    """Appends Markdown summary to $GITHUB_STEP_SUMMARY if running inside GitHub Actions."""
    gh_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary_path and os.path.exists(gh_summary_path):
        try:
            with open(gh_summary_path, "a", encoding="utf-8") as f:
                f.write(markdown_text)
                f.write("\n")
        except Exception as e:
            sys.stderr.write(f"Notice: Failed to write to GITHUB_STEP_SUMMARY: {e}\n")


def run_facturx_validation(target_path: str) -> Dict[str, Any]:
    """Finds and validates Factur-X / EN 16931 XML files."""
    files_to_check = []
    if os.path.isfile(target_path):
        files_to_check.append(target_path)
    elif os.path.isdir(target_path):
        # Look for *.xml recursively
        files_to_check.extend(glob.glob(os.path.join(target_path, "**", "*.xml"), recursive=True))

    results = []
    total_errors = 0
    total_warnings = 0

    if not files_to_check:
        return {
            "status": "WARNING",
            "message": f"No XML invoice files found in target path: {target_path}",
            "files": [],
            "error_count": 0,
            "warning_count": 0
        }

    for fpath in files_to_check:
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            # Only validate if looks like UN/CEFACT CII invoice
            if "CrossIndustryInvoice" in content:
                res = validate_facturx_xml(content)
                res["file_path"] = fpath
                results.append(res)
                if not res.get("is_valid", False):
                    total_errors += len(res.get("errors", []))
                total_warnings += len(res.get("warnings", []))
        except Exception as e:
            results.append({
                "file_path": fpath,
                "is_valid": False,
                "errors": [f"Could not read file: {e}"],
                "warnings": [],
                "details": {}
            })
            total_errors += 1

    overall_status = "COMPLIANT" if total_errors == 0 else "NON_COMPLIANT"
    return {
        "status": overall_status,
        "results": results,
        "files_checked": len(results),
        "error_count": total_errors,
        "warning_count": total_warnings
    }


def generate_facturx_report_md(report: Dict[str, Any]) -> str:
    lines = [
        "# 🇪🇺 Factur-X / EN 16931 Electronic Invoice Validation Report",
        "",
        f"> **Auditor Engine**: `mcp-eu-compliance v{SERVER_VERSION}`",
        f"> **Status**: **{report['status']}** | **Invoices Checked**: `{report.get('files_checked', 0)}` | **Errors**: `{report.get('error_count', 0)}` | **Warnings**: `{report.get('warning_count', 0)}`",
        "",
        "---",
        ""
    ]

    if not report.get("results"):
        lines.append(f"⚠️ {report.get('message', 'No Factur-X invoices discovered.')}")
        return "\n".join(lines)

    lines.append("| Invoice File | Profile | Number | Status | Errors | Warnings |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for res in report.get("results", []):
        fpath = os.path.basename(res.get("file_path", "unknown"))
        details = res.get("details", {})
        prof = details.get("profile_name", "UNKNOWN")
        inv_no = details.get("invoice_number", "N/A")
        is_val = "✅ PASS" if res.get("is_valid") else "❌ FAIL"
        errs = len(res.get("errors", []))
        warns = len(res.get("warnings", []))
        lines.append(f"| `{fpath}` | {prof} | `{inv_no}` | {is_val} | {errs} | {warns} |")

    lines.append("")
    # Detail failures
    for res in report.get("results", []):
        if not res.get("is_valid"):
            lines.append(f"### ❌ Issues in `{res.get('file_path')}`")
            for err in res.get("errors", []):
                lines.append(f"- **Error**: {err}")
            for w in res.get("warnings", []):
                lines.append(f"- **Warning**: {w}")
            lines.append("")

    lines.append("---")
    lines.append("Need enterprise Peppol BIS Billing 3.0 routing & automated PDF/A-3 hybrid compilation?")
    lines.append("👉 **Upgrade to Pro**: [https://eroniichan.github.io/eu-ai-act-compliance-toolkit/](https://eroniichan.github.io/eu-ai-act-compliance-toolkit/)")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="EU Compliance & Factur-X Action Runner")
    parser.add_argument("--mode", default="validate-facturx", choices=["validate-facturx", "audit-ai", "check-nis2"], help="Audit mode")
    parser.add_argument("--path", default=".", help="Path to XML file, directory, or codebase")
    parser.add_argument("--output", default="eu-compliance-report.md", help="Path to write report markdown")
    parser.add_argument("--fail-on-error", default="true", help="Fail with exit code 1 if errors found (true/false)")
    parser.add_argument("--system-name", default="AI Application", help="AI system name for AI Act mode")
    parser.add_argument("--purpose", default="General automated processing", help="AI system purpose")
    parser.add_argument("--domain", default="general", help="Domain / sector for AI audit")
    parser.add_argument("--sector", default="digital_infrastructure", help="Sector for NIS2 check")
    parser.add_argument("--employees", type=int, default=50, help="Employee headcount for NIS2")
    parser.add_argument("--turnover", type=float, default=15_000_000.0, help="Annual turnover in EUR for NIS2")

    args = parser.parse_args()

    fail_on = args.fail_on_error.lower() in ("true", "1", "yes")

    if args.mode == "validate-facturx":
        report = run_facturx_validation(args.path)
        md_text = generate_facturx_report_md(report)
        status = report["status"]
        issues_count = str(report["error_count"])
    elif args.mode == "audit-ai":
        res = audit_eu_ai_act(
            system_name=args.system_name,
            intended_purpose=args.purpose,
            domain=args.domain,
            capabilities=["automated-reasoning"],
            scans_codebase_path=args.path if os.path.exists(args.path) else None
        )
        status = res.get("risk_tier", "MINIMAL_RISK")
        issues_count = str(len(res.get("identified_triggers", [])))
        md_text = f"# 🇪🇺 EU AI Act Compliance Evaluation\n\n- **System**: {args.system_name}\n- **Assessed Risk Tier**: **{status}**\n- **Legal Basis**: {res.get('legal_basis', 'N/A')}\n- **Triggers**: `{issues_count}`\n\n{res.get('summary', '')}"
    else: # check-nis2
        res = check_gdpr_nis2_readiness(
            sector=args.sector,
            headcount=args.employees,
            annual_turnover_eur=args.turnover,
            has_incident_plan=True,
            processes_health_or_biometrics=False,
            dpo_appointed=False
        )
        status = res.get("nis2_classification", "OUT_OF_SCOPE")
        issues_count = str(len(res.get("critical_gaps", [])))
        md_text = f"# 🇪🇺 NIS2 & GDPR Readiness Assessment\n\n- **Sector**: {args.sector}\n- **NIS2 Status**: **{status}**\n- **Critical Gaps**: `{issues_count}`\n- **Summary**: {res.get('summary', '')}"

    # Save report
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(md_text)
            print(f"Report successfully saved to {args.output}")
        except Exception as e:
            print(f"Warning: Could not save report file: {e}")

    # GitHub Action Integration
    export_github_outputs({
        "compliance-status": status,
        "issues-count": issues_count,
        "report-path": args.output
    })
    export_step_summary(md_text)

    print(f"\n[mcp-eu-compliance] Execution finished: status={status}, issues={issues_count}")

    if fail_on and status in ("NON_COMPLIANT", "PROHIBITED", "HIGH_RISK"):
        print("Failing build due to compliance violations or validation errors.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
