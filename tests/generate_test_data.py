#!/usr/bin/env python
"""
Test data generator for Blueprint Graph.

This script generates test data for manual testing of the Blueprint Graph OCSF Detection Engine.
It can generate events in different formats (OCSF, syslog, CEF, LEEF) and send them to the API.
"""
import os
import json
import random
import argparse
import datetime
import requests
from typing import Dict, Any, List


def generate_ip() -> str:
    """Generate a random IP address."""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"


def generate_hostname() -> str:
    """Generate a random hostname."""
    prefixes = ["web", "app", "db", "auth", "api", "mail", "proxy", "dns", "vpn", "fw"]
    domains = ["example.com", "test.org", "acme.co", "internal.net"]
    return f"{random.choice(prefixes)}-{random.randint(1, 99)}.{random.choice(domains)}"


def generate_username() -> str:
    """Generate a random username."""
    first_names = ["john", "jane", "bob", "alice", "dave", "sarah", "mike", "lisa"]
    last_names = ["smith", "jones", "doe", "brown", "wilson", "taylor"]
    return f"{random.choice(first_names)}.{random.choice(last_names)}"


def generate_timestamp() -> str:
    """Generate a random timestamp within the last 24 hours."""
    now = datetime.datetime.now()
    delta = datetime.timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    timestamp = now - delta
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_ocsf_event() -> Dict[str, Any]:
    """Generate a random OCSF event."""
    event_types = [
        {"class_uid": "0001", "category_uid": "0002", "type": "authentication"},
        {"class_uid": "0003", "category_uid": "0001", "type": "process_execution"},
        {"class_uid": "0004", "category_uid": "0002", "type": "network_connection"},
        {"class_uid": "0005", "category_uid": "0003", "type": "privilege_escalation"},
    ]
    
    event_type = random.choice(event_types)
    src_ip = generate_ip()
    dst_ip = generate_ip()
    username = generate_username()
    hostname = generate_hostname()
    
    event = {
        "class_uid": event_type["class_uid"],
        "category_uid": event_type["category_uid"],
        "time": generate_timestamp(),
        "severity": random.randint(1, 10),
        "message": f"Test {event_type['type']} event",
        "metadata": {
            "version": "1.0.0",
            "product": {
                "name": "Test Product",
                "vendor_name": "Test Vendor"
            }
        },
        "src": {
            "id": f"src-{random.randint(1000, 9999)}",
            "type": "IP",
            "ip": src_ip,
            "hostname": hostname
        },
        "dst": {
            "id": f"dst-{random.randint(1000, 9999)}",
            "type": "IP",
            "ip": dst_ip
        },
        "principal": {
            "id": f"user-{random.randint(1000, 9999)}",
            "type": "User",
            "name": username,
            "domain": "test.local"
        }
    }
    
    # Add event-specific fields
    if event_type["type"] == "authentication":
        event["outcome"] = random.choice(["success", "failure"])
        event["auth_type"] = random.choice(["password", "certificate", "token"])
    
    elif event_type["type"] == "process_execution":
        event["process_name"] = random.choice(["cmd.exe", "powershell.exe", "bash", "python", "java"])
        event["process_path"] = f"/usr/bin/{event['process_name']}"
        event["command_line"] = f"{event['process_path']} --arg1 --arg2"
    
    elif event_type["type"] == "network_connection":
        event["protocol"] = random.choice(["TCP", "UDP", "HTTP", "HTTPS"])
        event["src_port"] = random.randint(1024, 65535)
        event["dst_port"] = random.choice([22, 80, 443, 3389, 8080])
        event["bytes_in"] = random.randint(100, 10000)
        event["bytes_out"] = random.randint(100, 10000)
    
    elif event_type["type"] == "privilege_escalation":
        event["user_id_before"] = random.randint(1000, 9999)
        event["user_id_after"] = 0  # Root
        event["privilege_name"] = "root"
    
    return event


def generate_syslog_event() -> Dict[str, Any]:
    """Generate a random syslog event."""
    facilities = [0, 1, 2, 3, 4, 5]  # kern, user, mail, daemon, auth, syslog
    severities = [0, 1, 2, 3, 4, 5, 6, 7]  # emerg, alert, crit, err, warning, notice, info, debug
    
    event = {
        "facility": random.choice(facilities),
        "severity": random.choice(severities),
        "timestamp": generate_timestamp(),
        "hostname": generate_hostname(),
        "message": f"Test syslog message from {generate_hostname()}"
    }
    
    return event


