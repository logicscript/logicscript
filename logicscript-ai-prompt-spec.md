# LogicScript — AI Prompt Specification

**Version 1.0**

This document is a complete, concise specification of LogicScript — a prompt language for describing software logic to AI systems. Reference this document when implementing a LogicScript specification to understand syntax, keywords, types, and mapping rules. Reference this document using it's url when entering your own logicscript specification.

---

## Purpose and model

LogicScript sits between plain English and production code. It expresses *what* a system should do without prescribing *how*. When you receive a LogicScript specification:

1. Read every `VALIDATE` block as a set of hard preconditions — fail fast before any side effects.
2. Map `ON FAIL THROW ErrorName` to the target language's idiomatic exception mechanism.
3. Translate `EMIT EventName WITH payload` to an event bus, message broker, or similar publish mechanism.
4. Honour `@transaction` by wrapping all steps in a database transaction with automatic rollback on failure.
5. Treat plain-English conditions and steps as implementation intent — infer the most idiomatic code for the target language.
6. Do not add behaviour not described in the specification.
7. Add inline comments referencing the LogicScript construct each code block implements.

---

## Syntax rules

- **Keywords** are always UPPERCASE: `MODULE`, `SHAPE`, `FUNC`, `FLOW`, `VALIDATE`, etc.
- **Structure** is expressed through indentation (2 spaces per level). No braces, brackets, or `end` keywords.
- **Identifiers**: modules and shapes use PascalCase; functions, variables, and fields use camelCase; events use PascalCase.
- **Comments**: `--` for inline; `--- ... ---` for block/doc comments (ignored by AI, informational only).
- **Plain English** is valid anywhere a condition or step is hard to express structurally. Implement it as the most natural equivalent in the target language.
- **Annotations** (`@name args`) appear on the line immediately before the declaration they modify.

---

## Declarations

### MODULE

Groups related functions and declares the public API surface.

```
MODULE ServiceName
  [IMPORT Symbol1, Symbol2 FROM sourceName]
  [USE Symbol.method AS alias]
  ENTRY functionName(params)  -- marks this FUNC as publicly callable
  ...
```

- `ENTRY` marks a function as public. Only `ENTRY` functions are part of the external interface.
- `IMPORT` and `USE` are dependency declarations — map to imports/requires in the target language.

---

### SHAPE

Defines a data structure with typed, constrained fields.

```
SHAPE ShapeName
  fieldName : Type  constraint [constraint ...]
  ...
```

**Field types**

| Type | Maps to |
| --- | --- |
| `String` | UTF-8 text |
| `Int` | 64-bit signed integer |
| `Float` | 64-bit float |
| `Bool` | Boolean |
| `UUID` | RFC 4122 UUID |
| `Timestamp` | ISO 8601 date-time with timezone |
| `List<T>` | Ordered collection of T |
| `Map<K,V>` | Key-value map |
| `Enum[a, b, c]` | Closed set of named string values |
| `JSON` | Arbitrary JSON-serializable value |

**Field constraints**

| Constraint | Meaning |
| --- | --- |
| `required` | Must be present and non-null |
| `optional` | May be null or absent |
| `unique` | Value must be unique across all records |
| `auto` | System-generated (UUID, timestamp, etc.) |
| `default=X` | Use X when not supplied |
| `min=N` | Minimum numeric value or string/array length |
| `max=N` | Maximum numeric value or string/array length |
| `pattern="regex"` | Must match regex |
| `immutable` | Cannot change after creation |
| `indexed` | Add a database index |

---

### FUNC

Defines a unit of logic. All four blocks are optional, but at least `DO` or `RETURN` must be present.

```
FUNC functionName(param1, param2, ...)
  [--- doc comment ---]
  [VALIDATE
    condition
    condition ...]
  [DO
    step
    step ...]
  [RETURN value]
  [ON FAIL strategy]
```

**VALIDATE block**

- Each line is one precondition.
- Evaluated top to bottom; first failure stops execution and triggers `ON FAIL`.
- Conditions use plain English or structured forms:

