#!/usr/bin/env python3
"""Run Théoria SaaS Desktop Client."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ai_voicer.config import load_config
from ai_voicer.logging_setup import setup_logging
from ai_voicer.daemon_runtime import run_daemon
from ai_voicer.saas_client import SaasAuthManager, SaasTranscriptionService


def show_usage():
    print("""
Théoria SaaS Desktop Client

Usage:
  python run_saas_daemon.py login <email>     Login to Théoria SaaS
  python run_saas_daemon.py logout            Logout and clear credentials
  python run_saas_daemon.py status            Show login status and usage
  python run_saas_daemon.py run               Start the daemon (default)
  python run_saas_daemon.py --help            Show this help

Examples:
  python run_saas_daemon.py login user@example.com
  python run_saas_daemon.py run
""")


def cmd_login(email: str):
    config = load_config()
    auth = SaasAuthManager(config.backend_url or "http://127.0.0.1:8090")
    
    print(f"Logging in as {email}...")
    if auth.login(email):
        print("✅ Login successful!")
        print(f"   Backend: {config.backend_url}")
        
        # Show usage after login
        service = SaasTranscriptionService(config.backend_url, auth)
        try:
            usage = service.get_usage()
            plan = usage.get("plan", {})
            usage_stats = usage.get("usage", {})
            print(f"\n📊 Plan: {plan.get('name', 'Free')}")
            print(f"   Used: {usage_stats.get('used_minutes', 0)} minutes")
            if usage_stats.get('remaining_minutes') is not None:
                print(f"   Remaining: {usage_stats.get('remaining_minutes')} minutes")
        except Exception as e:
            print(f"   (Could not fetch usage: {e})")
    else:
        print("❌ Login failed. Check your email and try again.")
        sys.exit(1)


def cmd_logout():
    config = load_config()
    auth = SaasAuthManager(config.backend_url or "http://127.0.0.1:8090")
    
    if auth.is_logged_in():
        auth.logout()
        print("✅ Logged out successfully.")
    else:
        print("ℹ️  Not logged in.")


def cmd_status():
    config = load_config()
    auth = SaasAuthManager(config.backend_url or "http://127.0.0.1:8090")
    
    print(f"Backend: {config.backend_url}")
    
    if auth.is_logged_in():
        creds = auth._load_credentials()
        print(f"Status: ✅ Logged in as {creds.email}")
        
        # Fetch usage
        service = SaasTranscriptionService(config.backend_url, auth)
        try:
            usage = service.get_usage()
            plan = usage.get("plan", {})
            usage_stats = usage.get("usage", {})
            
            print(f"\n📊 Plan: {plan.get('name', 'Free')}")
            print(f"   Monthly limit: {plan.get('monthly_minutes', 'Unlimited')} minutes")
            print(f"   Used this period: {usage_stats.get('used_minutes', 0)} minutes")
            if usage_stats.get('remaining_minutes') is not None:
                print(f"   Remaining: {usage_stats.get('remaining_minutes')} minutes")
            print(f"   Success rate: {usage.get('success_rate_percent', 0)}%")
        except Exception as e:
            print(f"\n⚠️  Could not fetch usage: {e}")
    else:
        print("Status: ❌ Not logged in")
        print("\nRun: python run_saas_daemon.py login <email>")


def cmd_run():
    config = load_config()
    setup_logging(config.log_level)
    
    # Check login
    auth = SaasAuthManager(config.backend_url or "http://127.0.0.1:8090")
    
    if not auth.is_logged_in():
        print("❌ Not logged in. Please run:")
        print(f"   python run_saas_daemon.py login <email>")
        sys.exit(1)
    
    print(f"✅ Connected as: {auth._load_credentials().email}")
    print(f"🎙️  Starting Théoria SaaS Daemon...")
    print(f"   Hotkey: {config.hotkey}")
    print(f"   Backend: {config.backend_url}")
    print()
    
    service = SaasTranscriptionService(config.backend_url, auth)
    run_daemon(config, service_override=service)


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ("run", "start"):
        cmd_run()
    elif args[0] == "login" and len(args) >= 2:
        cmd_login(args[1])
    elif args[0] == "logout":
        cmd_logout()
    elif args[0] in ("status", "info"):
        cmd_status()
    elif args[0] in ("-h", "--help", "help"):
        show_usage()
    else:
        print(f"Unknown command: {args[0]}")
        show_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
