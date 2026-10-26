#!/usr/bin/env python
"""
scripts/audit_platform.py
Comprehensive platform audit script for InfiniAI and PlatformHub.

Audits:
1. Django System Configuration & Migrations
2. Database Entities & Profiles (18 client accounts, requests, invoices, messages)
3. Live Hosted Showcases (Audrey Brown, DockStream, Orozco Roofing, ApexDesk)
4. Public Deliverable File Integrity (Byte sizes >= 10,240 bytes)
5. PII Masking and Security Handlers
"""

import os
import sys
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from platformhub.models import Deliverable, Invoice, PaymentRecord, ServiceRequest
from humanizer.models import ClientConversation, ClientMessage
from platformhub.chat_files import get_chat_files_dir

def log_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title.upper()}")
    print("=" * 70)

def audit_system_check():
    log_section("1. Django System Check")
    from django.core.management import call_command
    try:
        call_command("check", verbosity=0)
        print("  [PASS] Django system check: 0 errors, 0 silenced warnings.")
    except Exception as e:
        print(f"  [FAIL] Django check failed: {e}")

def audit_database():
    log_section("2. Database Entity Audit")
    User = get_user_model()
    users_count = User.objects.count()
    reqs_count = ServiceRequest.objects.count()
    invs_count = Invoice.objects.count()
    pmts_count = PaymentRecord.objects.count()
    msgs_count = ClientMessage.objects.count()
    convs_count = ClientConversation.objects.count()

    print(f"  Users registered:         {users_count}")
    print(f"  Service requests:         {reqs_count}")
    print(f"  Invoices recorded:        {invs_count}")
    print(f"  Payment records:          {pmts_count}")
    print(f"  Client conversations:     {convs_count}")
    print(f"  Messages in threads:      {msgs_count}")

    if users_count >= 18 and msgs_count >= 200:
        print("  [PASS] Full production orbit dataset loaded.")
    else:
        print("  [WARN] Database may require 'python manage.py seed_orbit_production --reset'.")

def audit_showcases():
    log_section("3. Hosted Showcases & Route Audit")
    client = Client()
    showcases = [
        ("Audrey Brown (Studio Brown)", "/showcase/studio-brown/", "Studio Brown", "Cormorant Garamond"),
        ("Jack Johnson (DockStream)", "/showcase/dockstream/", "DockStream", "Cross-Dock"),
        ("Azael Orozco (Orozco Roofing)", "/showcase/orozco-roofing/", "Orozco", "Commercial Roof Bid Calculator"),
        ("Carter Lemburg (ApexDesk)", "/showcase/apexdesk/", "ApexDesk", "Configure Your Desk Ecosystem"),
    ]

    all_passed = True
    for name, url, term1, term2 in showcases:
        res = client.get(url)
        content = res.content.decode("utf-8")
        status_ok = res.status_code == 200
        terms_ok = term1 in content and term2 in content
        size_kb = len(res.content) / 1024

        status_str = "PASS" if (status_ok and terms_ok) else "FAIL"
        if not (status_ok and terms_ok):
            all_passed = False

        print(f"  [{status_str}] {name:32} -> {res.status_code} ({size_kb:.1f} KB)")
        if not terms_ok:
            print(f"         Missing keywords: '{term1}' in page: {term1 in content}, '{term2}': {term2 in content}")

    if all_passed:
        print("  [PASS] All 4 bespoke showcases live and responding.")

def audit_deliverables():
    log_section("4. Public Deliverable File Integrity Audit")
    files_dir = get_chat_files_dir()
    if not files_dir.exists():
        print("  [FAIL] public/chat_files directory does not exist.")
        return

    files = list(files_dir.glob("*.*"))
    total_files = len(files)
    under_10kb = [f for f in files if f.stat().st_size < 10240]
    total_bytes = sum(f.stat().st_size for f in files)
    avg_kb = (total_bytes / total_files / 1024) if total_files > 0 else 0
    min_kb = min(f.stat().st_size for f in files) / 1024 if total_files > 0 else 0

    print(f"  Total deliverable files:   {total_files}")
    print(f"  Average file size:         {avg_kb:.1f} KB")
    print(f"  Smallest file size:        {min_kb:.1f} KB")
    print(f"  Files under 10 KB (<10240B): {len(under_10kb)}")

    if len(under_10kb) == 0 and total_files >= 90:
        print("  [PASS] 100% of deliverable files satisfy the >= 10 KB mandate.")
    else:
        print(f"  [FAIL] Found {len(under_10kb)} files under 10 KB threshold.")
        for uf in under_10kb:
            print(f"         - {uf.name} ({uf.stat().st_size} bytes)")

def audit_security():
    log_section("5. Security & PII Masking Audit")
    from platformhub.invoice_pdf import mask_name, mask_email
    
    test_cases = [
        ("audreymbrown2007@gmail.com", "a***7@gmail.com"),
        ("Audrey Brown", "Audrey B. [Protected]"),
        ("cruzjose6221@gmail.com", "c***1@gmail.com"),
        ("Jose Cruz", "Jose C. [Protected]"),
    ]
    all_masked = True
    for original, expected in test_cases:
        if "@" in original:
            actual = mask_email(original)
        else:
            actual = mask_name(original)
        if actual != expected:
            all_masked = False
            print(f"  [FAIL] Masking failed for '{original}': expected '{expected}', got '{actual}'")

    if all_masked:
        print("  [PASS] PII masking functions conform to security specifications.")

def main():
    print("=" * 70)
    print("        INFINIAI / PLATFORMBHUB COMPREHENSIVE SYSTEM AUDIT")
    print("=" * 70)
    audit_system_check()
    audit_database()
    audit_showcases()
    audit_deliverables()
    audit_security()
    log_section("Audit Conclusion")
    print("  All operational checks evaluated. Review results above.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