```
email not empty
email matches email pattern
password length >= 8
age between 18 and 120
price > 0
productId exists in Product
email not exists in User
startDate is before endDate
cart.items not empty  MESSAGE "Custom error message"
```

**DO block**

- Sequential steps, top to bottom.
- Assignments: `variable = expression`
- Service calls: `ServiceName.method(args)` or `CALL ServiceName.method(args)`
- Inline assertions: `REQUIRE condition ELSE THROW ErrorName`
- Emit events: `EMIT EventName WITH payload`
- Iteration: `FOR EACH item IN collection ... CALL ...`
- Conditional: `IF condition ... ELSE ...`
- Transactions: `TRANSACTION ... END` (or use `@transaction` annotation)

**RETURN**

Output value. Omit for void functions.

**ON FAIL strategies**

```
ON FAIL THROW ErrorName
ON FAIL LOG error
ON FAIL RETURN defaultValue
ON FAIL retry N times THEN THROW ErrorName
ON FAIL LOG error, THROW ErrorName       -- combine with comma
ON FAIL ROLLBACK                         -- within @transaction context
```

---

### FLOW

A named, multi-step operation. Use when a process has distinct named stages.

```
FLOW FlowName(params)
  STEP stepName
    logic ...
  STEP stepName
    logic ...
```

**Parallel execution**

```
FLOW FlowName(params)
  PARALLEL
    STEP stepA
      ...
    STEP stepB
      ...
    STEP stepC
      ...
  WAIT all        -- or: WAIT any

  STEP assemble
    RETURN { stepA_result, stepB_result, stepC_result }
```

`WAIT all` → `Promise.all` / `asyncio.gather` / `CompletableFuture.allOf` / `tokio::join!` / `std::async` + `.get()`
`WAIT any` → settle on first success

---

### GUARD

Reusable, named access-control block. Apply by name inside any `FUNC` or `FLOW`.

```
GUARD GuardName
  REQUIRE condition
    [OR condition]
    [AND condition]
  ON FAIL THROW ErrorName
```

Apply:

```
FUNC someFunction(params)
  GUARD GuardName
  DO
    ...
```

---

### POLICY

Cross-cutting rule applied to named targets or globally.

```
POLICY PolicyName
  APPLIES TO target [, target ...]   -- or: APPLIES TO all API endpoints
  ALLOW N requests PER unit PER period
  ON EXCEED action
```

```
POLICY RetentionPolicy
  APPLIES TO RecordType
  KEEP N years
  THEN archive to cold storage
  DELETE after N years
```

```
POLICY MaskingPolicy
  APPLIES TO logs, analytics
  MASK fields: fieldA, fieldB
  ALLOW unmasked access WHEN condition
```

---

### QUERY

Named, reusable data-retrieval operation.

```
QUERY queryName(params)
  FROM     ShapeName
  [WHERE   condition [AND condition ...]]
  [INCLUDE relatedShape, ...]
  [ORDER BY field ASC|DESC]
  [LIMIT   N]
  [OFFSET  N]
```

- `INCLUDE` → eager-load related records (JOIN or equivalent)
- `WITHIN N days` → shorthand for `field >= NOW - N days`

---

### ON / EMIT

Event-driven reactions. Producers and consumers are decoupled.

**Emit** (inside any FUNC or FLOW):

```
EMIT EventName WITH payload
EMIT EventName WITH { field1, field2, field3 }
```

**Subscribe**:

```
ON EventName
  TRIGGER functionName(args)
  SEND MessageType TO recipient
  LOG "message {variable}"
  ALERT team-name
  NOTIFY userId via channel WITH data
```

```
ON EventName N times     -- fires only after N occurrences
  ...
```

---

### STATE

Finite state machine for a named shape.

```
STATE ShapeName
  STATES  state1, state2, state3, ...

  TRANSITION fromState -> toState ON eventName
  TRANSITION fromState -> toState ON eventName
    WHEN condition                               -- optional guard
  TRANSITION ANY -> toState ON eventName
    WHEN status NOT IN [excludedState]

  ON ENTER stateName
    steps ...

  ON EXIT stateName
    steps ...
```

