"""
Demo Agents - Esempi di agenti per testare il Floor Manager
"""

import asyncio
import httpx
import json
from typing import Optional
from datetime import datetime


class DemoAgent:
    """
    Agente demo che si connette al Floor Manager via REST API
    """

    def __init__(
        self,
        speaker_uri: str,
        agent_name: str,
        capabilities: list[str],
        floor_api_url: str = "http://localhost:8000",
        service_url: Optional[str] = None
    ):
        self.speaker_uri = speaker_uri
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.floor_api_url = floor_api_url
        self.service_url = service_url or f"http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def register(self) -> bool:
        """Registra l'agente nel registry"""
        try:
            response = await self.client.post(
                f"{self.floor_api_url}/api/v1/agents/register",
                json={
                    "speakerUri": self.speaker_uri,
                    "agent_name": self.agent_name,
                    "capabilities": self.capabilities,
                    "serviceUrl": self.service_url
                }
            )
            response.raise_for_status()
            print(f"✅ {self.agent_name} registrato con successo")
            return True
        except Exception as e:
            print(f"❌ Errore registrazione {self.agent_name}: {e}")
            return False

    async def request_floor(self, conversation_id: str, priority: int = 5) -> bool:
        """Richiedi floor per una conversazione"""
        try:
            response = await self.client.post(
                f"{self.floor_api_url}/api/v1/floor/request",
                json={
                    "conversation_id": conversation_id,
                    "speakerUri": self.speaker_uri,
                    "priority": priority
                }
            )
            response.raise_for_status()
            data = response.json()
            if data.get("granted"):
                print(f"🎤 {self.agent_name} ha ottenuto il floor")
            else:
                print(f"⏳ {self.agent_name} è in coda per il floor")
            return data.get("granted", False)
        except Exception as e:
            print(f"❌ Errore richiesta floor {self.agent_name}: {e}")
            return False

    async def release_floor(self, conversation_id: str) -> bool:
        """Rilascia il floor"""
        try:
            response = await self.client.post(
                f"{self.floor_api_url}/api/v1/floor/release",
                json={
                    "conversation_id": conversation_id,
                    "speakerUri": self.speaker_uri
                }
            )
            response.raise_for_status()
            print(f"🔓 {self.agent_name} ha rilasciato il floor")
            return True
        except Exception as e:
            print(f"❌ Errore release floor {self.agent_name}: {e}")
            return False

    async def send_utterance(
        self,
        conversation_id: str,
        target_speaker_uri: Optional[str],
        text: str
    ) -> bool:
        """Invia un utterance"""
        try:
            response = await self.client.post(
                f"{self.floor_api_url}/api/v1/envelopes/utterance",
                json={
                    "conversation_id": conversation_id,
                    "sender_speakerUri": self.speaker_uri,
                    "target_speakerUri": target_speaker_uri,
                    "text": text
                }
            )
            response.raise_for_status()
            print(f"💬 {self.agent_name}: {text}")
            return True
        except Exception as e:
            print(f"❌ Errore invio utterance {self.agent_name}: {e}")
            return False

    async def get_floor_holder(self, conversation_id: str) -> Optional[str]:
        """Ottieni chi ha il floor"""
        try:
            response = await self.client.get(
                f"{self.floor_api_url}/api/v1/floor/holder/{conversation_id}"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("holder")
        except Exception as e:
            print(f"❌ Errore get floor holder: {e}")
            return None

    async def heartbeat(self) -> bool:
        """Aggiorna heartbeat"""
        try:
            response = await self.client.post(
                f"{self.floor_api_url}/api/v1/agents/heartbeat",
                json={"speakerUri": self.speaker_uri}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            return False

    async def close(self):
        """Chiudi connessione"""
        await self.client.aclose()


async def demo_multi_agent_conversation():
    """
    Demo: Conversazione multi-agente con floor control
    """
    print("=" * 60)
    print("DEMO: Conversazione Multi-Agente con Floor Control")
    print("=" * 60)
    print()

    # Crea agenti demo
    text_agent = DemoAgent(
        speaker_uri="tag:demo.com,2025:text_agent",
        agent_name="Text Agent",
        capabilities=["text_generation"]
    )

    image_agent = DemoAgent(
        speaker_uri="tag:demo.com,2025:image_agent",
        agent_name="Image Agent",
        capabilities=["image_generation"]
    )

    data_agent = DemoAgent(
        speaker_uri="tag:demo.com,2025:data_agent",
        agent_name="Data Agent",
        capabilities=["data_analysis"]
    )

    conversation_id = f"conv_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # Registra agenti
        print("📝 Registrazione agenti...")
        await text_agent.register()
        await image_agent.register()
        await data_agent.register()
        print()

        # Test floor control
        print("🎤 Test Floor Control:")
        print("-" * 60)

        # Agent 1 richiede floor
        print("\n1. Text Agent richiede floor (priority 5)...")
        await text_agent.request_floor(conversation_id, priority=5)
        holder = await text_agent.get_floor_holder(conversation_id)
        print(f"   Floor holder: {holder}")

        # Agent 2 richiede floor (sarà in coda)
        print("\n2. Image Agent richiede floor (priority 3)...")
        await image_agent.request_floor(conversation_id, priority=3)
        holder = await text_agent.get_floor_holder(conversation_id)
        print(f"   Floor holder: {holder}")

        # Agent 3 richiede floor (sarà in coda)
        print("\n3. Data Agent richiede floor (priority 4)...")
        await data_agent.request_floor(conversation_id, priority=4)
        holder = await text_agent.get_floor_holder(conversation_id)
        print(f"   Floor holder: {holder}")

        # Agent 1 invia utterance
        print("\n4. Text Agent invia utterance...")
        await text_agent.send_utterance(
            conversation_id,
            image_agent.speaker_uri,
            "Ciao Image Agent, puoi generare un'immagine?"
        )

        # Agent 1 rilascia floor
        print("\n5. Text Agent rilascia floor...")
        await text_agent.release_floor(conversation_id)
        await asyncio.sleep(1)  # Attendi processamento coda
        holder = await text_agent.get_floor_holder(conversation_id)
        print(f"   Nuovo floor holder: {holder}")

        # Agent con floor invia utterance
        if holder:
            print(f"\n6. {holder} invia utterance...")
            if holder == image_agent.speaker_uri:
                await image_agent.send_utterance(
                    conversation_id,
                    None,  # Broadcast
                    "Certamente! Sto generando l'immagine..."
                )
            elif holder == data_agent.speaker_uri:
                await data_agent.send_utterance(
                    conversation_id,
                    None,
                    "Posso analizzare i dati se necessario..."
                )

        print("\n" + "=" * 60)
        print("✅ Demo completata con successo!")
        print("=" * 60)

    finally:
        # Cleanup
        await text_agent.close()
        await image_agent.close()
        await data_agent.close()


async def demo_floor_priority():
    """
    Demo: Test priorità nel floor control
    """
    print("=" * 60)
    print("DEMO: Test Priorità Floor Control")
    print("=" * 60)
    print()

    agent1 = DemoAgent(
        speaker_uri="tag:demo.com,2025:agent_1",
        agent_name="Agent 1 (Priority 3)",
        capabilities=["text_generation"]
    )

    agent2 = DemoAgent(
        speaker_uri="tag:demo.com,2025:agent_2",
        agent_name="Agent 2 (Priority 5)",
        capabilities=["text_generation"]
    )

    conversation_id = f"conv_priority_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        await agent1.register()
        await agent2.register()

        print("Agent 1 richiede floor con priority 3...")
        await agent1.request_floor(conversation_id, priority=3)
        await asyncio.sleep(0.5)

        print("Agent 2 richiede floor con priority 5 (più alta)...")
        await agent2.request_floor(conversation_id, priority=5)
        await asyncio.sleep(0.5)

        holder = await agent1.get_floor_holder(conversation_id)
        print(f"\nFloor holder attuale: {holder}")
        print("Nota: Agent 2 ha priority più alta ma Agent 1 ha già il floor")

        print("\nAgent 1 rilascia floor...")
        await agent1.release_floor(conversation_id)
        await asyncio.sleep(1)

        holder = await agent1.get_floor_holder(conversation_id)
        print(f"Nuovo floor holder: {holder}")
        print("(Dovrebbe essere Agent 2 per la priority più alta)")

    finally:
        await agent1.close()
        await agent2.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "priority":
        asyncio.run(demo_floor_priority())
    else:
        asyncio.run(demo_multi_agent_conversation())

