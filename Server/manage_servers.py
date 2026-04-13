#!/usr/bin/env python
"""
Server Management Script
Start and stop all servers (excluding speech-to-text) with one command.

Usage:
    python manage_servers.py start    # Start all servers
    python manage_servers.py stop     # Stop all servers
    python manage_servers.py restart  # Restart all servers
    python manage_servers.py status   # Check server status
"""
import sys
import os
import subprocess
import signal
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

# Server configuration - excluding speech_to_text
SERVERS = {
    "master_agent": {
        "script": "start_master_agent.py",
        "port": 9000,
        "name": "Master Agent"
    },
    "decision_agent": {
        "script": "start_decision_agent.py",
        "port": 8004,
        "name": "Decision Agent"
    },
    "policy_eligibility_scanner": {
        "script": "start_policy_eligibility_scanner.py",
        "port": 8006,
        "name": "Policy Eligibility Scanner"
    },
    "quotation_api": {
        "script": "start_quotation_api.py",
        "port": 8009,
        "name": "Quotation API"
    },
    "insights_agent": {
        "script": "start_insights_agent.py",
        "port": 8008,
        "name": "Insights Agent"
    },
    "pdf_extractor": {
        "script": "start_pdf_extractor.py",
        "port": 8007,
        "name": "PDF Extractor"
    },
    "policy_analyzer_mcp": {
        "script": "start_policy_analyzer_mcp.py",
        "port": None,  # MCP server doesn't use HTTP port
        "name": "Policy Analyzer MCP"
    },
    "summary_agent": {
        "script": "start_summary_agent.py",
        "port": 8020,
        "name": "Summary Agent"
    }
}

# PID file to track running servers
PID_FILE = Path(__file__).parent / ".server_pids.json"


def load_pids() -> Dict[str, int]:
    """Load server PIDs from file."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_pids(pids: Dict[str, int]):
    """Save server PIDs to file."""
    try:
        with open(PID_FILE, 'w') as f:
            json.dump(pids, f, indent=2)
    except IOError as e:
        print(f"Error saving PID file: {e}")


def is_process_running(pid: int) -> bool:
    """Check if a process is still running."""
    try:
        if sys.platform == "win32":
            # Windows: Use tasklist to check if process exists
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return str(pid) in result.stdout
        else:
            # Unix-like: Send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError, subprocess.SubprocessError):
        return False


def kill_process(pid: int):
    """Kill a process by PID."""
    try:
        if sys.platform == "win32":
            # Windows: Use taskkill
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            # Unix-like: Send SIGTERM, then SIGKILL if needed
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                if is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    except Exception as e:
        print(f"Error killing process {pid}: {e}")


def start_server(server_key: str, server_config: Dict) -> Optional[int]:
    """Start a single server and return its PID."""
    script_path = Path(__file__).parent / server_config["script"]
    
    if not script_path.exists():
        print(f"⚠️  Warning: {server_config['script']} not found, skipping {server_config['name']}")
        return None
    
    print(f"🚀 Starting {server_config['name']}...")
    
    try:
        # Change to Server directory
        server_dir = Path(__file__).parent
        
        # Start process
        if sys.platform == "win32":
            # Windows: Use CREATE_NEW_CONSOLE to see output in separate windows
            # Or use CREATE_NO_WINDOW for background execution
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(server_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Unix-like: Start in background
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(server_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        pid = process.pid
        print(f"   ✓ {server_config['name']} started (PID: {pid})")
        if server_config.get("port"):
            print(f"   → http://localhost:{server_config['port']}")
        
        return pid
    except Exception as e:
        print(f"   ✗ Failed to start {server_config['name']}: {e}")
        return None


def start_all_servers():
    """Start all servers."""
    print("=" * 80)
    print("Starting All Servers (excluding speech-to-text)")
    print("=" * 80)
    
    pids = {}
    
    for server_key, server_config in SERVERS.items():
        pid = start_server(server_key, server_config)
        if pid:
            pids[server_key] = pid
        time.sleep(0.5)  # Small delay between starts
    
    save_pids(pids)
    
    print("\n" + "=" * 80)
    print(f"✓ Started {len(pids)} server(s)")
    print("=" * 80)
    print("\nTo stop all servers, run: python manage_servers.py stop")


def stop_all_servers():
    """Stop all running servers."""
    print("=" * 80)
    print("Stopping All Servers")
    print("=" * 80)
    
    pids = load_pids()
    
    if not pids:
        print("No servers are currently running (no PID file found).")
        return
    
    stopped = 0
    for server_key, pid in pids.items():
        server_name = SERVERS.get(server_key, {}).get("name", server_key)
        if is_process_running(pid):
            print(f"🛑 Stopping {server_name} (PID: {pid})...")
            kill_process(pid)
            stopped += 1
        else:
            print(f"⚠️  {server_name} (PID: {pid}) is not running")
    
    # Clean up PID file
    if PID_FILE.exists():
        PID_FILE.unlink()
    
    print("\n" + "=" * 80)
    print(f"✓ Stopped {stopped} server(s)")
    print("=" * 80)


def check_status():
    """Check status of all servers."""
    print("=" * 80)
    print("Server Status")
    print("=" * 80)
    
    pids = load_pids()
    
    if not pids:
        print("No servers have been started via this script.")
        print("Run 'python manage_servers.py start' to start servers.")
        return
    
    running = []
    stopped = []
    
    for server_key, pid in pids.items():
        server_config = SERVERS.get(server_key, {})
        server_name = server_config.get("name", server_key)
        
        if is_process_running(pid):
            status = "🟢 RUNNING"
            port_info = f" (Port: {server_config.get('port', 'N/A')})" if server_config.get('port') else ""
            running.append(f"  {status} - {server_name} (PID: {pid}){port_info}")
        else:
            status = "🔴 STOPPED"
            stopped.append(f"  {status} - {server_name} (PID: {pid})")
    
    if running:
        print("\nRunning Servers:")
        for status in running:
            print(status)
    
    if stopped:
        print("\nStopped Servers:")
        for status in stopped:
            print(status)
    
    if not running and not stopped:
        print("No server information available.")
    
    print("=" * 80)


def restart_servers():
    """Restart all servers."""
    print("Restarting all servers...\n")
    stop_all_servers()
    time.sleep(2)  # Wait a bit before restarting
    print()
    start_all_servers()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_all_servers()
    elif command == "stop":
        stop_all_servers()
    elif command == "restart":
        restart_servers()
    elif command == "status":
        check_status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