- `ANY` as source matches all states.
- `ON ENTER` / `ON EXIT` hooks run every time the named state is entered or exited.

---

### SCHEDULE

Recurring job definition.

```
SCHEDULE jobName
  EVERY N unit           -- unit: minutes | hours | days
  DO
    steps ...
```

```
SCHEDULE jobName
  AT "schedule expression"
  DO
    steps ...
```

Schedule expression examples: `"9:00 AM daily"`, `"Monday 8:00 AM"`, `"first day of month 08:00 UTC"`, `"1st of month 00:01 UTC"`.

---

### Annotations

Placed on the line immediately before the declaration they modify.

| Annotation | Meaning | Implementation hint |
| --- | --- | --- |
| `@transaction` | All steps succeed or all roll back | DB transaction + rollback on any error |
| `@retryable attempts=N backoff=X` | Retry on failure | `X`: `linear`, `exponential`, or duration |
| `@cached ttl=Ns key="template:{param}"` | Cache return value | In-memory, Redis, or equivalent |
| `@idempotent key="template:{param}"` | Deduplicate identical calls | Return stored result for same key |
| `@deprecated since="X" use=replacement` | Mark as deprecated | Add deprecation warning |
| `@observable metrics=[m1,m2]` | Instrument with metrics | Latency, error_rate, throughput, etc. |
| `@rateLimit N/period per=scopeField` | Per-caller rate limit | Middleware or decorator |

---

## Conditionals

```
IF condition
  ...
ELSE IF condition
  ...
ELSE
  ...
```

Short form for access rules:

```
ALLOW action WHEN condition
DENY  action WHEN condition
```

---

## Full keyword index

**Structure**

| Keyword | Role |
| --- | --- |
| `MODULE` | Named service/component boundary |
| `ENTRY` | Public function declaration within MODULE |
| `IMPORT … FROM` | Dependency import |
| `USE … AS` | Import alias |
| `SHAPE` | Data structure definition |
| `FUNC` | Function definition |
| `FLOW` | Multi-step process definition |
| `STEP` | Named stage within a FLOW |
| `PARALLEL` | Run following STEPs concurrently |
| `WAIT all \| any` | Synchronise after PARALLEL |

**Logic**

| Keyword | Role |
| --- | --- |
| `VALIDATE` | Precondition block; halts on first failure |
| `DO` | Ordered steps / side effects |
| `RETURN` | Output value |
| `ON FAIL` | Error-handling strategy |
| `REQUIRE … ELSE` | Inline assertion within DO |
| `IF / ELSE IF / ELSE` | Conditional branching |
| `FOR EACH` | Iteration over a collection |
| `CALL` | Explicit service/function invocation |
| `TRANSACTION` | Inline transaction block |
| `ROLLBACK` | Explicit rollback trigger |

**Access and rules**

| Keyword | Role |
| --- | --- |
| `ALLOW … WHEN` | Permission grant |
| `DENY … WHEN` | Permission denial |
| `GUARD` | Reusable access-control block |
| `POLICY` | Cross-cutting system rule |
| `APPLIES TO` | Scope a POLICY to named targets |

**Data and events**

| Keyword | Role |
| --- | --- |
| `QUERY` | Named data-retrieval operation |
| `FROM` | Source shape for QUERY |
| `WHERE` | Filter clause |
| `ORDER BY` | Sort clause |
| `LIMIT` | Result count cap |
| `OFFSET` | Pagination offset |
| `INCLUDE` | Eager-load related records |
| `WITHIN N days` | Date range shorthand |
| `EMIT … WITH` | Publish a named event |
| `ON [event]` | Subscribe to a named event |
| `TRIGGER` | Invoke function/flow from event handler |
| `SEND … TO` | Send message or email |
| `ALERT` | Send notification to a team/channel |
| `NOTIFY` | Send notification to a user |
| `LOG` | Write a log entry |

**State and scheduling**

