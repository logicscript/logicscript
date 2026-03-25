# logicscript
LogicScript sits between plain English (too ambiguous) and actual code (too implementation-specific). You write what should happen; the AI figures out how in whatever language or framework you're using.
## The core constructs
ConstructPurpose

MODULES Service boundary with public entry points
SHAPE Data structure with typed, constrained fields
FUNC Function with validate / do / return / on-fail blocks
FLOW Multi-step operation, supports parallel steps
GUARD Reusable access control blocksPOLICYCross-cutting rules (rate limits, retention)
QUERY Named data retrieval with filters and ordering
ON / EMIT Event-driven async reactions
STATEState machines with valid transitions
SCHEDULE Recurring jobs
@annotations Metadata for cache, retry, deprecation, observability

## Design principles

* Indentation-based — no brackets or semicolons
* Plain-English conditions in VALIDATE blocks (email matches email pattern, age between 18 and 120)
* Intentionally incomplete — fill gaps with plain prose inline; the AI infers sensible defaults
* AI-target agnostic — the same LogicScript becomes Python, TypeScript, Go, or SQL depending on your context

The interactive reference includes a playground where you can write LogicScript and Claude will implement it, or describe something in plain English and get LogicScript back.
