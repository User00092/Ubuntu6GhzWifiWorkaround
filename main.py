#!/usr/bin/env python3

import subprocess
import time
import socket

# Configuration
TARGET_SSID     = "YOUR_SSID"
WIFI_PASSWORD   = "YOUR_PASSWORD"
WIFI_INTERFACE  = "YOUR_INTERFACE"
POLL_INTERVAL   = 5
REGION_CODE     = "YOUR_REGION_CODE"
CONNECT_TIMEOUT = 30

def run(cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    print("$ %s", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def is_on_ethernet():
    # https://wiki.archlinux.org/title/Talk:NetworkManager
    result = run(["nmcli", "-t", "-f", "TYPE,STATE", "device"], timeout=5)

    # looks like: "ethernet:connected\nwifi:disconnected\nloopback:unmanaged"
    lines = result.stdout.strip().split('\n')
    return any(line == "ethernet:connected" for line in lines)


def get_current_ssid():
    # Sometimes maybe good, sometimes maybe sh*t
    for attempt in range(3):
        # This works... sometimes? idk man
        # https://askubuntu.com/questions/117065/how-do-i-find-out-the-name-of-the-ssid-im-connected-to-from-the-command-line
        try:
            result = run(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], timeout=5)
            for line in result.stdout.splitlines():
                if line.startswith("yes:"):
                    ssid = line.split(":", 1)[1].strip()
                    if ssid:
                        return ssid
        except Exception as e:
            print("nmcli SSID check failed: %s", e)

    return None


def has_internet(host: str = "8.8.8.8", port: int = 53, timeout: int = 3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def restart_network_manager(*, wait: bool = True):
    run(["sudo", "systemctl", "restart", "NetworkManager"], timeout=15)

    if not wait:
        return True

    start_time = time.time()
    while time.time() - start_time < CONNECT_TIMEOUT:
        res = run(["nmcli", "networking", "connectivity"], timeout=5)

        if "full" in res.stdout.strip():
            return True

        time.sleep(1)

    return False

def reconnect():
    print(f"{'-'*10}Starting reconnect sequence{'-'*10}")

    print("Setting WiFi regulatory domain to %s", REGION_CODE)
    result = run(["iw", "reg", "set", REGION_CODE])
    if result.returncode != 0:
        print("iw reg set returned %d: %s", result.returncode, result.stderr.strip())

    print("\tRestarting NetworkManager...")
    restart_network_manager()
    print("\tNetworkManager connectivity is fully active.")

    print("Sleeping 5s to allow for system updates...")
    time.sleep(5)

    print("Bringing up connection '%s' ...", TARGET_SSID)
    cmd = ["nmcli", "dev", "wifi", "connect", TARGET_SSID, "password", WIFI_PASSWORD]
    result = run(cmd, timeout=CONNECT_TIMEOUT)

    if result.returncode != 0:
        print("Direct connect failed, attempting profile-based up...")
        result = run(["nmcli", "con", "up", TARGET_SSID], timeout=CONNECT_TIMEOUT)

    if result.returncode == 0:
        print("Connected successfully")
    else:
        print("Connection failed (returncode %d): %s", result.returncode, result.stderr.strip())

    print(f"{'-'*10}Reconnect sequence finished{'-'*10}")


def check_and_fix():
    if is_on_ethernet():
        print("On Ethernet - skipping WiFi checks.")
        return True

    ssid = get_current_ssid()
    online = has_internet()

    print("Status  SSID='%s'  internet=%s", ssid or "(none)", online)

    if ssid == TARGET_SSID and online:
        print("All good.")
        return True

    if ssid != TARGET_SSID:
        print("Wrong/missing SSID (got '%s', want '%s'). Reconnecting...", ssid, TARGET_SSID)
    else:
        print("On correct SSID but no internet. Reconnecting...")

    reconnect()
    return False


def main():
    print("wifi_watchdog starting. Target SSID: '%s', poll interval: %ds", TARGET_SSID, POLL_INTERVAL)

    check_and_fix()

    while True:
        time.sleep(POLL_INTERVAL)
        try:
            check_and_fix()
        except Exception as e:
            print("Unexpected error in check loop: %s", e)


if __name__ == "__main__":
    main()
