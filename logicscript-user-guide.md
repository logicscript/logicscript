# LogicScript: User Guide

*Version 1.0 · April 2026*

> LogicScript is a structured way of describing *what* you want software to do — an AI handles the coding. You do not need to know how to code. Just use the LogicScript keywords to describe core logic and standard natual languge prompts for everything else.
>
> Technical specification and formal grammar: logicscript-reference.md
>
> Examples: logicscript-examples.md

---

## Contents

- [LogicScript: User Guide](#logicscript-user-guide)
  - [Contents](#contents)
  - [What is LogicScript?](#what-is-logicscript)
    - [The key idea](#the-key-idea)
  - [How it works](#how-it-works)
  - [Writing your first prompt](#writing-your-first-prompt)
  - [Building blocks at a glance](#building-blocks-at-a-glance)
  - [Describing data: SHAPE](#describing-data-shape)
    - [Field types](#field-types)
    - [Field rules (constraints)](#field-rules-constraints)
    - [Example](#example)
  - [Describing actions: FUNC](#describing-actions-func)
    - [VALIDATE — pre-flight checks](#validate--pre-flight-checks)
    - [DO — the steps](#do--the-steps)
    - [ON FAIL — error handling](#on-fail--error-handling)
    - [A complete FUNC example](#a-complete-func-example)
  - [Describing processes: FLOW](#describing-processes-flow)
    - [Sequential flow](#sequential-flow)
    - [Parallel flow](#parallel-flow)
  - [Making decisions: IF / ELSE](#making-decisions-if--else)
  - [Checking inputs: VALIDATE](#checking-inputs-validate)
    - [Common patterns](#common-patterns)
    - [Plain English is always fine](#plain-english-is-always-fine)
  - [Access control: GUARD and ALLOW / DENY](#access-control-guard-and-allow--deny)
    - [GUARD — reusable access rules](#guard--reusable-access-rules)
    - [ALLOW / DENY — inline permission rules](#allow--deny--inline-permission-rules)
  - [System-wide rules: POLICY](#system-wide-rules-policy)
  - [Finding records: QUERY](#finding-records-query)
    - [QUERY clauses](#query-clauses)
  - [Reacting to events: ON and EMIT](#reacting-to-events-on-and-emit)
    - [EMIT — fire an event](#emit--fire-an-event)
    - [ON — react to an event](#on--react-to-an-event)
  - [Tracking status: STATE](#tracking-status-state)
    - [Structure](#structure)
    - [ON ENTER — hooks](#on-enter--hooks)
    - [Reading a state machine](#reading-a-state-machine)
  - [Scheduled tasks: SCHEDULE](#scheduled-tasks-schedule)
    - [Timing options](#timing-options)
  - [Performance hints: Annotations](#performance-hints-annotations)
    - [Examples](#examples)
  - [Tips for better prompts](#tips-for-better-prompts)
    - [Do mix plain English and LogicScript](#do-mix-plain-english-and-logicscript)
    - [Keep each FUNC focused](#keep-each-func-focused)
    - [Name things clearly](#name-things-clearly)
    - [Add doc comments](#add-doc-comments)
    - [Be explicit about failures](#be-explicit-about-failures)
    - [Annotate for safety when money is involved](#annotate-for-safety-when-money-is-involved)
  - [Quick reference card](#quick-reference-card)
    - [Structure keywords](#structure-keywords)
    - [Logic keywords](#logic-keywords)
    - [Access control](#access-control)
    - [Data and events](#data-and-events)
    - [Status and scheduling](#status-and-scheduling)
    - [Common annotations](#common-annotations)

---

## What is LogicScript?

LogicScript is a way of writing down the *rules* of a piece of software in plain, structured English — precise enough that an AI can turn it into working code, but readable enough that a non-programmer can write and understand it.

Think of it like writing a job description or a Standard Operating Procedure. You describe:

- **What information exists** (data shapes)
- **What actions are allowed** (functions)
- **What the rules are** (validation, access control, policies)
- **What happens automatically** (events, schedules)

You do *not* describe how the computer carries out those actions — that is the AI's job.

### The key idea

> Write *what*, not *how*.

Bad (too vague): *"Make a login screen."*

Bad (too specific): *"Query the users table, compare the bcrypt hash, issue a JWT…"*

Good LogicScript:

```logicscript
FUNC login(email, password)
  VALIDATE
    email not empty
    password not empty
  DO
    user = find user by email
    check password matches stored hash
    create a new session for user
  RETURN session
  ON FAIL THROW AuthError
```

---

## How it works

1. **You write a prompt** in LogicScript describing the system's rules and behaviors.
2. **You give the prompt to an AI** (Claude, GPT-4, etc.) with an instruction like:*"Implement this LogicScript prompt in Python."*
3. **The AI produces working code** that follows your prompt exactly.
4. A developer reviews and deploys the code.

You stay in control of the *rules*. The AI handles the *implementation*.

---

## Writing your first prompt

A LogicScript prompt looks like this. Notice:

- **Keywords are ALL CAPS** —`SHAPE`,`FUNC`,`VALIDATE`, etc.
- **Indentation matters** — two spaces per level, like a bullet list
- **Plain English is fine** inside any block
- **Comments start with `--`**

```logicscript
-- This is a comment. The AI ignores it.

SHAPE Product
  id    : UUID    required auto
  name  : String  required
  price : Float   required min=0
  stock : Int     required default=0

FUNC buyProduct(productId, quantity, userId)
  --- Lets a user purchase a product. ---

  VALIDATE
    quantity > 0
    product exists with id = productId
    product.stock >= quantity
    user has valid payment method

  DO
    charge user for quantity * product.price
    reduce product.stock by quantity
    create an Order record
    EMIT OrderPlaced WITH order

  RETURN order
  ON FAIL THROW PurchaseError
```

That is a complete, usable prompt. An AI can turn that into production code in any language.

---

## Building blocks at a glance

| Keyword         | What it describes                             | Plain-English analogy           |
| --------------- | --------------------------------------------- | ------------------------------- |
| `SHAPE`       | A type of record or object                    | A form template                 |
| `FUNC`        | An action the system can perform              | A procedure in an SOP           |
| `FLOW`        | A multi-step process                          | A flowchart                     |
| `VALIDATE`    | Rules that must be true before an action runs | Pre-flight checklist            |
| `DO`          | The steps that happen during an action        | The body of the procedure       |
| `GUARD`       | A reusable access rule                        | "Only managers may…"           |
| `POLICY`      | A system-wide rule                            | A company policy                |
| `QUERY`       | A saved search or report                      | A database report               |
| `ON`          | A reaction to an event                        | "When X happens, do Y"          |
| `EMIT`        | Fire a named event                            | Send an internal notification   |
| `STATE`       | Valid statuses and transitions                | A status workflow               |
| `SCHEDULE`    | A recurring automatic task                    | A cron job or calendar reminder |
| `@annotation` | A performance or behaviour hint               | A sticky note for the AI        |

---

## Describing data: SHAPE

A `SHAPE` describes a type of record — what fields it has, what type of information each field holds, and any rules about that field.

### Field types

| Type              | What it stores                | Example value                       |
| ----------------- | ----------------------------- | ----------------------------------- |
| `String`        | Text                          | `"hello"`, `"user@example.com"` |
| `Int`           | Whole number                  | `42`, `-7`                      |
| `Float`         | Decimal number                | `9.99`, `3.14`                  |
| `Bool`          | True or false                 | `true`, `false`                 |
| `UUID`          | Unique ID                     | auto-generated                      |
| `Timestamp`     | Date and time                 | auto-generated                      |
| `Enum[a, b, c]` | One of a fixed list of values | `draft`, `published`            |
| `List<Type>`    | A collection of values        | list of strings                     |

### Field rules (constraints)

Add these after the type to restrict what values are allowed:

| Rule          | Meaning                                                          |
| ------------- | ---------------------------------------------------------------- |
| `required`  | Must always have a value                                         |
| `optional`  | May be left blank                                                |
| `unique`    | No two records may share this value                              |
| `auto`      | The system fills this in automatically                           |
| `default=X` | If not provided, use X                                           |
| `min=N`     | Must be at least N (for numbers) or N characters long (for text) |
| `max=N`     | Must be at most N                                                |
| `immutable` | Cannot be changed after creation                                 |
| `indexed`   | Optimise lookups on this field                                   |

### Example

```logicscript
SHAPE Invoice
  id          : UUID       required auto
  number      : String     required unique
  customerName: String     required
  amount      : Float      required min=0
  status      : Enum[draft, sent, paid, overdue]  default=draft
  dueDate     : Timestamp  required
  createdAt   : Timestamp  auto
  notes       : String     optional
```

Think of `SHAPE Invoice` as defining the blank invoice form. Every invoice that exists in the system will follow this template.

---

## Describing actions: FUNC

A `FUNC` describes something the system can *do*. It has up to four sections:

| Section      | What it does                                  |
| ------------ | --------------------------------------------- |
| `VALIDATE` | Checks that must pass before anything happens |
| `DO`       | The steps that run when all checks pass       |
| `RETURN`   | What the function hands back to the caller    |
| `ON FAIL`  | What happens if something goes wrong          |

### VALIDATE — pre-flight checks

Each line inside `VALIDATE` is one check. If any check fails, the function stops immediately and the `ON FAIL` handler runs. Nothing in `DO` is executed.

Write conditions in plain English:

```logicscript
VALIDATE
  email not empty
  email matches email pattern
  password length >= 8
  user does not already exist with this email
  price > 0
  quantity between 1 and 100
  product.stock >= quantity
  start date is before end date
```

You can also add a custom error message:

```logicscript
VALIDATE
  cart.items not empty  MESSAGE "Your cart is empty"
  total > 0             MESSAGE "Order total must be positive"
```

### DO — the steps

`DO` contains the actual work — in order, top to bottom. Write steps as plain instructions:

```logicscript
DO
  hash the password
  create a new User record with the provided details
  send a welcome email to user.email
  EMIT UserCreated WITH user
```

You can also do inline checks here with `REQUIRE`:

```logicscript
DO
  order = find order by id
  REQUIRE order exists ELSE THROW NotFoundError
  REQUIRE order.status IS pending ELSE THROW InvalidStateError
  process the payment
```

### ON FAIL — error handling

```logicscript
ON FAIL THROW ValidationError
ON FAIL LOG error, RETURN null
ON FAIL retry 3 times THEN THROW ServiceError
```

### A complete FUNC example

```logicscript
FUNC submitExpenseReport(reportId, userId)
  --- Submits a draft expense report for manager approval. ---

  VALIDATE
    report exists with id = reportId
    report.status IS draft
    report.ownerId IS userId
    report.totalAmount > 0
    report has at least one expense line item

  DO
    report.status = pending
    report.submittedAt = NOW
    EMIT ReportSubmitted WITH { reportId, userId }
    SEND notification to report.managerId

  RETURN report
  ON FAIL LOG error, THROW SubmissionError
```

---

## Describing processes: FLOW

A `FLOW` is for multi-step processes where the steps have meaningful names and need to be clear in the prompt. Use a `FLOW` instead of a `FUNC` when:

- There are 3 or more distinct stages
- Some stages might run at the same time
- You want the process documented step-by-step

### Sequential flow

Steps run one after another:

```logicscript
FLOW OnboardNewEmployee(employeeId)
  --- Runs when HR marks a new employee as active. ---

  STEP createSystemAccounts
    create accounts in email, Slack, and HR system
    set temporary password, require change on first login

  STEP assignEquipment
    create equipment request for laptop and accessories
    notify IT team

  STEP scheduleOrientation
    add employee to next available orientation session
    send calendar invite to employee and manager

  STEP notify
    send welcome email to employee.email
    send onboarding checklist to employee
    EMIT EmployeeOnboarded WITH employee
```

### Parallel flow

Use `PARALLEL` when steps can run at the same time, and `WAIT all` to pause until all of them finish:

```logicscript
FLOW GenerateMonthlyReport(month, year)
  PARALLEL
    STEP fetchSalesData
      sales = pull sales figures for month/year
    STEP fetchExpenseData
      expenses = pull expense totals for month/year
    STEP fetchHeadcountData
      headcount = pull headcount snapshot for month/year
  WAIT all

  STEP compile
    report = combine sales, expenses, headcount into report
    RETURN report
```

---

## Making decisions: IF / ELSE

Use `IF`, `ELSE IF`, and `ELSE` for conditional logic:

```logicscript
IF order.total > 1000
  apply 10% discount
  assign dedicated account manager
ELSE IF order.total > 500
  apply 5% discount
ELSE
  no discount applied
```

Short form for access rules:

```logicscript
ALLOW edit   WHEN user.role IS admin OR user.role IS editor
DENY  delete WHEN document.status IS published
DENY  access WHEN user.accountStatus IS suspended
```

---

## Checking inputs: VALIDATE

`VALIDATE` blocks can appear inside any `FUNC`. They are the system's way of refusing bad input before doing any work.

### Common patterns

```logicscript
VALIDATE
  -- The field exists and is not blank
  name not empty
  email not empty

  -- The value is in the right format
  email matches email pattern
  phone matches international phone format
  postcode matches UK postcode pattern

  -- The number is in range
  age between 18 and 120
  quantity > 0
  discount between 0 and 100

  -- The text is the right length
  username length between 3 and 30
  bio length <= 500

  -- The record exists (or doesn't)
  productId exists in Product
  email not exists in User

  -- Relational checks
  startDate is before endDate
  budget >= totalCost
```

### Plain English is always fine

If you cannot express a rule as a short condition, just write it out:

```logicscript
VALIDATE
  the invoice must have at least one line item
  line item quantities must all be positive integers
  the customer must have an active account in good standing
```

The AI will figure out how to implement it.

> **Tip:** Think of `VALIDATE` as the questions a helpful receptionist asks before letting someone through: *"Do you have an appointment? Is your ID valid? Are you on the list?"* The work only starts once all checks pass.

---

## Access control: GUARD and ALLOW / DENY

### GUARD — reusable access rules

A `GUARD` is a named access rule you define once and apply wherever you need it. This keeps access rules consistent and easy to update.

```logicscript
GUARD AdminOnly
  REQUIRE user.role IS admin
  ON FAIL THROW ForbiddenError

GUARD OwnerOrAdmin
  REQUIRE user.id IS resource.ownerId
    OR user.role IS admin
  ON FAIL THROW ForbiddenError

GUARD ActiveAccountOnly
  REQUIRE user.accountStatus IS active
  ON FAIL THROW AccountSuspendedError
```

Apply a guard to any `FUNC` by naming it at the top:

```logicscript
FUNC deleteRecord(recordId)
  GUARD AdminOnly
  DO
    Record.delete(recordId)
    LOG "Record {recordId} deleted"

FUNC editRecord(recordId, data)
  GUARD OwnerOrAdmin
  DO
    Record.update(recordId, data)
```

### ALLOW / DENY — inline permission rules

For simpler cases, use `ALLOW` and `DENY` inline:

```logicscript
ALLOW publish  WHEN user.role IS admin OR user.role IS editor
ALLOW view     WHEN document.visibility IS public OR user IS member
DENY  download WHEN document.downloadable IS false
DENY  edit     WHEN document.locked IS true
```

---

## System-wide rules: POLICY

A `POLICY` is a rule that applies across multiple functions or the entire system. Use it for rate limits, data retention, compliance requirements, and similar cross-cutting concerns.

```logicscript
POLICY RateLimit
  APPLIES TO all API endpoints
  ALLOW 100 requests PER user PER minute
  ON EXCEED return error "Too many requests, please slow down"

POLICY LoginProtection
  APPLIES TO login, passwordReset
  ALLOW 5 attempts PER ip address PER 15 minutes
  ON EXCEED lock the ip for 30 minutes, ALERT security-team

POLICY DataRetention
  APPLIES TO CustomerActivityLog
  KEEP 2 years of data
  THEN archive to long-term storage
  DELETE after 7 years

POLICY GDPRCompliance
  APPLIES TO all user data
  MASK fields: email, phone, dateOfBirth in logs and analytics
  ALLOW unmasked access WHEN user.role IS compliance-officer
```

---

## Finding records: QUERY

A `QUERY` is a saved, named search that can be reused across the system.

```logicscript
QUERY overdueInvoices
  FROM Invoice
  WHERE status IS sent
  AND   dueDate < TODAY
  ORDER BY dueDate ASC

QUERY topCustomers(limit)
  FROM Customer
  WHERE status IS active
  ORDER BY totalSpend DESC
  LIMIT limit

QUERY recentOrdersForUser(userId)
  FROM Order
  WHERE userId IS userId
  AND   createdAt WITHIN 90 days
  INCLUDE items, shippingAddress
  ORDER BY createdAt DESC
```

### QUERY clauses

| Clause                   | What it does                              |
| ------------------------ | ----------------------------------------- |
| `FROM`                 | Which record type to search               |
| `WHERE … AND …`      | Filter conditions                         |
| `ORDER BY … ASC/DESC` | Sort the results                          |
| `LIMIT N`              | Return at most N results                  |
| `OFFSET N`             | Skip the first N results (for pagination) |
| `INCLUDE`              | Also load related records                 |
| `WITHIN N days`        | Shorthand for date range filters          |

---

## Reacting to events: ON and EMIT

Events let different parts of the system communicate without being directly connected. One function fires an event; other parts of the system react to it independently.

### EMIT — fire an event

Inside any `FUNC` or `FLOW`, use `EMIT` to signal that something happened:

```logicscript
EMIT UserCreated WITH user
EMIT OrderPlaced WITH { orderId, userId, total }
EMIT LowStock    WITH { productId, currentStock }
EMIT PaymentFailed WITH { userId, amount, reason }
```

### ON — react to an event

Define what should happen when an event fires:

```logicscript
ON UserCreated
  send welcome email to user.email
  add user to mailing list
  create default settings for user
  LOG "New signup: {user.email}"

ON OrderPlaced
  send order confirmation to user.email
  notify fulfillment team
  update sales dashboard

ON LowStock
  TRIGGER PurchasingService.createReorderRequest(productId)
  ALERT inventory-manager

ON PaymentFailed 3 times
  suspend the user's account
  send notification to billing-team
  ALERT finance-manager
```

> **Tip:** Think of events as internal memos. `EMIT` is *sending the memo*. `ON` is *acting on the memo*. The sender doesn't need to know who reads it — they just send it.

---

## Tracking status: STATE

A `STATE` machine defines the valid statuses a record can have and which transitions between statuses are allowed. It prevents impossible states — for example, an invoice jumping from `draft` directly to `paid` without being `sent` first.

### Structure

```logicscript
STATE Invoice
  STATES  draft, sent, paid, overdue, cancelled

  TRANSITION draft  -> sent      ON sendInvoice
  TRANSITION sent   -> paid      ON paymentReceived
  TRANSITION sent   -> overdue   ON dueDatePassed
  TRANSITION overdue -> paid     ON paymentReceived
  TRANSITION ANY    -> cancelled ON cancelInvoice
    WHEN status NOT IN [paid]
```

### ON ENTER — hooks

Add automatic actions when a status is entered:

```logicscript
STATE Invoice
  STATES  draft, sent, paid, overdue, cancelled

  TRANSITION draft   -> sent     ON sendInvoice
  TRANSITION sent    -> paid     ON paymentReceived
  TRANSITION sent    -> overdue  ON dueDatePassed
  TRANSITION overdue -> paid     ON paymentReceived

  ON ENTER sent
    EMIT InvoiceSent WITH invoice
    LOG "Invoice {invoice.number} sent to {invoice.customerEmail}"

  ON ENTER paid
    EMIT InvoicePaid WITH invoice
    TRIGGER AccountingService.recordPayment(invoice)

  ON ENTER overdue
    EMIT InvoiceOverdue WITH invoice
    SEND reminder email to invoice.customerEmail
    ALERT accounts-receivable-team
```

### Reading a state machine

| Part                               | Meaning                                                    |
| ---------------------------------- | ---------------------------------------------------------- |
| `STATES a, b, c`                 | The complete list of valid statuses                        |
| `TRANSITION a -> b ON eventName` | Status changes from a to b when eventName happens          |
| `WHEN condition`                 | The transition only happens if this condition is also true |
| `ANY -> cancelled`               | From any status, can transition to cancelled               |
| `ON ENTER status`                | Run these steps every time this status is entered          |
| `ON EXIT status`                 | Run these steps every time this status is left             |

---

## Scheduled tasks: SCHEDULE

A `SCHEDULE` defines something that runs automatically on a timer.

```logicscript
SCHEDULE sendOverdueReminders
  AT "9:00 AM daily"
  DO
    invoices = run overdueInvoices query
    FOR EACH invoice
      SEND reminder email to invoice.customerEmail
    LOG "Sent {count} overdue reminders"

SCHEDULE weeklyDigest
  AT "Monday 8:00 AM"
  DO
    digest = compile weekly activity summary
    SEND digest to all managers

SCHEDULE cleanUpExpiredSessions
  EVERY 1 hour
  DO
    deleted = remove all sessions where expiresAt < NOW
    LOG "Cleaned up {deleted} expired sessions"

SCHEDULE monthlyBilling
  AT "1st of month 00:01 UTC"
  DO
    subscribers = all active subscriptions
    FOR EACH subscriber
      charge subscriber for their plan
      send receipt to subscriber.email
    LOG "Billed {count} subscribers"
```

### Timing options

| Format                           | Example                               | Meaning                          |
| -------------------------------- | ------------------------------------- | -------------------------------- |
| `EVERY N unit`                 | `EVERY 15 minutes`                  | Run every N minutes/hours/days   |
| `AT "time daily"`              | `AT "9:00 AM daily"`                | Run every day at a specific time |
| `AT "day of week time"`        | `AT "Monday 8:00 AM"`               | Run weekly on a specific day     |
| `AT "Nth of month time"`       | `AT "1st of month 00:01 UTC"`       | Run monthly                      |
| `AT "first day of month time"` | `AT "first day of month 08:00 UTC"` | Run at start of month            |

---

## Performance hints: Annotations

Annotations are optional notes you add to a `FUNC` or `FLOW` to give the AI extra guidance about how it should be implemented. They start with `@` and go on the line *before* the function.

You do not need to use these to write a valid prompt — they are optional optimisations.

| Annotation                                    | What it means in plain English                                                      |
| --------------------------------------------- | ----------------------------------------------------------------------------------- |
| `@cached ttl=5m key="..."`                  | Remember the result for 5 minutes; don't re-run for the same input                  |
| `@retryable attempts=3 backoff=exponential` | If this fails, try up to 3 more times before giving up                              |
| `@transaction`                              | All the steps in this function must succeed together, or none of them should happen |
| `@idempotent key="..."`                     | If called twice with the same inputs, only actually run it once                     |
| `@deprecated since="2.0" use=newFuncName`   | This is old; use the new one instead                                                |
| `@observable metrics=[latency, error_rate]` | Track how long this takes and how often it fails                                    |
| `@rateLimit 10/minute per=userId`           | Allow each user to call this at most 10 times per minute                            |

### Examples

```logicscript
@cached ttl=10m key="dashboard:{userId}"
FUNC getDashboardData(userId)
  DO
    fetch all dashboard widgets for user
  RETURN dashboard

@retryable attempts=3 backoff=exponential
FUNC sendEmailNotification(userId, template, data)
  DO
    CALL EmailService.send(userId, template, data)

@transaction
FUNC transferBalance(fromAccountId, toAccountId, amount)
  VALIDATE
    amount > 0
    fromAccountId not equals toAccountId
    fromAccount.balance >= amount
  DO
    subtract amount from fromAccount.balance
    add amount to toAccount.balance
    EMIT BalanceTransferred WITH { fromAccountId, toAccountId, amount }
```

---

## Tips for better prompts

### Do mix plain English and LogicScript

You do not have to use keywords for everything. If something is easier to say in plain English, just say it:

```logicscript
DO
  create a PDF of the invoice using the company letterhead template
  upload the PDF to the document storage system
  attach the PDF to the invoice record
```

### Keep each FUNC focused

A good function does one thing. If your `DO` block has more than 5–7 steps, consider whether some of them should be their own `FUNC` or a `FLOW`.

### Name things clearly

Use descriptive names. `FUNC submitExpenseReport` is clearer than `FUNC submit`. `SHAPE CustomerInvoice` is clearer than `SHAPE CI`.

### Add doc comments

Use `---` block comments to explain the *purpose* and *constraints* of a function in plain English:

```logicscript
FUNC approveLeaveRequest(requestId, managerId)
  --- Approves a pending leave request.
      Only the direct manager of the requesting employee may approve.
      Cannot approve requests that overlap with another approved leave period
      for the same employee. ---
  ...
```

### Be explicit about failures

Tell the AI what should happen when things go wrong:

```logicscript
ON FAIL THROW PaymentDeclinedError
ON FAIL LOG error, send alert to payments-team, RETURN failure
ON FAIL retry 2 times THEN THROW TimeoutError
```

### Annotate for safety when money is involved

Always add `@transaction` to any function that moves money, adjusts inventory, or makes multiple writes that must all succeed or all fail:

```logicscript
@transaction
FUNC processRefund(orderId, amount, reason)
  ...
```

---

## Quick reference card

### Structure keywords

```
SHAPE   Name                 — define a data record
FUNC    name(inputs)         — define an action
FLOW    Name(inputs)         — define a multi-step process
  STEP  stepName             — one stage of a flow
  PARALLEL … WAIT all        — run steps at the same time
MODULE  Name                 — group related functions
  ENTRY functionName         — mark a function as public
```

### Logic keywords

```
VALIDATE                     — pre-flight checks (stop if any fail)
DO                           — the actual steps
RETURN value                 — what the function gives back
ON FAIL THROW ErrorName      — what to do if something goes wrong
REQUIRE x ELSE THROW Error   — inline check inside DO
IF condition … ELSE          — branching logic
FOR EACH item … CALL …       — loop over a collection
```

### Access control

```
GUARD  Name                  — define a reusable access rule
  REQUIRE condition
  ON FAIL THROW Error
GUARD  Name                  — apply it inside a FUNC

ALLOW action WHEN condition  — permit something if a condition is true
DENY  action WHEN condition  — block something if a condition is true
```

### Data and events

```
QUERY  name(params)          — define a saved search
  FROM Shape
  WHERE field IS value
  AND   field < value
  ORDER BY field DESC
  LIMIT N
  INCLUDE relatedShape

EMIT  EventName WITH data    — fire an event
ON    EventName              — react when an event fires
  TRIGGER functionName(...)
  SEND  message TO recipient
  LOG   "message"
  ALERT team-name
```

### Status and scheduling

```
STATE  ShapeName             — define a status machine
  STATES  a, b, c
  TRANSITION a -> b ON event
  WHEN condition
  ON ENTER status            — runs when entering a status

SCHEDULE  jobName            — define a recurring job
  EVERY 1 hour               — or: AT "9:00 AM daily"
  DO
    steps...
```

### Common annotations

```
@transaction                 — all steps succeed or none do
@retryable attempts=3        — retry on failure
@cached ttl=5m               — cache the result
@idempotent key="..."        — only run once per unique input
@rateLimit 10/minute         — limit how often this can be called
```

---

*For the full technical specification including formal grammar and complete keyword definitions, see **logicscript-reference.md**.*
*For worked code examples in JavaScript, Python, SQL, Java, Rust, and C++, see **logicscript-examples.md**.*
