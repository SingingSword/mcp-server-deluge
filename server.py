#!/usr/bin/env python3
"""
Deluge MCP Server - Provides torrent management capabilities via Deluge Web API
"""

import os
import requests
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Deluge Torrent Manager")

# Global session for maintaining cookies
session = requests.Session()

def get_deluge_config():
    """Get Deluge configuration from environment variables"""
    url = os.getenv("DELUGE_URL")
    password = os.getenv("DELUGE_PASSWORD")
    
    if not url:
        raise ValueError("DELUGE_URL environment variable is required")
    if not password:
        raise ValueError("DELUGE_PASSWORD environment variable is required")
    
    return url, password

def deluge_request(method: str, params: List[Any], request_id: int = 1) -> Dict:
    """Make a request to Deluge JSON-RPC API"""
    url, _ = get_deluge_config()
    data = {"method": method, "params": params, "id": request_id}
    response = session.post(url, json=data)
    return response.json()

def ensure_authenticated():
    """Ensure we're authenticated with Deluge"""
    _, password = get_deluge_config()
    result = deluge_request("auth.login", [password])
    if not result.get("result"):
        raise Exception("Failed to authenticate with Deluge")

@mcp.tool()
def list_torrents() -> Dict:
    """Get list of all torrents with their status"""
    ensure_authenticated()
    result = deluge_request("web.update_ui", [
        ["name", "state", "progress", "download_payload_rate", "upload_payload_rate", "eta", "total_size"],
        {}
    ])
    
    if result.get("result") and result["result"].get("torrents"):
        torrents = result["result"]["torrents"]
        formatted = []
        for torrent_id, data in torrents.items():
            formatted.append({
                "id": torrent_id,
                "name": data.get("name", "Unknown"),
                "state": data.get("state", "Unknown"),
                "progress": f"{data.get('progress', 0):.1f}%",
                "download_speed": f"{data.get('download_payload_rate', 0)/1024:.1f} KB/s",
                "upload_speed": f"{data.get('upload_payload_rate', 0)/1024:.1f} KB/s"
            })
        return {"torrents": formatted, "count": len(formatted)}
    return {"torrents": [], "count": 0}

@mcp.tool()
def add_magnet(magnet_uri: str) -> Dict:
    """Add a torrent via magnet link"""
    ensure_authenticated()
    result = deluge_request("core.add_torrent_magnet", [magnet_uri, {}])
    
    if result.get("result"):
        return {"success": True, "torrent_id": result["result"], "message": "Torrent added successfully"}
    else:
        return {"success": False, "error": result.get("error", "Unknown error")}

@mcp.tool()
def pause_torrent(torrent_id: str) -> Dict:
    """Pause a torrent by ID"""
    ensure_authenticated()
    result = deluge_request("core.pause_torrent", [[torrent_id]])
    
    if result.get("error") is None:
        return {"success": True, "message": f"Torrent {torrent_id} paused"}
    else:
        return {"success": False, "error": result.get("error")}

@mcp.tool()
def resume_torrent(torrent_id: str) -> Dict:
    """Resume a torrent by ID"""
    ensure_authenticated()
    result = deluge_request("core.resume_torrent", [[torrent_id]])
    
    if result.get("error") is None:
        return {"success": True, "message": f"Torrent {torrent_id} resumed"}
    else:
        return {"success": False, "error": result.get("error")}

@mcp.tool()
def remove_torrent(torrent_id: str, remove_data: bool = False) -> Dict:
    """Remove a torrent by ID, optionally removing downloaded data"""
    ensure_authenticated()
    result = deluge_request("core.remove_torrent", [torrent_id, remove_data])
    
    if result.get("result"):
        action = "and data" if remove_data else ""
        return {"success": True, "message": f"Torrent {torrent_id} removed {action}"}
    else:
        return {"success": False, "error": result.get("error", "Failed to remove torrent")}

@mcp.tool()
def get_deluge_stats() -> Dict:
    """Get Deluge daemon statistics"""
    ensure_authenticated()
    result = deluge_request("web.update_ui", [[], {}])
    
    if result.get("result"):
        stats = result["result"].get("stats", {})
        return {
            "connected": result["result"].get("connected", False),
            "download_rate": f"{stats.get('download_rate', 0)/1024:.1f} KB/s",
            "upload_rate": f"{stats.get('upload_rate', 0)/1024:.1f} KB/s",
            "num_connections": stats.get("num_connections", 0),
            "dht_nodes": stats.get("dht_nodes", 0),
            "free_space": f"{stats.get('free_space', 0)/(1024**3):.1f} GB"
        }
    return {"error": "Failed to get stats"}

if __name__ == "__main__":
    try:
        # Check environment variables
        url, password = get_deluge_config()
        print(f"Deluge URL: {url}")
        print("Password: configured")
        
        # Run the MCP server
        mcp.run()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set DELUGE_URL and DELUGE_PASSWORD environment variables")
        exit(1)
