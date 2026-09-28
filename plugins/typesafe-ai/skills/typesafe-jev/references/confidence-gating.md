# Calibrated Confidence Gating

## The Importance of Calibration

Traditional generative LLMs frequently exhibit overconfidence: an LLM may output a wrong classification while asserting 99% certainty in its natural language explanation.

**TypeSafe AI's Jev outputs statistically calibrated probabilities:**
- A confidence of `0.90` mathematically indicates that across a large sample of historical predictions at that score, exactly 90% are empirically correct.
- This calibration permits software engineers to build **deterministic confidence gating** directly into production code.

---

## Confidence Threshold Matrix

| Confidence Tier | Score Range | Action | Example Workflow |
| :--- | :--- | :--- | :--- |
| **Tier 1: High Certainty** | `score >= 0.85` | **Auto-execute:** Direct database update or automated routing. | Auto-archive spam email; route standard return ticket. |
| **Tier 2: Mild Ambiguity** | `0.65 <= score < 0.85` | **Secondary Check / System 2 Fallback:** Re-evaluate with an LLM or domain rule. | Complex invoice triage; borderline refund request. |
| **Tier 3: Low Certainty** | `score < 0.65` | **Human-in-the-Loop:** Place into manual review queue; alert operator. | Disputed chargeback; safety escalation. |

---

## Universal Gating Algorithm (Pseudocode)

```python
async def route_with_confidence_gating(
    input_text: str,
    target_schema: type[T],
    threshold: float = 0.85,
) -> RoutingResult[T]:
    # 1. Fast decision from Jev System 1
    decision = await jev_client.evaluate(input_text, schema=target_schema)

    # 2. Check calibrated probability
    if decision.confidence >= threshold:
        return RoutingResult(
            value=decision.value,
            confidence=decision.confidence,
            routed_by="jev_system1_auto",
        )

    # 3. Safe fallback path
    log.info(
        "Low confidence decision; falling back",
        score=decision.confidence,
        threshold=threshold,
    )
    fallback_value = await fallback_llm_or_human_queue(input_text, target_schema)
    return RoutingResult(
        value=fallback_value,
        confidence=decision.confidence,
        routed_by="system2_fallback",
    )
```

---

## Best Practices

1. **Never Hardcode a Global Threshold:** A fraud detection pipeline may require `0.98` confidence to auto-approve, whereas blog tag suggestions might operate happily at `0.70`.
2. **Track Disagreements:** When falling back to System 2 or human review, log both the Jev prediction and the final human verdict to continuously monitor drift.
3. **Graceful Degradation:** If the Jev endpoint is temporarily unreachable, fall back immediately to your rule engine or secondary model.
