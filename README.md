# Ubuntu 6GHz WiFi Workaround

A lightweight Python watchdog for Ubuntu that automatically fixes 6GHz WiFi connectivity issues.

## The Problem
Many Linux users encounter a 'regulatory domain bug' that prevents 6GHz connections or causes them to drop randomly. This script monitors the connection and enforces the correct settings to keep you connected.

If a driver refuses to connect to 6GHz, it’s often because it hasn't received a "Country Code" from the local Access Point. This script essentially provides the "nudge" the system needs to stay compliant with your hardware's capabilities.

## Features
- **Connectivity Monitoring:** Detects when the 6GHz connection drops.
- **Regulatory Domain Enforcement:** Automatically sets the correct domain to enable 6GHz bands.
- **Auto-Restoration:** Restores the SSID connection if it fails.
- **Systemd Integration:** Includes a service file to run automatically on boot.

## Quick Start
1. Clone the repository.
2. Update `main.py` with `TARGET_SSID` `WIFI_PASSWORD`, `WIFI_INTERFACE`, and `REGION_CODE`.
   <br>OR<br>set the environment variables:
    `ENSURE_6GHZ_TARGET_SSID`, `ENSURE_6GHZ_WIFI_PASSWORD`, `ENSURE_6GHZ_WIFI_INTERFACE`, `ENSURE_6GHZ_REGION_CODE`
4. Install the systemd service using `ensure-6ghz.service`.

## Tags
#linux #ubuntu #wifi-fix #6ghz #network-manager #python #automation

## Disclaimer
**Do not use this script to spoof regulatory domains or bypass local wireless regulations. The author is not responsible for your actions, use cases, or any legal consequences resulting from the use or misuse of this software. Always ensure you are compliant with your local state and federal regulations.**
