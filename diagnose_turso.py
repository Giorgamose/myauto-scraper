#!/usr/bin/env python3
"""
Turso Connection Diagnostic Tool
Helps troubleshoot 505 errors and database connectivity issues
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.ENDC}\n")

def check_environment():
    """Check environment variables"""
    print_section("1. CHECKING ENVIRONMENT VARIABLES")

    db_url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    if db_url:
        print(f"{Colors.GREEN}[OK] TURSO_DATABASE_URL found{Colors.ENDC}")
        print(f"  URL: {db_url[:50]}...")
    else:
        print(f"{Colors.RED}[FAIL] TURSO_DATABASE_URL not found{Colors.ENDC}")
        return False

    if auth_token:
        print(f"{Colors.GREEN}[OK] TURSO_AUTH_TOKEN found{Colors.ENDC}")
        print(f"  Token: {auth_token[:20]}...")
    else:
        print(f"{Colors.RED}[FAIL] TURSO_AUTH_TOKEN not found{Colors.ENDC}")
        return False

    return True

def check_dependencies():
    """Check required packages"""
    print_section("2. CHECKING DEPENDENCIES")

    required = ['libsql_client', 'certifi', 'dotenv']
    missing = []

    for package in required:
        try:
            if package == 'dotenv':
                from dotenv import load_dotenv
            elif package == 'libsql_client':
                from libsql_client import create_client_sync
            elif package == 'certifi':
                import certifi

            print(f"{Colors.GREEN}[OK] {package} installed{Colors.ENDC}")
        except ImportError:
            print(f"{Colors.RED}[FAIL] {package} NOT installed{Colors.ENDC}")
            missing.append(package)

    if missing:
        print(f"\n{Colors.YELLOW}Install missing packages:{Colors.ENDC}")
        print(f"  pip install {' '.join(missing)}")
        return False

    return True

def check_ssl_certificates():
    """Check SSL certificate configuration"""
    print_section("3. CHECKING SSL CERTIFICATES")

    try:
        import certifi
        cert_file = certifi.where()
        print(f"{Colors.GREEN}[OK] Certifi certificate bundle found{Colors.ENDC}")
        print(f"  Location: {cert_file}")

        # Check if file exists
        if os.path.exists(cert_file):
            size = os.path.getsize(cert_file)
            print(f"{Colors.GREEN}[OK] Certificate file exists ({size} bytes){Colors.ENDC}")
        else:
            print(f"{Colors.RED}[FAIL] Certificate file not found{Colors.ENDC}")
            return False

        return True
    except Exception as e:
        print(f"{Colors.RED}[FAIL] Error checking SSL certificates: {e}{Colors.ENDC}")
        return False

def check_network_connectivity():
    """Check network connectivity"""
    print_section("4. CHECKING NETWORK CONNECTIVITY")

    try:
        import socket
        import urllib.request

        # Test DNS resolution for Turso
        turso_host = "car-listings-giorgamose.aws-eu-west-1.turso.io"
        print(f"Testing DNS resolution for: {turso_host}")

        try:
            ip = socket.gethostbyname(turso_host)
            print(f"{Colors.GREEN}[OK] DNS resolution successful: {ip}{Colors.ENDC}")
        except socket.gaierror as e:
            print(f"{Colors.RED}[FAIL] DNS resolution failed: {e}{Colors.ENDC}")
            return False

        # Test basic connectivity
        print(f"\nTesting basic HTTP connectivity...")
        try:
            response = urllib.request.urlopen('https://www.google.com', timeout=5)
            print(f"{Colors.GREEN}[OK] Internet connectivity OK{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}[WARN] Internet connectivity test failed: {e}{Colors.ENDC}")
            # Don't fail here as it might just be a timeout

        return True
    except Exception as e:
        print(f"{Colors.RED}[FAIL] Network check error: {e}{Colors.ENDC}")
        return False

def test_direct_connection():
    """Test direct Turso connection"""
    print_section("5. TESTING TURSO CONNECTION")

    try:
        from libsql_client import create_client_sync
        import certifi

        # Set SSL certificate
        os.environ['SSL_CERT_FILE'] = certifi.where()

        db_url = os.getenv("TURSO_DATABASE_URL")
        auth_token = os.getenv("TURSO_AUTH_TOKEN")

        if not db_url or not auth_token:
            print(f"{Colors.RED}[FAIL] Database credentials missing{Colors.ENDC}")
            return False

        print(f"Attempting to connect to: {db_url[:50]}...")

        try:
            # Create client with timeout
            client = create_client_sync(
                url=db_url,
                auth_token=auth_token
            )
            print(f"{Colors.GREEN}[OK] Connection successful!{Colors.ENDC}")

            # Try a simple query
            print(f"\nTesting simple query...")
            result = client.execute("SELECT 1 as test")
            print(f"{Colors.GREEN}[OK] Query successful: {result}{Colors.ENDC}")

            return True

        except Exception as e:
            print(f"{Colors.RED}[FAIL] Connection failed: {e}{Colors.ENDC}")
            print(f"\nError details:")
            print(f"  Type: {type(e).__name__}")
            print(f"  Message: {str(e)}")

            # Try to extract more info
            import traceback
            print(f"\nFull traceback:")
            traceback.print_exc()

            return False

    except Exception as e:
        print(f"{Colors.RED}[FAIL] Error during connection test: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False

def test_with_retry():
    """Test connection with retry logic"""
    print_section("6. TESTING WITH RETRY LOGIC")

    try:
        from libsql_client import create_client_sync
        import certifi
        import time

        os.environ['SSL_CERT_FILE'] = certifi.where()

        db_url = os.getenv("TURSO_DATABASE_URL")
        auth_token = os.getenv("TURSO_AUTH_TOKEN")

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            print(f"\nAttempt {attempt + 1}/{max_retries}...")

            try:
                client = create_client_sync(
                    url=db_url,
                    auth_token=auth_token
                )

                result = client.execute("SELECT 1 as test")
                print(f"{Colors.GREEN}[OK] Connection successful on attempt {attempt + 1}!{Colors.ENDC}")
                return True

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"{Colors.YELLOW}[WARN] Attempt {attempt + 1} failed: {e}{Colors.ENDC}")
                    print(f"  Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"{Colors.RED}[FAIL] All {max_retries} attempts failed{Colors.ENDC}")
                    print(f"  Last error: {e}")
                    return False

        return False

    except Exception as e:
        print(f"{Colors.RED}[FAIL] Error: {e}{Colors.ENDC}")
        return False

def get_solutions():
    """Provide solutions based on error"""
    print_section("SOLUTIONS & RECOMMENDATIONS")

    print(f"{Colors.CYAN}For 505 'Invalid response status' errors:{Colors.ENDC}\n")

    solutions = [
        {
            "issue": "SSL/TLS Handshake Failures",
            "solutions": [
                "Install/update certifi: pip install --upgrade certifi",
                "Install/update libsql-client: pip install --upgrade libsql-client",
                "Check your internet connection",
                "Try running from a different network",
            ]
        },
        {
            "issue": "Invalid Database Credentials",
            "solutions": [
                "Verify TURSO_DATABASE_URL is correct",
                "Verify TURSO_AUTH_TOKEN is correct",
                "Check that credentials haven't expired",
                "Generate new credentials from: https://app.turso.tech",
            ]
        },
        {
            "issue": "Rate Limiting",
            "solutions": [
                "Add delays between database operations",
                "Check Turso dashboard for rate limit info",
                "Reduce frequency of database connections",
                "Contact Turso support if limits are too low",
            ]
        },
        {
            "issue": "Network/Firewall Issues",
            "solutions": [
                "Check your firewall settings",
                "Try disabling VPN/proxy temporarily",
                "Check if Turso domain is accessible: ping car-listings-*.turso.io",
                "Contact your network administrator",
            ]
        },
        {
            "issue": "Turso Service Issues",
            "solutions": [
                "Check Turso status page: https://status.turso.tech",
                "Wait a few minutes and retry",
                "Check GitHub Issues: https://github.com/tursodatabase/turso-client-py",
            ]
        }
    ]

    for solution in solutions:
        print(f"{Colors.YELLOW}{solution['issue']}:{Colors.ENDC}")
        for i, sol in enumerate(solution['solutions'], 1):
            print(f"  {i}. {sol}")
        print()

def main():
    """Run all diagnostics"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("Turso Database Connection Diagnostic Tool")
    print("=" * 60)
    print(f"{Colors.ENDC}\n")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    load_dotenv('.env')

    # Run all checks
    results = {
        "Environment Variables": check_environment(),
        "Dependencies": check_dependencies(),
        "SSL Certificates": check_ssl_certificates(),
        "Network Connectivity": check_network_connectivity(),
        "Direct Connection": test_direct_connection(),
        "Retry Logic": test_with_retry(),
    }

    # Summary
    print_section("SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Tests passed: {Colors.GREEN}{passed}/{total}{Colors.ENDC}\n")

    for test, result in results.items():
        status = f"{Colors.GREEN}[OK] PASS{Colors.ENDC}" if result else f"{Colors.RED}[FAIL] FAIL{Colors.ENDC}"
        print(f"  {test}: {status}")

    print()

    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}All tests passed! Database should be working.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some tests failed. See recommendations below.{Colors.ENDC}")
        get_solutions()

    print()
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
