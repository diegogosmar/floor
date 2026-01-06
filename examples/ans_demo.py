#!/usr/bin/env python3
"""
Demo: ANS (Agent Name Server) Usage

This demonstrates:
1. Publishing agent manifests to ANS
2. Discovering agents by capability
3. Using discovered agents

ANS (Agent Name Server) is like DNS but for OFP agents.
"""

import asyncio
import httpx
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ans.client import ANSClient
from src.ans.models import ManifestData, ConversantIdentification


async def demo_publish_manifest():
    """Demo: Publish an agent manifest"""
    print("\n📤 Demo: Publishing Agent Manifest")
    print("=" * 50)
    
    client = ANSClient("http://localhost:8001")
    
    # Create manifest for a fictional agent
    manifest = ManifestData(
        identification=ConversantIdentification(
            speakerUri="tag:demo.example.com,2025:translation_agent",
            serviceUrl="http://localhost:8002",
            organization="Demo Corp",
            conversationalName="Translation Agent",
            role="Translator",
            synopsis="AI agent for language translation"
        ),
        capabilities=["language_translation", "text_generation"],
        metadata={"model": "gpt-4o-mini", "languages": ["en", "es", "fr", "it"]}
    )
    
    try:
        success = await client.publish_manifest(manifest)
        if success:
            print("✅ Manifest published successfully!")
            print(f"   Speaker URI: {manifest.identification.speakerUri}")
            print(f"   Capabilities: {manifest.capabilities}")
        else:
            print("❌ Failed to publish manifest")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


async def demo_discover_agents():
    """Demo: Discover agents by capability"""
    print("\n🔍 Demo: Discovering Agents")
    print("=" * 50)
    
    client = ANSClient("http://localhost:8001")
    
    try:
        # Search for translation agents
        print("\nSearching for agents with 'language_translation' capability...")
        manifests = await client.search_by_capability("language_translation")
        
        print(f"\n✅ Found {len(manifests)} agent(s):")
        for i, manifest in enumerate(manifests, 1):
            ident = manifest.identification
            print(f"\n{i}. {ident.conversationalName or ident.speakerUri}")
            print(f"   Speaker URI: {ident.speakerUri}")
            print(f"   Service URL: {ident.serviceUrl}")
            print(f"   Organization: {ident.organization}")
            print(f"   Capabilities: {manifest.capabilities}")
            if manifest.metadata:
                print(f"   Metadata: {manifest.metadata}")
        
        # Search for text generation agents
        print("\n\nSearching for agents with 'text_generation' capability...")
        manifests = await client.get_manifests(filters={"capabilities": ["text_generation"]})
        
        print(f"\n✅ Found {len(manifests)} agent(s):")
        for i, manifest in enumerate(manifests, 1):
            ident = manifest.identification
            print(f"{i}. {ident.conversationalName or ident.speakerUri}")
            print(f"   Capabilities: {manifest.capabilities}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()


async def demo_full_workflow():
    """Demo: Full workflow - publish, discover, use"""
    print("\n🔄 Demo: Full Workflow")
    print("=" * 50)
    
    client = ANSClient("http://localhost:8001")
    
    try:
        # Step 1: Publish multiple agent manifests
        print("\n1️⃣ Publishing agent manifests...")
        
        agents = [
            ManifestData(
                identification=ConversantIdentification(
                    speakerUri="tag:demo.example.com,2025:budget_agent",
                    serviceUrl="http://localhost:8003",
                    organization="Demo Corp",
                    conversationalName="Budget Analyst",
                    role="Financial Advisor"
                ),
                capabilities=["financial_analysis", "text_generation"]
            ),
            ManifestData(
                identification=ConversantIdentification(
                    speakerUri="tag:demo.example.com,2025:travel_agent",
                    serviceUrl="http://localhost:8004",
                    organization="Demo Corp",
                    conversationalName="Travel Agent",
                    role="Travel Advisor"
                ),
                capabilities=["travel_planning", "text_generation"]
            ),
        ]
        
        for agent in agents:
            await client.publish_manifest(agent)
            print(f"   ✅ Published: {agent.identification.conversationalName}")
        
        # Step 2: Discover agents
        print("\n2️⃣ Discovering agents...")
        all_agents = await client.get_manifests()
        print(f"   ✅ Found {len(all_agents)} total agents")
        
        # Step 3: Search by specific capability
        print("\n3️⃣ Searching for financial analysis agents...")
        financial_agents = await client.search_by_capability("financial_analysis")
        print(f"   ✅ Found {len(financial_agents)} financial agent(s)")
        
        # Step 4: Use discovered agent
        if financial_agents:
            selected = financial_agents[0]
            print(f"\n4️⃣ Selected agent: {selected.identification.conversationalName}")
            print(f"   Service URL: {selected.identification.serviceUrl}")
            print(f"   Ready to use in conversation!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def main():
    """Run all demos"""
    print("🎨 ANS (Agent Name Server) Demo")
    print("=" * 50)
    print("\n⚠️  Make sure ANS (Agent Name Server) is running:")
    print("   uvicorn src.ans.main:app --port 8001")
    print("\nPress Enter to continue...")
    input()
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health", timeout=5.0)
            if response.status_code != 200:
                print("❌ ANS (Agent Name Server) is not running!")
                return
    except Exception:
        print("❌ Cannot connect to ANS (Agent Name Server)!")
        print("   Start it with: uvicorn src.ans.main:app --port 8001")
        return
    
    # Run demos
    await demo_publish_manifest()
    await asyncio.sleep(1)
    
    await demo_discover_agents()
    await asyncio.sleep(1)
    
    await demo_full_workflow()
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())

