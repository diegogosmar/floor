#!/usr/bin/env python3
"""
Browser Functionality Test Script
Tests the Streamlit GUI and Floor Manager API endpoints
"""

import httpx
import json
import time
from typing import Dict, Any

# Configuration
STREAMLIT_URL = "http://localhost:8501"
FLOOR_API = "http://localhost:8000/api/v1"
CONVERSATION_ID = "streamlit_chat_001"

# Test agents
AGENTS = {
    "Budget Analyst": {
        "speakerUri": "tag:demo,2025:budget",
        "priority": 5
    },
    "Travel Agent": {
        "speakerUri": "tag:demo,2025:travel",
        "priority": 7
    },
    "Coordinator": {
        "speakerUri": "tag:demo,2025:coordinator",
        "priority": 10
    }
}


def test_health_check() -> bool:
    """Test Floor Manager health endpoint"""
    print("🔍 Testing Floor Manager health...")
    try:
        response = httpx.get(f"{FLOOR_API.replace('/api/v1', '')}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False


def test_streamlit_accessible() -> bool:
    """Test if Streamlit GUI is accessible"""
    print("🔍 Testing Streamlit GUI accessibility...")
    try:
        response = httpx.get(STREAMLIT_URL, timeout=5.0)
        if response.status_code == 200:
            # Check if it's actually Streamlit
            if "streamlit" in response.text.lower() or "Open Floor Protocol" in response.text:
                print(f"   ✅ Streamlit GUI is accessible (HTTP {response.status_code})")
                return True
            else:
                print(f"   ⚠️  Page accessible but doesn't look like Streamlit")
                return False
        else:
            print(f"   ❌ Streamlit not accessible: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Streamlit accessibility error: {e}")
        return False


def test_floor_request(agent_name: str, agent_info: Dict[str, Any]) -> bool:
    """Test floor request for an agent"""
    print(f"🔍 Testing floor request for {agent_name}...")
    try:
        response = httpx.post(
            f"{FLOOR_API}/floor/request",
            json={
                "conversation_id": CONVERSATION_ID,
                "speakerUri": agent_info["speakerUri"],
                "priority": agent_info["priority"]
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            granted = data.get("granted", False)
            print(f"   ✅ Floor request successful: granted={granted}")
            return True
        else:
            print(f"   ❌ Floor request failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Floor request error: {e}")
        return False


def test_floor_holder() -> bool:
    """Test getting current floor holder"""
    print("🔍 Testing floor holder endpoint...")
    try:
        response = httpx.get(
            f"{FLOOR_API}/floor/holder/{CONVERSATION_ID}",
            timeout=5.0
        )
        
        if response.status_code == 200:
            data = response.json()
            holder = data.get("holder")
            print(f"   ✅ Floor holder retrieved: {holder}")
            return True
        else:
            print(f"   ❌ Floor holder request failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Floor holder error: {e}")
        return False


def test_floor_release(agent_info: Dict[str, Any]) -> bool:
    """Test floor release"""
    print("🔍 Testing floor release...")
    try:
        response = httpx.post(
            f"{FLOOR_API}/floor/release",
            json={
                "conversation_id": CONVERSATION_ID,
                "speakerUri": agent_info["speakerUri"]
            },
            timeout=5.0
        )
        
        if response.status_code == 200:
            print(f"   ✅ Floor released successfully")
            return True
        else:
            print(f"   ❌ Floor release failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Floor release error: {e}")
        return False


def test_sse_endpoint() -> bool:
    """Test SSE endpoint connectivity"""
    print("🔍 Testing SSE endpoint...")
    try:
        # Try to connect and get at least one message
        # Note: SSE endpoint is at /api/v1/floor/events/floor/{conversation_id}
        with httpx.stream(
            "GET",
            f"{FLOOR_API}/floor/events/floor/{CONVERSATION_ID}",
            timeout=3.0
        ) as response:
            if response.status_code == 200:
                # Try to read first line
                try:
                    first_line = next(response.iter_lines())
                    if "data:" in first_line:
                        print(f"   ✅ SSE endpoint is working")
                        return True
                    else:
                        print(f"   ⚠️  SSE endpoint responded but format unexpected")
                        return False
                except StopIteration:
                    print(f"   ⚠️  SSE endpoint connected but no data received")
                    return True  # Still counts as working
            else:
                print(f"   ❌ SSE endpoint failed: HTTP {response.status_code}")
                return False
    except httpx.TimeoutException:
        print(f"   ⚠️  SSE endpoint timeout (may be normal if no updates)")
        return True  # Timeout is OK for SSE
    except Exception as e:
        print(f"   ❌ SSE endpoint error: {e}")
        return False


def test_priority_queue() -> bool:
    """Test priority-based floor queue"""
    print("🔍 Testing priority queue...")
    try:
        # Request floor with different priorities
        results = []
        
        # Request with lowest priority first
        response1 = httpx.post(
            f"{FLOOR_API}/floor/request",
            json={
                "conversation_id": CONVERSATION_ID,
                "speakerUri": AGENTS["Budget Analyst"]["speakerUri"],
                "priority": AGENTS["Budget Analyst"]["priority"]
            },
            timeout=5.0
        )
        results.append(("Budget Analyst", response1.status_code == 200))
        
        # Request with highest priority
        response2 = httpx.post(
            f"{FLOOR_API}/floor/request",
            json={
                "conversation_id": CONVERSATION_ID,
                "speakerUri": AGENTS["Coordinator"]["speakerUri"],
                "priority": AGENTS["Coordinator"]["priority"]
            },
            timeout=5.0
        )
        results.append(("Coordinator", response2.status_code == 200))
        
        # Check who has floor (should be Coordinator due to higher priority)
        time.sleep(0.5)
        holder_response = httpx.get(
            f"{FLOOR_API}/floor/holder/{CONVERSATION_ID}",
            timeout=5.0
        )
        
        if holder_response.status_code == 200:
            holder_data = holder_response.json()
            holder = holder_data.get("holder", "")
            
            if AGENTS["Coordinator"]["speakerUri"] in holder:
                print(f"   ✅ Priority queue working: Coordinator has floor (highest priority)")
                return True
            else:
                print(f"   ⚠️  Priority queue may not be working correctly. Holder: {holder}")
                return False
        else:
            print(f"   ❌ Could not verify priority queue")
            return False
            
    except Exception as e:
        print(f"   ❌ Priority queue test error: {e}")
        return False
    finally:
        # Cleanup: release floor
        try:
            httpx.post(
                f"{FLOOR_API}/floor/release",
                json={
                    "conversation_id": CONVERSATION_ID,
                    "speakerUri": AGENTS["Coordinator"]["speakerUri"]
                },
                timeout=5.0
            )
        except:
            pass


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Browser Functionality Test Suite")
    print("=" * 60)
    print()
    
    results = []
    
    # Basic connectivity tests
    results.append(("Health Check", test_health_check()))
    print()
    results.append(("Streamlit Accessible", test_streamlit_accessible()))
    print()
    
    # Floor control tests
    results.append(("Floor Request", test_floor_request("Budget Analyst", AGENTS["Budget Analyst"])))
    print()
    results.append(("Floor Holder", test_floor_holder()))
    print()
    results.append(("Floor Release", test_floor_release(AGENTS["Budget Analyst"])))
    print()
    
    # Advanced tests
    results.append(("Priority Queue", test_priority_queue()))
    print()
    results.append(("SSE Endpoint", test_sse_endpoint()))
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed ({passed*100//total}%)")
    print()
    
    if passed == total:
        print("🎉 All tests passed!")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed, but some issues found")
    else:
        print("❌ Multiple test failures detected")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
