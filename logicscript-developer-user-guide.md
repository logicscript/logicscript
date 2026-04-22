# LogicScript Language Reference

*Version 1.0 · April 2026*

> This document covers the LogicScript language specification: syntax, keywords, types, and grammar. For generated code examples in JavaScript, Python, SQL, Java, Rust, and C++, see **logicscript-examples.md**.

---

## Contents

**Getting started**
- [Overview](#logicscript)
- [Quickstart](#quickstart)
- [Core concepts](#core-concepts)

**Language reference**
- [MODULE](#module)
- [SHAPE](#shape)
- [FUNC](#func)
- [FLOW](#flow)
- [Conditionals](#conditionals)
- [VALIDATE](#validate)
- [GUARD](#guard)
- [POLICY](#policy)
- [QUERY](#query)
- [Events: ON / EMIT](#events-on--emit)
- [STATE](#state)
- [SCHEDULE](#schedule)
- [Annotations](#annotations)

**Data types**
- [Primitive types](#primitive-types)
- [Constraints](#constraints)

**Reference**
- [Keyword index](#keyword-index)
- [Formal grammar](#formal-grammar)

---

## Getting started

# LogicScript

*Guide* Version 1.0 · Updated April 2026

LogicScript is a prompt language for describing software logic to AI systems. It occupies the space between plain English (ambiguous, imprecise) and production code (over-specified, language-locked) — letting you communicate *what* a system should do without prescribing *how*.

Use LogicScript to specify business logic, data structures, authorization rules, state machines, and scheduled jobs. Give a LogicScript specification to an AI code generator, and it produces idiomatic output in any target language.

## When to use LogicScript

LogicScript is most useful when you want to:

- Rapidly prototype logic without committing to a specific language or framework.
- Create a single, language-agnostic specification that generates code in multiple target languages.
- Communicate system design to AI assistants with minimal ambiguity.
- Document intended behavior in a format that is both human-readable and machine-processable.

## Language building blocks

- **`MODULE`** — Named service boundary with public entry points and imports
- **`SHAPE`** — Typed data structures with field-level constraints
- **`FUNC`** — Functions with validate, do, return, and on-fail blocks
- **`FLOW`** — Ordered multi-step operations with optional parallelism
- **`GUARD`** — Reusable access-control blocks
- **`POLICY`** — Cross-cutting rules for rate limits, retention, and more
- **`ON / EMIT`** — Event subscriptions and emissions for async decoupling
- **`STATE`** — State machines with transitions and enter/exit hooks

## Design philosophy

LogicScript makes three intentional trade-offs:

- **Intentionally incomplete.** LogicScript describes intent. The AI infers sensible implementation defaults. You can supplement any block with plain-English prose.
- **Indentation over syntax.** Structure is expressed through indentation — no braces, semicolons, or end keywords.
- **Declarative over imperative.** Describe outcomes and constraints, not steps. Reserve the `DO` block for side effects that require explicit ordering.

> **Note:** LogicScript is a specification language, not an execution runtime. It has no interpreter. Its output is always AI-generated code in a target language such as JavaScript, Python, Go, or SQL.

---

---

# Quickstart

*Guide*

Write your first LogicScript specification and generate working code in under five minutes.

## Step 1: Define a data shape

Start by describing the data your system operates on using `SHAPE`.

```logicscript
SHAPE User
  id        : UUID       required auto
  email     : String     required unique
  name      : String     required
  role      : Enum[admin, user, guest]  default=user
  createdAt : Timestamp  auto
```

## Step 2: Write a function

Describe what the function does, its preconditions, and what it returns.

```logicscript
FUNC createUser(email, password, name)
  VALIDATE
    email    matches email pattern
    password length >= 8
    name     length >= 2
    email    not exists in User

  DO
    hash = bcrypt(password)
    user = User.create(email, hash, name)
    EMIT UserCreated WITH user

  RETURN user
  ON FAIL THROW ValidationError
```

## Step 3: Pass the specification to an AI

Include the LogicScript in your prompt with a target-language instruction:

## Step 4: Review generated output

The AI produces idiomatic code. See Generating output for examples and prompt templates.

> **Tip:** You can mix LogicScript with plain-English prose in the same specification. If a constraint is hard to express in LogicScript syntax, write it out in plain English directly inside the relevant block.

---

---

# Core concepts

*Guide*

Understanding a few structural rules makes LogicScript easy to read and write consistently.

## Indentation

LogicScript uses indentation (two spaces recommended) to express nesting. Blocks do not use braces or end keywords.

```logicscript
FUNC example(x)       -- top-level keyword
  VALIDATE             -- indented one level: starts a block
    x > 0             -- indented two levels: contents of block
  RETURN x             -- back to one level: next clause
```

## Keywords

All LogicScript keywords are uppercase. Identifiers (function names, field names, variable names) are camelCase. Type names are PascalCase.

## Comments

Use `--` for inline comments and `--- ... ---` for block doc-comments.

```logicscript
-- Single-line comment

---
  Block comment. Use for function-level documentation.
  Describe purpose, parameters, and return values here.
---

FUNC getUser(userId)
  --- Returns the user with the given ID.
      Throws NotFoundError if the user does not exist. ---
  ...
```

## Plain English in specifications

LogicScript is intentionally incomplete. Any condition or behavior that is difficult to express in structured syntax can be written as plain English inside any block.

```logicscript
VALIDATE
  email matches email pattern
  -- Plain English is valid when the constraint is complex:
  password must contain at least one uppercase letter,
    one digit, and one special character
```

## Identifiers and naming

- Module names: PascalCase (for example, `AuthService`)
- Shape names: PascalCase (for example, `UserProfile`)
- Function and variable names: camelCase (for example, `createUser`, `userId`)
- Event names: PascalCase (for example, `UserCreated`)
- Field names: camelCase (for example, `createdAt`)

---

---

## Output examples

---

## Language reference

# MODULE

*Reference*

A `MODULE` declares a named, bounded unit of logic — analogous to a class, service, or package. It defines public entry points and imports external dependencies.

## Syntax

```
MODULE ModuleName
  [IMPORT Dep1, Dep2 FROM source]
  [USE Dep1.method AS alias]
  ENTRY functionName(params) -- ReturnType
  ...
```

### Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| ModuleName | Yes | PascalCase identifier for the module. |
| IMPORT | No | Comma-separated list of symbols to import from a named source. |
| USE ... AS | No | Alias a deeply nested import for convenience. |
| ENTRY | Yes (≥1) | Declares a function as part of the public API. At least one `ENTRY` is required. |

## Example

```logicscript
MODULE PaymentService
  IMPORT StripeClient, UserRepo FROM core
  IMPORT Logger               FROM utils
  USE Logger.info AS log

  ENTRY charge(userId, amount, currency) -- Transaction
  ENTRY refund(transactionId)            -- void
  ENTRY getHistory(userId)               -- List<Transaction>
```

> **Note:** `ENTRY` declarations describe the module's public surface. Private helper functions are defined with `FUNC` at the module level and are not listed as `ENTRY` points.

---

---

# SHAPE

*Reference*

A `SHAPE` defines a data structure. Each field has a name, a type, and one or more constraints. Types and constraints are implementation hints — the AI maps them to the most appropriate constructs in the target language.

## Syntax

```
SHAPE ShapeName
  fieldName : Type  [constraint ...]
  ...
```

## Field constraints

| Constraint | Description |
| --- | --- |
| required | The field must always be present and non-null. |
| optional | The field may be null or absent. |
| unique | The value must be unique across all records of this shape. |
| default=*value* | The default value when the field is not supplied. |
| auto | The value is generated automatically (for example, a UUID or timestamp). |
| min=*N* | Minimum numeric value or minimum string/array length. |
| max=*N* | Maximum numeric value or maximum string/array length. |
| pattern=*"regex"* | A regular expression the value must match. |

## Example

```logicscript
SHAPE BlogPost
  id          : UUID          required auto
  title       : String        required min=3 max=200
  body        : String        required
  slug        : String        required unique
  status      : Enum[draft, published, archived]  default=draft
  authorId    : UUID          required
  tags        : List<String>  optional
  publishedAt : Timestamp     optional
  createdAt   : Timestamp     auto
  updatedAt   : Timestamp     auto
```

See Primitive types for the full list of built-in types.

---

---

# FUNC

*Reference*

A `FUNC` defines a unit of logic with up to four blocks: `VALIDATE`, `DO`, `RETURN`, and `ON FAIL`. All blocks are optional, but every function should have at least a `DO` or `RETURN` block.

## Syntax

```
FUNC functionName(param1, param2, ...)
  [--- doc comment ---]
  [VALIDATE
    condition ...]
  [DO
    step ...]
  [RETURN value]
  [ON FAIL strategy]
```

### Blocks

**`VALIDATE`**  
Precondition checks. Each line is a condition. If any condition fails, execution halts and the `ON FAIL` handler runs. See Validation.

**`DO`**  
Ordered side-effect steps. Assignments, service calls, and `EMIT` statements go here. Steps execute sequentially unless wrapped in `PARALLEL`.

**`RETURN`**  
The function's output value. Omit for void functions.

**`ON FAIL`**  
Error handling strategy. Can be `THROW ErrorType`, `LOG error`, `RETURN defaultValue`, or a combination.

## Example

```logicscript
FUNC getUserProfile(userId)
  --- Returns a user's public profile.
      Throws NotFoundError if the user does not exist. ---

  VALIDATE
    userId not empty

  DO
    user = UserRepo.findById(userId)
    REQUIRE user exists ELSE THROW NotFoundError
    profile = ProfileRepo.findByUserId(userId)

  RETURN { user, profile }
  ON FAIL LOG error, THROW ServiceError
```

### Inline REQUIRE

Use `REQUIRE … ELSE …` inside a `DO` block for post-fetch assertions:

```logicscript
DO
  order = OrderRepo.find(orderId)
  REQUIRE order exists           ELSE THROW NotFoundError
  REQUIRE order.status IS pending ELSE THROW InvalidStateError
```

---

---

# FLOW

*Reference*

A `FLOW` is a named, multi-step operation. Use it when a process has distinct, named stages — for example, an order checkout or a data ingestion pipeline. Steps run sequentially by default; wrap steps in `PARALLEL` to run them concurrently.

## Syntax

```
FLOW FlowName(params)
  STEP stepName
    logic ...
  [PARALLEL
    STEP stepName ...
  WAIT all | any]
```

## Sequential flow example

```logicscript
FLOW OrderCheckout(cartId, userId)
  STEP validateCart
    REQUIRE cart.items not empty
    REQUIRE cart.total > 0

  STEP processPayment
    CALL PaymentService.charge(cart.total, user.paymentMethod)
    ON FAIL retry 3 times THEN THROW PaymentError

  STEP createOrder
    order = Order.create(FROM cart)
    EMIT OrderCreated WITH order

  STEP notify
    SEND ConfirmationEmail TO user.email
    CALL CartService.clear(cartId)
```

## Parallel flow example

```logicscript
FLOW GenerateDashboard(userId)
  PARALLEL
    STEP fetchStats
      stats = Analytics.getUserStats(userId)
    STEP fetchActivity
      activity = ActivityLog.recent(userId, limit=20)
    STEP fetchNotifications
      notifications = Inbox.unread(userId)
  WAIT all

  STEP assemble
    RETURN { stats, activity, notifications }
```

---

---

# Conditionals

*Reference*

LogicScript supports standard conditional branching with `IF`, `ELSE IF`, and `ELSE`. Short-form `ALLOW`/`DENY WHEN` is available for access control conditions.

## IF / ELSE IF / ELSE

```logicscript
IF user.role IS admin
  ALLOW full access
ELSE IF user.role IS user
  ALLOW read, write OWN records
  DENY delete
ELSE
  DENY all
  THROW UnauthorizedError
```

## Short form: ALLOW / DENY WHEN

```logicscript
ALLOW publish WHEN user.role IS admin OR user.role IS editor
DENY  delete  WHEN resource.locked IS true
DENY  access  WHEN user.bannedUntil > NOW
```

---

---

# VALIDATE

*Reference*

The `VALIDATE` block contains precondition checks for a `FUNC`. Conditions are evaluated in order. The first failing condition triggers the `ON FAIL` handler.

## Common condition patterns

```logicscript
VALIDATE
  -- Presence
  email not empty
  user exists

  -- Format
  email matches email pattern
  phone matches "/^\+?[0-9]{10,15}$/"

  -- Range and length
  password length >= 8
  age between 18 and 120
  price > 0

  -- Uniqueness and existence
  email not exists in User
  productId exists in Product

  -- Custom message
  cart.items not empty MESSAGE "Cart cannot be empty"
```

> **Caution:** Conditions in `VALIDATE` are not guaranteed to run in a transaction. Uniqueness conditions (for example, `email not exists in User`) may be subject to race conditions in production. The generated code should use database-level unique constraints in addition to application-level checks.

---

---

# GUARD

*Reference*

A `GUARD` is a named, reusable access-control block. Apply a guard to any `FUNC` or `FLOW` by referencing it by name inside the function body.

## Defining a guard

```logicscript
GUARD AdminOnly
  REQUIRE user.role IS admin
  ON FAIL THROW ForbiddenError

GUARD OwnerOrAdmin
  REQUIRE user.id IS resource.ownerId
    OR user.role IS admin
  ON FAIL THROW ForbiddenError
```

## Applying a guard

```logicscript
FUNC deleteUser(userId)
  GUARD AdminOnly
  DO
    User.delete(userId)
    LOG "Deleted user {userId}"

FUNC updatePost(postId, data)
  GUARD OwnerOrAdmin
  DO
    Post.update(postId, data)
```

---

---

# POLICY

*Reference*

A `POLICY` defines a cross-cutting rule that applies to a named set of functions, flows, or globally. Use policies for rate limiting, data retention, compliance requirements, and observability constraints.

## Examples

```logicscript
POLICY RateLimit
  APPLIES TO all API endpoints
  ALLOW 100 requests PER user PER minute
  ON EXCEED return 429, message="Rate limit exceeded"

POLICY AuthRateLimit
  APPLIES TO login, signup, resetPassword
  ALLOW 5 requests PER ip PER 15 minutes
  ON EXCEED lockout for 30 minutes, ALERT security-team

POLICY DataRetention
  APPLIES TO AuditLog
  KEEP 1 year
  THEN archive to cold storage
  DELETE after 7 years
```

---

---

# QUERY

*Reference*

A `QUERY` defines a named, reusable data-retrieval operation. Use `WHERE` for filtering, `ORDER BY` for sorting, `LIMIT` for pagination, and `INCLUDE` for eager loading related data.

## Syntax

```
QUERY queryName(params)
  FROM     ShapeName
  [WHERE   condition [AND condition ...]]
  [INCLUDE relatedShape, ...]
  [ORDER BY field ASC|DESC]
  [LIMIT   N]
  [OFFSET  N]
```

## Examples

```logicscript
QUERY activeUsers
  FROM     User
  WHERE    status IS active
  AND      lastLogin WITHIN 30 days
  ORDER BY createdAt DESC
  LIMIT    100

QUERY userOrderHistory(userId)
  FROM     Order
  WHERE    userId IS userId
  AND      status IS NOT cancelled
  INCLUDE  items, shippingAddress
  ORDER BY createdAt DESC

QUERY lowInventory(threshold)
  FROM     Product
  WHERE    stockCount < threshold
  AND      active IS true
  ORDER BY stockCount ASC
```

---

---

# Events: ON / EMIT

*Reference*

`EMIT` publishes a named event. `ON` subscribes to a named event and specifies reactions. Events decouple producers from consumers — the emitting function does not need to know what is listening.

## EMIT

```logicscript
EMIT UserCreated WITH user
EMIT OrderPlaced WITH { orderId, userId, total }
EMIT LowInventory WITH { productId, remaining: 2 }
```

## ON

```logicscript
ON UserCreated
  TRIGGER EmailService.sendWelcome(user.email, user.name)
  TRIGGER AnalyticsService.track("signup", user.id)
  LOG "New signup: {user.email}"

ON PaymentFailed 3 times
  TRIGGER suspendAccount(user.id)
  ALERT billing-team
```

---

---

# STATE

*Reference*

A `STATE` block defines a finite state machine for a named shape. It specifies valid states, allowed transitions, triggering events, and optional enter/exit hooks.

## Example

```logicscript
STATE Order
  STATES  draft, pending, paid, shipped, delivered, cancelled

  TRANSITION draft   -> pending   ON submitOrder
  TRANSITION pending -> paid      ON paymentReceived
  TRANSITION paid    -> shipped   ON fulfillOrder
  TRANSITION shipped -> delivered ON deliveryConfirmed
  TRANSITION ANY     -> cancelled ON cancelOrder
    WHEN status NOT IN [delivered]

  ON ENTER shipped
    EMIT OrderShipped WITH order
    NOTIFY user via email WITH trackingInfo

  ON ENTER cancelled
    TRIGGER refundIfPaid(order)
    LOG "Order {order.id} cancelled"
```

---

---

# SCHEDULE

*Reference*

A `SCHEDULE` defines a recurring job. Use `EVERY` for interval-based scheduling or `AT` for calendar-based scheduling. The body follows standard `DO` block syntax.

## Examples

```logicscript
SCHEDULE cleanExpiredSessions
  EVERY 1 hour
  DO
    deleted = Session.deleteExpired()
    LOG "Purged {deleted} expired sessions"

SCHEDULE monthlyInvoices
  AT "first day of month 08:00 UTC"
  DO
    subscribers = Subscription.active()
    FOR EACH subscriber
      CALL BillingService.generateInvoice(subscriber)
    LOG "Invoiced {count} subscribers"

SCHEDULE healthCheck
  EVERY 5 minutes
  DO
    result = DB.ping()
    IF result IS failure
      ALERT ops-team
      EMIT DatabaseDown
```

---

---

# Annotations

*Reference*

Annotations add metadata to `FUNC`, `FLOW`, and `SHAPE` declarations. They signal implementation concerns — caching, retries, observability — without embedding those concerns in the logic itself.

## Built-in annotations

| Annotation | Arguments | Description |
| --- | --- | --- |
| @cached | ttl, key | Cache the function's return value. `ttl` is the time-to-live; `key` is the cache key template. |
| @retryable | attempts, backoff | Retry on failure. `backoff` can be `linear`, `exponential`, or a fixed duration. |
| @transaction | — | Wrap the function body in a database transaction. Roll back on any failure. |
| @idempotent | key | Deduplicate calls using the given key. A second call with the same key returns the first result. |
| @deprecated | since, use | Mark a function as deprecated. `use` names the replacement. |
| @observable | metrics | Instrument the function with the listed metrics (for example, `latency`, `error_rate`). |
| @rateLimit | N/period, per | Apply a per-caller rate limit. |

## Example

```logicscript
@cached ttl=300s key="user:{userId}"
FUNC getUserProfile(userId) ...

@retryable attempts=3 backoff=exponential
FUNC callPaymentGateway(payload) ...

@deprecated since="2.0" use=createUserV2
FUNC createUser(email, password) ...

@observable metrics=[latency, error_rate, throughput]
FLOW OrderCheckout ...

@idempotent key="payment:{orderId}"
FUNC processPayment(orderId, amount) ...
```

---

---

## Data types

---

## Data types

# Primitive types

*Reference*

LogicScript's built-in types are implementation hints. The AI maps each type to the most appropriate construct in the target language.

| Type | Description | JavaScript | Python | SQL | Java | Rust | C++ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| String | UTF-8 text of any length | `string` | `str` | `TEXT` | `String` | `String` | `std::string` |
| Int | Signed 64-bit integer | `number` (integer) | `int` | `BIGINT` | `long` | `i64` | `int64_t` |
| Float | 64-bit floating-point | `number` | `float` | `DOUBLE PRECISION` | `double` | `f64` | `double` |
| Bool | Boolean true or false | `boolean` | `bool` | `BOOLEAN` | `boolean` | `bool` | `bool` |
| UUID | RFC 4122 UUID | `string` (UUID format) | `str` (UUID format) | `UUID` | `UUID` | `Uuid` | `std::string` |
| Timestamp | ISO 8601 date-time with timezone | `Date` | `datetime` | `TIMESTAMPTZ` | `Instant` | `DateTime` | `time_point` |
| `List<T>` | Ordered collection of T | `T[]` | `list[T]` | `T[]` / `JSONB` | `List<T>` | `Vec<T>` | `std::vector` |
| `Map<K, V>` | Key-value map | `Record<K,V>` | `dict[K, V]` | `JSONB` | `Map` | `HashMap<K,V>` | `std::unordered_map` |
| Enum[a, b, ...] | Closed set of named values | `type T = 'a' \| 'b' \| ...` | `Enum` subclass | `CREATE TYPE … AS ENUM` | `enum` | `enum` | `enum class` |
| JSON | Arbitrary JSON-serializable value | `unknown` | `Any` | `JSONB` | `Object` | `serde_json::Value` | `nlohmann::json` |

---

---

# Constraints

*Reference*

Constraints appear after the type declaration in a `SHAPE` field. Multiple constraints can appear on the same line, separated by spaces.

| Constraint | Applies to | Description |
| --- | --- | --- |
| required | All types | Field must be present and non-null. |
| optional | All types | Field may be null or absent. |
| unique | All types | Value must be unique across all records. |
| auto | UUID, Timestamp | Value is generated automatically. |
| default=*value* | All types | Default value when the field is not supplied. |
| min=*N* | Int, Float, String, List | Minimum value or minimum length. |
| max=*N* | Int, Float, String, List | Maximum value or maximum length. |
| pattern=*"regex"* | String | Value must match the regular expression. |
| immutable | All types | Value cannot be changed after creation. |
| indexed | All types | Field should be indexed in the data store. |

---

---

## Reference

---

## Reference

# Keyword index

*Reference*

All keywords, grouped by category. Keywords are always uppercase.

## Structure

| Keyword | Description |
| --- | --- |
| MODULE | Declare a named service or component. |
| ENTRY | Mark a function as part of a module's public API. |
| IMPORT … FROM | Import named symbols from a source. |
| USE … AS | Alias an import. |
| SHAPE | Define a data structure. |
| FUNC | Define a function. |
| FLOW | Define a multi-step operation. |
| STEP | A named stage within a FLOW. |
| PARALLEL … WAIT | Run steps concurrently; wait for all or any to complete. |

## Logic

| Keyword | Description |
| --- | --- |
| VALIDATE | Precondition block — halts execution on failure. |
| DO | Ordered side-effect steps. |
| RETURN | Output value of a function. |
| ON FAIL | Error-handling strategy. |
| REQUIRE … ELSE | Inline assertion within a DO block. |
| IF / ELSE IF / ELSE | Conditional branching. |
| FOR EACH | Iterate over a collection. |
| CALL | Explicitly invoke a function or service method. |
| TRANSACTION | Wrap steps in a database transaction. |
| ROLLBACK | Roll back a transaction on failure. |

## Permissions

| Keyword | Description |
| --- | --- |
| ALLOW … WHEN | Permit an action, optionally conditioned. |
| DENY … WHEN | Forbid an action, optionally conditioned. |
| GUARD | Define or apply a reusable access-control block. |
| POLICY | Define a cross-cutting rule. |
| APPLIES TO | Scope a POLICY to named targets. |

## Data and events

| Keyword | Description |
| --- | --- |
| QUERY | Named data-retrieval operation. |
| FROM / WHERE / ORDER BY / LIMIT / INCLUDE | Query clauses. |
| EMIT … WITH | Publish a named event with an optional payload. |
| ON [event] | Subscribe to a named event. |
| TRIGGER | Invoke a function or flow in response to an event. |
| ALERT | Send a notification to a team or channel. |
| NOTIFY | Send a notification to a user. |
| SEND … TO | Send a message or email. |

## State and scheduling

| Keyword | Description |
| --- | --- |
| STATE | Define a finite state machine. |
| STATES | Declare the valid state values. |
| TRANSITION … ON … WHEN | Define a state transition. |
| ON ENTER | Hook that runs when a state is entered. |
| ON EXIT | Hook that runs when a state is exited. |
| SCHEDULE | Define a recurring job. |
| EVERY | Interval-based schedule. |
| AT | Calendar-based schedule. |

---

---

# Formal grammar

*Reference*

The following is an approximate BNF-style grammar for LogicScript. It describes the structural rules without exhaustively enumerating all condition forms, which are intentionally open-ended.

```bnf
program     ::= (declaration | comment)*

declaration ::= module | shape | func | flow | guard | policy
              | query | on_handler | state | schedule

-- Identifiers
IDENT       ::= [a-zA-Z][a-zA-Z0-9_]*
PASCAL      ::= [A-Z][a-zA-Z0-9]*   -- PascalCase
CAMEL       ::= [a-z][a-zA-Z0-9]*   -- camelCase
EVENT       ::= PASCAL               -- events use PascalCase

-- Module
module      ::= "MODULE" PASCAL NL
                (INDENT import_stmt)* 
                (INDENT use_stmt)*
                (INDENT "ENTRY" CAMEL "(" params? ")")*

import_stmt ::= "IMPORT" PASCAL ("," PASCAL)* "FROM" CAMEL
use_stmt    ::= "USE" IDENT "AS" CAMEL

-- Shape
shape       ::= "SHAPE" PASCAL NL
                (INDENT field_decl)*

field_decl  ::= CAMEL ":" type constraint*
type        ::= "String" | "Int" | "Float" | "Bool"
              | "UUID" | "Timestamp" | "JSON"
              | "List" | "Map"
              | "Enum[" CAMEL ("," CAMEL)* "]"

constraint  ::= "required" | "optional" | "unique" | "auto"
              | "immutable" | "indexed"
              | "default=" value
              | "min=" NUMBER | "max=" NUMBER
              | "pattern=" STRING

-- Function
func        ::= annotation* "FUNC" CAMEL "(" params? ")" NL
                doc_comment?
                validate_block?
                do_block?
                return_stmt?
                on_fail?

validate_block ::= INDENT "VALIDATE" NL (INDENT INDENT condition)*
do_block       ::= INDENT "DO" NL (INDENT INDENT step)*
return_stmt    ::= INDENT "RETURN" expr
on_fail        ::= INDENT "ON FAIL" fail_action

fail_action ::= "THROW" PASCAL
              | "LOG" expr
              | "RETURN" expr
              | fail_action "," fail_action

-- Flow
flow        ::= annotation* "FLOW" PASCAL "(" params? ")" NL step_group+

step_group  ::= INDENT "STEP" CAMEL NL (INDENT INDENT step)*
              | INDENT "PARALLEL" NL (INDENT INDENT "STEP" CAMEL NL (INDENT INDENT INDENT step)*)+ INDENT "WAIT" ("all" | "any")

-- Annotations
annotation  ::= "@" CAMEL (CAMEL "=" value)*

-- Common
params      ::= CAMEL ("," CAMEL)*
comment     ::= "--" .* NL
doc_comment ::= "---" .* "---"
condition   ::= <plain-English or structured condition>
step        ::= <assignment | call | emit | require | if | log | send>
NL          ::= newline
INDENT      ::= "  " (two spaces)
```

> **Note:** The `condition` and `step` productions are intentionally open-ended. LogicScript does not define a parser; its grammar is a guide for human writers and AI consumers, not a machine-parseable specification.

---

---