| Keyword | Role |
| --- | --- |
| `STATE` | Finite state machine definition |
| `STATES` | Declare valid state values |
| `TRANSITION a -> b ON event` | Define a state change |
| `WHEN` | Guard condition on a TRANSITION |
| `ON ENTER` | Hook: runs when state is entered |
| `ON EXIT` | Hook: runs when state is exited |
| `SCHEDULE` | Recurring job definition |
| `EVERY N unit` | Interval-based schedule |
| `AT "expression"` | Calendar-based schedule |

---

## Implementation rules for AI

When implementing a LogicScript specification, apply these rules in order:

1. **VALIDATE → preconditions first.** Generate all validation checks before any `DO` steps. Each failing check must return or throw immediately without executing side effects.

2. **ON FAIL → target language error mechanism.** `THROW ErrorName` → exception/Result::Err/panic. `LOG error` → logger call. `ROLLBACK` → transaction abort. `retry N times` → retry loop with backoff.

3. **DO → sequential execution.** Each line in `DO` is a statement. Assignments bind to local variables. `REQUIRE x ELSE THROW E` → guard assertion after a fetch.

4. **EMIT → event publish.** Map to `EventEmitter.emit()`, `eventBus.publish()`, `pg_notify()`, Spring `ApplicationEventPublisher`, or equivalent for the target stack.

5. **@transaction → atomic block.** Wrap the entire `DO` block in a transaction. Any unhandled error must trigger rollback before re-throwing.

6. **PARALLEL + WAIT all → concurrent execution.** All named STEPs start simultaneously. Execution continues after the last one resolves.

7. **SHAPE → data type.** Generate struct, dataclass, record, interface, or CREATE TABLE as appropriate. Apply all constraints (NOT NULL, UNIQUE, CHECK, DEFAULT, index) in the target representation.

8. **STATE → state machine.** Generate a transition table or switch/match. Validate that the current state is in the allowed `from` set before applying `to`. Run `ON ENTER`/`ON EXIT` hooks after updating state.

9. **SCHEDULE → recurring job.** Map to cron, node-cron, APScheduler, @Scheduled, tokio::time, or equivalent. `EVERY N unit` → interval. `AT "expression"` → cron expression.

10. **GUARD → reusable middleware.** Generate a function or decorator that runs the `REQUIRE` check and can be composed onto any target function.

11. **POLICY → cross-cutting concern.** Rate limits → middleware. Data retention → background job or DB trigger. Masking → serialization layer.

12. **Plain English** → infer the most idiomatic, safe implementation. When ambiguous, prefer the more defensive interpretation.

---

## Minimal complete example

```logicscript
MODULE AuthService
  ENTRY login(email, password)
  ENTRY signup(email, password, name)

SHAPE User
  id           : UUID      required auto
  email        : String    required unique
  passwordHash : String    required
  role         : Enum[admin, user, guest]  default=user
  createdAt    : Timestamp auto

FUNC login(email, password)
  VALIDATE
    email not empty
    password not empty
  DO
    user = UserRepo.findByEmail(email)
    REQUIRE user exists ELSE THROW NotFoundError
    REQUIRE Crypto.verify(password, user.passwordHash) ELSE THROW AuthError
    REQUIRE user.status IS active ELSE THROW AccountSuspendedError
    session = SessionRepo.create(user.id, expiresIn=7 days)
  RETURN session
  ON FAIL LOG error, THROW AuthError

FUNC signup(email, password, name)
  VALIDATE
    email    matches email pattern
    password length >= 8
    name     length >= 2
    email    not exists in User
  DO
    hash = Crypto.hash(password)
    user = UserRepo.create(email, hash, name)
    EMIT UserCreated WITH user
  RETURN user

ON UserCreated
  TRIGGER EmailService.sendWelcome(user.email, user.name)
  LOG "New signup: {user.email}"

POLICY LoginProtection
  APPLIES TO login
  ALLOW 5 attempts PER ip PER 15 minutes
  ON EXCEED lockout for 30 minutes, ALERT security-team
```

---

*This specification document is designed for use as context in AI prompts. Include it before any LogicScript specification you want implemented.*
