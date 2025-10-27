#!/usr/bin/env python3
"""
Test script to verify all API keys and configurations are set up correctly.
"""

import os
import sys
from dotenv import load_dotenv
import httpx
import json

# Load environment variables
load_dotenv()


def print_status(message, status):
    """Print colored status message."""
    colors = {
        'success': '\033[92m',  # Green
        'error': '\033[91m',    # Red
        'warning': '\033[93m',  # Yellow
        'info': '\033[94m'      # Blue
    }
    reset = '\033[0m'
    symbols = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    print(f"{colors[status]}{symbols[status]} {message}{reset}")


def check_env_vars():
    """Check if all required environment variables are set."""
    print("\n" + "="*50)
    print("🔍 Checking Environment Variables")
    print("="*50)

    required_vars = {
        'WHATSAPP_PHONE_NUMBER_ID': 'WhatsApp Phone Number ID',
        'WHATSAPP_BUSINESS_ACCOUNT_ID': 'WhatsApp Business Account ID',
        'WHATSAPP_ACCESS_TOKEN': 'WhatsApp Access Token',
        'WHATSAPP_VERIFY_TOKEN': 'WhatsApp Verify Token',
        'SERPAPI_API_KEY': 'SerpAPI Key',
        'ANTHROPIC_API_KEY': 'Anthropic API Key'
    }

    all_set = True
    for var, name in required_vars.items():
        value = os.getenv(var)
        if value and value != f"YOUR_{var}":
            print_status(f"{name}: Set", "success")
        else:
            print_status(f"{name}: Not set", "error")
            all_set = False

    return all_set


def test_serpapi():
    """Test SerpAPI connection."""
    print("\n" + "="*50)
    print("🔍 Testing SerpAPI Connection")
    print("="*50)

    api_key = os.getenv('SERPAPI_API_KEY')
    if not api_key or api_key.startswith('YOUR_'):
        print_status("SerpAPI key not configured", "warning")
        return False

    try:
        # Use httpx to test the API
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_maps",
            "q": "restaurant",
            "type": "search",
            "api_key": api_key
        }

        with httpx.Client() as client:
            response = client.get(url, params=params, timeout=10.0)

        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print_status(f"SerpAPI Error: {data['error']}", "error")
                return False
            print_status("SerpAPI connection successful", "success")
            if 'search_metadata' in data:
                print_status(f"Credits used: {data['search_metadata'].get('total_time_taken', 'N/A')}", "info")
            return True
        else:
            print_status(f"SerpAPI returned status {response.status_code}", "error")
            return False

    except Exception as e:
        print_status(f"SerpAPI connection failed: {str(e)}", "error")
        return False


def test_anthropic():
    """Test Anthropic API connection."""
    print("\n" + "="*50)
    print("🤖 Testing Anthropic API Connection")
    print("="*50)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key.startswith('YOUR_'):
        print_status("Anthropic API key not configured", "warning")
        return False

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ]
        )

        if message.content:
            print_status("Anthropic API connection successful", "success")
            print_status(f"Response: {message.content[0].text}", "info")
            return True
        else:
            print_status("Anthropic API returned empty response", "error")
            return False

    except Exception as e:
        print_status(f"Anthropic API connection failed: {str(e)}", "error")
        return False


def test_whatsapp():
    """Test WhatsApp Business API connection."""
    print("\n" + "="*50)
    print("📱 Testing WhatsApp Business API Connection")
    print("="*50)

    phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')

    if not token or token.startswith('YOUR_'):
        print_status("WhatsApp Access Token not configured", "warning")
        return False

    try:
        url = f"https://graph.facebook.com/v18.0/{phone_id}"
        headers = {"Authorization": f"Bearer {token}"}

        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=10.0)

        if response.status_code == 200:
            data = response.json()
            print_status("WhatsApp API connection successful", "success")
            print_status(f"Phone Number: {data.get('display_phone_number', 'N/A')}", "info")
            return True
        else:
            print_status(f"WhatsApp API returned status {response.status_code}", "error")
            try:
                error_data = response.json()
                print_status(f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}", "error")
            except:
                pass
            return False

    except Exception as e:
        print_status(f"WhatsApp API connection failed: {str(e)}", "error")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🤖 WhatsApp Restaurant Assistant - Configuration Test")
    print("="*60)

    # Check environment variables
    env_ok = check_env_vars()

    if not env_ok:
        print("\n" + "="*50)
        print_status("Please configure all required environment variables in .env file", "error")
        print("="*50)
        sys.exit(1)

    # Run API tests
    serpapi_ok = test_serpapi()
    anthropic_ok = test_anthropic()
    whatsapp_ok = test_whatsapp()

    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)

    results = {
        "Environment Variables": env_ok,
        "SerpAPI": serpapi_ok,
        "Anthropic API": anthropic_ok,
        "WhatsApp Business API": whatsapp_ok
    }

    for test, result in results.items():
        status = "success" if result else "error"
        print_status(f"{test}: {'Passed' if result else 'Failed'}", status)

    all_passed = all(results.values())

    print("\n" + "="*50)
    if all_passed:
        print_status("All tests passed! You're ready to start the bot. 🎉", "success")
        print("\nNext steps:")
        print("  1. Start the application: ./setup.sh or ./run_local.sh")
        print("  2. Expose with ngrok: ngrok http 8000")
        print("  3. Configure WhatsApp webhook in Meta Dashboard")
    else:
        print_status("Some tests failed. Please check the configuration.", "error")
        sys.exit(1)
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
