from typing import Callable, Any
import uuid, httpx, os, json
from a2a.client import A2AClient
from a2a.types import (
    SendMessageResponse,
    SendMessageRequest,
    AgentCard,
    Task,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
)
from dotenv import load_dotenv

load_dotenv()

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]

class RemoteAgentConnections:
    """A class to hold the connections to the remote agents."""

    def __init__(self, agent_card: AgentCard, agent_url: str):
        self._url = "https://disaster-management-871861759609.us-east4.run.app"
        print(f"agent_card: {agent_card}")
        print(f"agent_url: {agent_url}")
        print(f"_URL : {self._url}")
        self._httpx_client = httpx.AsyncClient(timeout=30)
        self.agent_client = A2AClient(self._httpx_client, agent_card, url=self._url)
        self.card = agent_card
        self.conversation_name = None
        self.conversation = None
        self.pending_tasks = set()

    def get_agent(self) -> AgentCard:
        return self.card

    async def send_message(self, message_request: SendMessageRequest) -> SendMessageResponse:
        return  await self.agent_client.send_message(message_request)
        