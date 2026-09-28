# Python & Pydantic AI Integration Guide

## Overview

In Python backends (FastAPI, Litestar, Starlette), Jev integrates cleanly with **Pydantic v2** and **Pydantic AI** via `TypeSafeModel`.

Instead of running an auto-regressive agent prompt to extract a typed JSON object, Jev consumes standard Pydantic models and Enums, returning validated typed decisions.

---

## Example 1: Direct Decision with Pydantic v2

```python
from enum import StrEnum
from typing import Annotated
from pydantic import BaseModel, Field
from typesafe_ai import JevClient

class TicketCategory(StrEnum):
    BILLING = "billing"
    TECHNICAL_BUG = "technical_bug"
    FEATURE_REQUEST = "feature_request"
    ACCOUNT_SECURITY = "account_security"

class TicketDecision(BaseModel):
    category: TicketCategory
    is_urgent: bool = Field(description="True if customer is blocked or security is at risk")

# Initialize client
client = JevClient(api_key="ts_live_...")

async def triage_ticket(ticket_body: str) -> TicketDecision:
    # Jev evaluates in parallel, returning schema-validated result + confidence
    response = await client.decide(
        prompt=ticket_body,
        response_model=TicketDecision,
    )
    
    # Confidence is calibrated
    if response.confidence < 0.85:
        # Fallback to human triage or secondary agent
        pass
        
    return response.data
```

---

## Example 2: Pydantic AI Integration (`TypeSafeModel`)

When building multi-agent architectures with Pydantic AI:

```python
from pydantic_ai import Agent
from pydantic_ai.models.typesafe import TypeSafeModel
from pydantic import BaseModel

class Intent(BaseModel):
    action: str
    target_service: str

# Router agent powered by Jev (System 1)
router_agent = Agent(
    model=TypeSafeModel("jev-1"),
    result_type=Intent,
    system_prompt="Route incoming user commands to backend services.",
)

async def handle_user_command(user_input: str) -> None:
    result = await router_agent.run(user_input)
    # Fast typed execution without conversational overhead
    print(f"Routing to {result.data.target_service} with action {result.data.action}")
```

---

## Example 3: Clean Architecture / Ports & Adapters

In repositories following the Looptech architecture (`expert-backend-python`):

```python
# ports/triage_service.py
from abc import ABC, abstractmethod
from domain.triage import TriageDecision

class ITriageService(ABC):
    @abstractmethod
    async def triage(self, content: str) -> TriageDecision:
        ...

# infrastructure/typesafe/jev_triage_service.py
from ports.triage_service import ITriageService
from typesafe_ai import JevClient

class JevTriageService(ITriageService):
    def __init__(self, client: JevClient, confidence_threshold: float = 0.85) -> None:
        self._client = client
        self._threshold = confidence_threshold

    async def triage(self, content: str) -> TriageDecision:
        res = await self._client.decide(prompt=content, response_model=TriageDecision)
        return res.data
```