def generate_cef_event() -> Dict[str, Any]:
    """Generate a random CEF event."""
    vendors = ["Cisco", "Palo Alto", "Fortinet", "CheckPoint", "Symantec"]
    products = ["Firewall", "IDS", "IPS", "Antivirus", "WAF"]
    
    event = {
        "deviceVendor": random.choice(vendors),
        "deviceProduct": random.choice(products),
        "deviceVersion": f"{random.randint(1, 10)}.{random.randint(0, 9)}",
        "deviceEventClassId": str(random.randint(100, 999)),
        "name": "Test CEF Event",
        "severity": str(random.randint(1, 10)),
        "deviceReceiptTime": generate_timestamp(),
        "message": "Test CEF message",
        "sourceAddress": generate_ip(),
        "destinationAddress": generate_ip(),
        "sourceUserName": generate_username(),
        "sourceHostName": generate_hostname()
    }
    
    return event


def generate_leef_event() -> Dict[str, Any]:
    """Generate a random LEEF event."""
    vendors = ["IBM", "QRadar", "LogRhythm", "Splunk", "ArcSight"]
    products = ["SIEM", "Log Manager", "Security Analytics", "Threat Manager"]
    
    event = {
        "devname": random.choice(products),
        "devtime": generate_timestamp(),
        "devtype": random.choice(vendors),
        "sev": random.randint(1, 10),
        "msg": "Test LEEF message",
        "vendor": random.choice(vendors),
        "src": generate_ip(),
        "dst": generate_ip(),
        "usrName": generate_username(),
        "hostName": generate_hostname()
    }
    
    return event


def generate_events(count: int, format_type: str) -> List[Dict[str, Any]]:
    """Generate a list of events in the specified format."""
    events = []
    
    for _ in range(count):
        if format_type == "ocsf":
            event = generate_ocsf_event()
        elif format_type == "syslog":
            event = generate_syslog_event()
        elif format_type == "cef":
            event = generate_cef_event()
        elif format_type == "leef":
            event = generate_leef_event()
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        events.append(event)
    
    return events


def save_events_to_file(events: List[Dict[str, Any]], filename: str):
    """Save events to a file."""
    with open(filename, "w") as f:
        json.dump(events, f, indent=2)
    
    print(f"Saved {len(events)} events to {filename}")


def send_events_to_api(events: List[Dict[str, Any]], format_type: str, api_url: str):
    """Send events to the API."""
    success_count = 0
    
    for event in events:
        try:
            payload = {
                "event": event,
                "source_format": format_type
            }
            
            response = requests.post(f"{api_url}/events", json=payload)
            
            if response.status_code == 201:
                success_count += 1
            else:
                print(f"Failed to send event: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error sending event: {str(e)}")
    
    print(f"Successfully sent {success_count} out of {len(events)} events to the API")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate test data for Blueprint Graph")
    parser.add_argument("--count", type=int, default=10, help="Number of events to generate")
    parser.add_argument("--format", type=str, choices=["ocsf", "syslog", "cef", "leef", "all"], default="ocsf", help="Event format")
    parser.add_argument("--output", type=str, help="Output file (optional)")
    parser.add_argument("--api", type=str, help="API URL (optional)")
    
    args = parser.parse_args()
    
    if args.format == "all":
        formats = ["ocsf", "syslog", "cef", "leef"]
        all_events = []
        
        for format_type in formats:
            print(f"Generating {args.count} {format_type} events...")
            events = generate_events(args.count, format_type)
            all_events.extend(events)
            
            if args.api:
                print(f"Sending {format_type} events to API...")
                send_events_to_api(events, format_type, args.api)
        
        if args.output:
            save_events_to_file(all_events, args.output)
    
    else:
        print(f"Generating {args.count} {args.format} events...")
        events = generate_events(args.count, args.format)
        
        if args.output:
            save_events_to_file(events, args.output)
        
        if args.api:
            print(f"Sending events to API...")
            send_events_to_api(events, args.format, args.api)


if __name__ == "__main__":
    main() 