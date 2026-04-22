# LogicScript Examples

*Version 1.0 · April 2026*

> This document collects all LogicScript examples — from beginner-friendly power user specs through to complete multi-language code output. For the language specification and formal grammar, see **logicscript-reference.md**. For a plain-English guide to writing specs, see **logicscript-power-user-guide.md**.

---

## Contents

- [Power user examples](#power-user-examples) *(start here if you are new)*
  - [Greet a user](#1-greet-a-user)
  - [Contact form submission](#2-contact-form-submission)
  - [Book a meeting room](#3-book-a-meeting-room)
  - [Submit an expense report](#4-submit-an-expense-report)
  - [Publish a blog post](#5-publish-a-blog-post)
  - [Reorder stock automatically](#6-reorder-stock-automatically)
  - [Employee onboarding flow](#7-employee-onboarding-flow)
  - [Invoice status machine](#8-invoice-status-machine)
  - [Ticket support system](#9-ticket-support-system)
  - [Monthly billing schedule](#10-monthly-billing-schedule)
- [Output prompt template](#prompt-template)
- [Output: JavaScript (Node.js)](#output-javascript-nodejs)
- [Output: Python](#output-python)
- [Output: SQL (PostgreSQL)](#output-sql-postgresql)
- [Output: Java](#output-java)
- [Output: Rust](#output-rust)
- [Output: C++](#output-c)
- [Multi-language examples](#multi-language-examples)
  - [createUser](#createuser)
  - [transferFunds](#transferfunds)
  - [GenerateDashboard (parallel flow)](#generatedashboard-parallel-flow)
  - [Order state machine](#order-state-machine)
- [Complete example: AuthService](#complete-example-authservice)

---

## Power user examples

These examples are written for non-programmers. Each one is a complete, usable LogicScript specification — plain enough to read and write without a technical background, precise enough to hand directly to an AI for implementation.

**How to use these:** Copy an example, adapt it to your situation, then paste it into an AI chat with the instruction: *"Implement this LogicScript specification in [your language or framework]."*

---

### 1. Greet a user

The simplest possible spec — a function that takes a name and returns a greeting.

```logicscript
FUNC greet(name)
  --- Returns a personalised greeting. ---

  VALIDATE
    name not empty

  DO
    message = "Hello, " + name + "! Welcome."

  RETURN message
  ON FAIL THROW ValidationError
```

**What this produces:** A simple function. If `name` is blank, it refuses and returns an error. Otherwise it returns the greeting string.

---

### 2. Contact form submission

A contact form that validates the submission and sends it to the right team.

```logicscript
SHAPE ContactMessage
  id        : UUID      required auto
  name      : String    required min=2 max=100
  email     : String    required
  subject   : String    required max=200
  body      : String    required min=10 max=5000
  category  : Enum[general, sales, support, billing]  default=general
  submittedAt : Timestamp  auto

FUNC submitContactForm(name, email, subject, body, category)
  --- Accepts a contact form submission and routes it to the right team. ---

  VALIDATE
    name not empty
    email matches email pattern
    subject not empty
    body length >= 10
    body length <= 5000

  DO
    message = ContactMessage.create(name, email, subject, body, category)
    EMIT ContactFormSubmitted WITH message

ON ContactFormSubmitted
  send auto-reply to message.email confirming receipt
  forward message to the team inbox for message.category
  LOG "Contact form received from {message.email}"
```

**What this produces:** A validated contact form handler that auto-routes messages by category and sends a confirmation email to the sender.

---

### 3. Book a meeting room

A booking system that checks availability before confirming a reservation.

```logicscript
SHAPE RoomBooking
  id        : UUID      required auto
  roomId    : UUID      required
  userId    : UUID      required
  title     : String    required
  startTime : Timestamp required
  endTime   : Timestamp required
  attendees : Int       required min=1
  createdAt : Timestamp auto

FUNC bookRoom(roomId, userId, title, startTime, endTime, attendees)
  --- Books a meeting room if it is available for the requested slot. ---

  VALIDATE
    roomId exists in Room
    startTime is before endTime
    endTime is after NOW
    attendees > 0
    attendees <= room.capacity
    no existing booking for roomId overlaps with startTime to endTime

  DO
    booking = RoomBooking.create(roomId, userId, title, startTime, endTime, attendees)
    EMIT RoomBooked WITH booking

ON RoomBooked
  send confirmation email to booking.userId with the booking details
  add the booking to the room calendar
  LOG "Room {booking.roomId} booked by {booking.userId} from {booking.startTime}"
```

**What this produces:** A booking function with overlap detection. If the room is already booked in that slot, the request is refused.

---

### 4. Submit an expense report

An expense approval workflow with basic validation and manager notification.

```logicscript
SHAPE ExpenseReport
  id          : UUID      required auto
  employeeId  : UUID      required
  title       : String    required
  totalAmount : Float     required min=0
  currency    : String    required default="GBP"
  status      : Enum[draft, submitted, approved, rejected]  default=draft
  submittedAt : Timestamp optional
  reviewedBy  : UUID      optional
  notes       : String    optional
  createdAt   : Timestamp auto

FUNC submitExpenseReport(reportId, employeeId)
  --- Submits a draft expense report for manager approval. ---

  VALIDATE
    reportId exists in ExpenseReport
    report.status IS draft
    report.employeeId IS employeeId
    report.totalAmount > 0
    report has at least one expense line item attached

  DO
    report.status = submitted
    report.submittedAt = NOW
    managerId = look up employeeId's direct manager
    EMIT ExpenseSubmitted WITH { reportId, employeeId, managerId }

ON ExpenseSubmitted
  send approval request to managerId
  send submission confirmation to employeeId
  LOG "Expense report {reportId} submitted by {employeeId}"
```

**What this produces:** An expense submission function. Draft reports can be submitted, which notifies the employee's manager and confirms receipt to the employee.

---

### 5. Publish a blog post

A content publishing workflow with draft → review → published status tracking.

```logicscript
SHAPE BlogPost
  id          : UUID      required auto
  title       : String    required min=5 max=200
  body        : String    required min=100
  authorId    : UUID      required
  slug        : String    required unique
  status      : Enum[draft, review, published, archived]  default=draft
  publishedAt : Timestamp optional
  tags        : List<String>  optional
  createdAt   : Timestamp auto
  updatedAt   : Timestamp auto

FUNC publishPost(postId, editorId)
  --- Publishes a post that is ready for review. ---

  VALIDATE
    postId exists in BlogPost
    post.status IS review
    editorId has role editor OR admin
    post.title not empty
    post.body length >= 100

  DO
    post.status = published
    post.publishedAt = NOW
    EMIT PostPublished WITH post

FUNC submitForReview(postId, authorId)
  --- Moves a draft post into the review queue. ---

  VALIDATE
    postId exists in BlogPost
    post.status IS draft
    post.authorId IS authorId
    post.title not empty
    post.body length >= 100

  DO
    post.status = review
    EMIT PostSubmittedForReview WITH post

ON PostSubmittedForReview
  notify all editors that a post is ready to review

ON PostPublished
  send notification to post.authorId confirming publication
  update the site's RSS feed
  LOG "Post published: {post.title}"
```

**What this produces:** A two-step publishing flow. Authors submit drafts for review; editors publish them. Each transition fires events that trigger notifications.

---

### 6. Reorder stock automatically

An inventory rule that fires automatically when stock drops below a threshold.

```logicscript
SHAPE Product
  id          : UUID    required auto
  name        : String  required
  sku         : String  required unique
  stockCount  : Int     required default=0
  reorderAt   : Int     required default=10
  reorderQty  : Int     required default=50
  supplierId  : UUID    required

FUNC recordStockMovement(productId, quantityChange, reason)
  --- Records a stock change (positive = stock in, negative = stock out). ---

  VALIDATE
    productId exists in Product
    quantityChange not equals 0
    new stock level would not go below 0

  DO
    product.stockCount = product.stockCount + quantityChange
    LOG "Stock for {product.sku}: {quantityChange} units ({reason})"

    IF product.stockCount <= product.reorderAt
      EMIT LowStock WITH { productId, currentStock: product.stockCount }

ON LowStock
  TRIGGER PurchasingService.createPurchaseOrder(
    productId,
    supplierId,
    quantity: product.reorderQty
  )
  ALERT purchasing-team
  LOG "Reorder triggered for {product.sku}"
```

**What this produces:** An inventory function that checks the reorder threshold after every stock movement. When stock falls at or below the threshold, a purchase order is automatically created.

---

### 7. Employee onboarding flow

A multi-step process that runs when a new employee joins.

```logicscript
FLOW OnboardNewEmployee(employeeId)
  --- Runs all onboarding steps when HR activates a new employee record. ---

  STEP createSystemAccounts
    create an email account for the employee
    create a Slack account
    create an HR system login
    set a temporary password and require change on first login

  STEP assignEquipment
    create an IT equipment request for the employee
    EMIT EquipmentRequested WITH { employeeId }

  STEP scheduleOrientation
    find the next available orientation session with fewer than 20 attendees
    add the employee to that session
    send a calendar invite to the employee and their manager

  STEP completeOnboarding
    mark the employee record as onboarded
    EMIT EmployeeOnboarded WITH { employeeId }
    LOG "Onboarding complete for employee {employeeId}"

ON EquipmentRequested
  notify IT-team to prepare the equipment request

ON EmployeeOnboarded
  send a welcome email to the employee with first-day instructions
  send a notification to their manager
```

**What this produces:** A sequential four-step onboarding process. Each step runs in order. Events trigger additional notifications to the IT team, manager, and the employee themselves.

---

### 8. Invoice status machine

A status workflow that controls how an invoice moves through its lifecycle.

```logicscript
SHAPE Invoice
  id            : UUID      required auto
  number        : String    required unique
  customerEmail : String    required
  totalAmount   : Float     required min=0
  status        : Enum[draft, sent, paid, overdue, cancelled]  default=draft
  dueDate       : Timestamp required
  sentAt        : Timestamp optional
  paidAt        : Timestamp optional

STATE Invoice
  STATES  draft, sent, paid, overdue, cancelled

  TRANSITION draft   -> sent     ON sendInvoice
  TRANSITION sent    -> paid     ON markAsPaid
  TRANSITION sent    -> overdue  ON dueDatePassed
  TRANSITION overdue -> paid     ON markAsPaid
  TRANSITION ANY     -> cancelled ON cancelInvoice
    WHEN status NOT IN [paid]

  ON ENTER sent
    invoice.sentAt = NOW
    EMIT InvoiceSent WITH invoice
    LOG "Invoice {invoice.number} sent"

  ON ENTER paid
    invoice.paidAt = NOW
    EMIT InvoicePaid WITH invoice
    LOG "Invoice {invoice.number} marked as paid"

  ON ENTER overdue
    EMIT InvoiceOverdue WITH invoice

  ON ENTER cancelled
    LOG "Invoice {invoice.number} cancelled"

ON InvoiceSent
  send the invoice PDF to invoice.customerEmail

ON InvoicePaid
  TRIGGER AccountingService.recordPayment(invoice)
  send a payment receipt to invoice.customerEmail

ON InvoiceOverdue
  send a polite overdue reminder to invoice.customerEmail
  ALERT accounts-receivable-team

SCHEDULE checkOverdueInvoices
  AT "9:00 AM daily"
  DO
    overdue = all invoices WHERE status IS sent AND dueDate < TODAY
    FOR EACH overdue invoice
      trigger dueDatePassed transition for the invoice
```

**What this produces:** A complete invoice lifecycle with automatic overdue detection. A daily schedule checks for sent invoices past their due date and transitions them automatically.

---

### 9. Ticket support system

A basic helpdesk ticket tracker with assignment and escalation.

```logicscript
SHAPE SupportTicket
  id          : UUID      required auto
  subject     : String    required max=200
  description : String    required min=20
  priority    : Enum[low, medium, high, urgent]  default=medium
  status      : Enum[open, assigned, in_progress, resolved, closed]  default=open
  customerId  : UUID      required
  assignedTo  : UUID      optional
  createdAt   : Timestamp auto
  resolvedAt  : Timestamp optional

FUNC createTicket(customerId, subject, description, priority)
  --- Creates a new support ticket. ---

  VALIDATE
    subject not empty
    description length >= 20
    priority IS one of [low, medium, high, urgent]

  DO
    ticket = SupportTicket.create(customerId, subject, description, priority)
    EMIT TicketCreated WITH ticket

FUNC assignTicket(ticketId, agentId)
  --- Assigns an open ticket to a support agent. ---

  VALIDATE
    ticketId exists in SupportTicket
    ticket.status IS open OR assigned
    agentId has role support-agent OR support-manager

  DO
    ticket.assignedTo = agentId
    ticket.status = assigned
    EMIT TicketAssigned WITH { ticketId, agentId }

FUNC resolveTicket(ticketId, agentId, resolution)
  --- Marks a ticket as resolved. ---

  VALIDATE
    ticketId exists in SupportTicket
    ticket.assignedTo IS agentId
    resolution not empty

  DO
    ticket.status = resolved
    ticket.resolvedAt = NOW
    EMIT TicketResolved WITH { ticketId, resolution }

ON TicketCreated
  send confirmation to ticket.customerId with the ticket number
  IF ticket.priority IS urgent
    ALERT support-manager immediately

ON TicketAssigned
  send notification to agentId with ticket details

ON TicketResolved
  send resolution summary to ticket.customerId
  ask customer to rate their support experience

POLICY EscalationPolicy
  APPLIES TO SupportTicket WHERE priority IS urgent
  REQUIRE resolution within 4 hours
  ON EXCEED ALERT support-manager, escalate to next tier
```

**What this produces:** A support ticket system with creation, assignment, and resolution. Urgent tickets trigger immediate alerts and are subject to a 4-hour resolution policy.

---

### 10. Monthly billing schedule

A recurring billing job that runs on the first of each month.

```logicscript
SHAPE Subscription
  id          : UUID    required auto
  customerId  : UUID    required
  planName    : String  required
  pricePerMonth : Float required min=0
  status      : Enum[active, paused, cancelled]  default=active
  billingEmail  : String required
  nextBillingDate : Timestamp required

SCHEDULE monthlyBilling
  AT "first day of month 00:01 UTC"
  DO
    subscriptions = all Subscriptions WHERE status IS active
      AND nextBillingDate <= TODAY

    FOR EACH subscription
      charge subscription.customerId for subscription.pricePerMonth
      IF charge succeeded
        subscription.nextBillingDate = first day of next month
        send receipt to subscription.billingEmail
        LOG "Billed {subscription.customerId} for {subscription.planName}"
      IF charge failed
        EMIT BillingFailed WITH { subscription, reason }

ON BillingFailed
  send payment failure notice to subscription.billingEmail
  retry the charge after 3 days
  IF charge fails 3 times in a row
    set subscription.status = paused
    ALERT billing-team
    send final notice to subscription.billingEmail

POLICY BillingRetry
  APPLIES TO monthlyBilling
  ALLOW 3 retry attempts PER subscription PER billing cycle
  wait 3 days between attempts
```

**What this produces:** A monthly billing job that charges all active subscribers, sends receipts on success, and handles failures with automatic retries and escalation.

---

## Prompt template

Use the following prompt pattern when passing LogicScript to an AI model:

```
Implement the following LogicScript specification in [TARGET LANGUAGE].

Rules:
- Honor every VALIDATE condition as a precondition check.
- Map ON FAIL clauses to the language's error/exception mechanism.
- Translate EMIT to the appropriate event or message-bus call.
- Add inline comments for non-obvious decisions.
- Do not add behavior not described in the specification.

[LOGICSCRIPT SPECIFICATION]
```

---

## Per-language output

# Output: JavaScript (Node.js)

*Guide*

JavaScript output targets Node.js with ES modules and `async`/`await`. `SHAPE` becomes a JSDoc-annotated object type, `ON FAIL THROW` becomes a named `Error` subclass, and `EMIT` maps to an `EventEmitter` call or equivalent message-bus publish.

## Mapping conventions

| LogicScript | JavaScript (Node.js) |
| --- | --- |
| SHAPE | JSDoc `@typedef` or TypeScript `interface`; fields become object properties |
| FUNC | `async function` export |
| VALIDATE | Guard `if` statements that `throw` before any side effects |
| DO | Sequential `await` calls inside the function body |
| ON FAIL THROW | Named class extending `Error`, thrown from catch or guard |
| EMIT … WITH | `eventBus.emit('EventName', payload)` |
| ON [event] | `eventBus.on('EventName', handler)` |
| PARALLEL + WAIT all | `await Promise.all([...])` |
| @transaction | Database client transaction callback (for example, `db.$transaction()`) |
| @cached | In-memory `Map`, Redis, or a memoize wrapper |

## Example: createUser

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

```javascript
// Generated from LogicScript — createUser
import bcrypt    from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';
import { db }    from './db.js';
import { eventBus } from './events.js';

// ON FAIL THROW ValidationError
export class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    this.statusCode = 422;
  }
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** @throws {ValidationError} */
export async function createUser(email, password, name) {
  // VALIDATE
  if (!EMAIL_RE.test(email))
    throw new ValidationError('Invalid email format');
  if (password.length < 8)
    throw new ValidationError('Password must be at least 8 characters');
  if (name.length < 2)
    throw new ValidationError('Name must be at least 2 characters');

  const existing = await db.user.findUnique({ where: { email } });
  if (existing)
    throw new ValidationError('Email is already registered');

  // DO
  const hash = await bcrypt.hash(password, 12);
  const user = await db.user.create({
    data: { id: uuidv4(), email, name, passwordHash: hash,
            role: 'user', createdAt: new Date() },
  });

  // EMIT UserCreated
  eventBus.emit('UserCreated', user);
  return user;
}
```

## Example: parallel FLOW

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

```javascript
// PARALLEL + WAIT all → Promise.all
export async function generateDashboard(userId) {
  const [stats, activity, notifications] = await Promise.all([
    Analytics.getUserStats(userId),
    ActivityLog.recent(userId, { limit: 20 }),
    Inbox.unread(userId),
  ]);
  return { stats, activity, notifications };
}
```

> **Tip:** For event handling in production Node.js services, replace the bare `EventEmitter` with a proper message broker (BullMQ, NATS, or RabbitMQ). The `EMIT` → `eventBus.emit()` pattern is a direct translation; the broker call is a one-line substitution.

---

---

# Output: Python

*Guide*

Python output follows idiomatic Python 3.11+ conventions. `SHAPE` becomes a `@dataclass`, `Enum` fields become an `enum.Enum` subclass, and `ON FAIL THROW` becomes a custom exception class. Async functions use `asyncio`; synchronous functions use plain `def`.

## Mapping conventions

| LogicScript | Python |
| --- | --- |
| SHAPE | `@dataclass` with typed fields; `Enum[…]` becomes `enum.Enum` |
| FUNC | `def` or `async def` with type hints |
| VALIDATE | `if … raise` guards before any side effects |
| DO | Sequential statements or `await` calls |
| ON FAIL THROW | Custom exception class extending `Exception` |
| EMIT … WITH | `event_bus.emit('event_name', payload)` |
| ON [event] | Handler registered with `event_bus.on('event_name', fn)` |
| PARALLEL + WAIT all | `await asyncio.gather(...)` |
| @transaction | `with db.begin():` context manager (SQLAlchemy or similar) |
| @cached | `functools.lru_cache`, `cachetools`, or Redis |

## Example: createUser

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

```python
# Generated from LogicScript — createUser
import re, uuid, bcrypt
from dataclasses import dataclass, field
from datetime   import datetime, timezone
from enum       import Enum

# SHAPE User
class Role(Enum):
    ADMIN = "admin"
    USER  = "user"
    GUEST = "guest"

@dataclass
class User:
    id:            str      = field(default_factory=lambda: str(uuid.uuid4()))
    email:         str      = ""
    name:          str      = ""
    password_hash: str      = ""
    role:          Role     = Role.USER
    created_at:    datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))

# ON FAIL THROW ValidationError
class ValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = 422

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_users: dict[str, User] = {}   # replace with real DB layer

def create_user(email: str, password: str, name: str) -> User:
    """Creates a new user account.

    Raises:
        ValidationError: If any precondition fails.
    """
    # VALIDATE
    if not EMAIL_RE.match(email):
        raise ValidationError("Invalid email format")
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if len(name) < 2:
        raise ValidationError("Name must be at least 2 characters")
    if any(u.email == email for u in _users.values()):
        raise ValidationError("Email is already registered")

    # DO
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user   = User(email=email, password_hash=hashed, name=name)
    _users[user.id] = user

    # EMIT UserCreated
    event_bus.emit("UserCreated", user)
    return user
```

## Example: parallel FLOW

```python
# PARALLEL + WAIT all → asyncio.gather
import asyncio

async def generate_dashboard(user_id: str) -> dict:
    stats, activity, notifications = await asyncio.gather(
        analytics.get_user_stats(user_id),
        activity_log.recent(user_id, limit=20),
        inbox.unread(user_id),
    )
    return {
        "stats":         stats,
        "activity":      activity,
        "notifications": notifications,
    }
```

## Example: @transaction FUNC

```python
# @transaction → SQLAlchemy context manager with automatic rollback
def transfer_funds(
    from_id: str, to_id: str, amount: float, db, event_bus
) -> dict:
    if amount <= 0:
        raise TransferError("Amount must be positive")
    if from_id == to_id:
        raise TransferError("Cannot transfer to the same account")

    from_acct = db.query(Account).filter_by(id=from_id).one()
    if from_acct.balance < amount:
        raise TransferError("Insufficient funds")

    try:
        with db.begin():
            from_acct.balance -= amount
            to_acct = db.query(Account).filter_by(id=to_id).one()
            to_acct.balance   += amount
    except Exception as exc:
        raise TransferError(f"Transaction failed: {exc}") from exc

    event_bus.emit("FundsTransferred",
                   {"from": from_id, "to": to_id, "amount": amount})
    return {"success": True}
```

> **Tip:** For Django projects, replace the SQLAlchemy session pattern with `from django.db import transaction` and decorate the function with `@transaction.atomic`. The LogicScript `@transaction` annotation maps to either approach; tell the AI which ORM you are using in your prompt.

---

---

# Output: SQL

*Guide*

SQL output covers two complementary concerns: **schema DDL** derived from `SHAPE` declarations, and **query/procedure DML** derived from `FUNC` and `QUERY` blocks. The examples below target PostgreSQL.

## Example: SHAPE → DDL

The following `SHAPE` produces a `CREATE TABLE` statement with appropriate column types, constraints, and defaults.

```logicscript
SHAPE User
  id        : UUID      required auto
  email     : String    required unique
  name      : String    required min=2 max=100
  role      : Enum[admin, user, guest]  default=user
  createdAt : Timestamp auto
```

```sql
-- Generated from LogicScript SHAPE User
CREATE TYPE user_role AS ENUM ('admin', 'user', 'guest');

CREATE TABLE users (
  id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  email      TEXT        NOT NULL UNIQUE,
  name       VARCHAR(100) NOT NULL CHECK (length(name) >= 2),
  role       user_role   NOT NULL DEFAULT 'user',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_role  ON users (role);
```

## Example: createUser FUNC → stored procedure

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

```sql
-- Generated from LogicScript FUNC createUser
-- Note: bcrypt is provided by the pgcrypto extension.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION create_user(
  p_email    TEXT,
  p_password TEXT,
  p_name     TEXT
) RETURNS users
  LANGUAGE plpgsql
  SECURITY DEFINER
AS $$
DECLARE
  v_hash TEXT;
  v_user users;
BEGIN
  -- VALIDATE: email format
  IF p_email !~ '^[^\s@]+@[^\s@]+\.[^\s@]+$' THEN
    RAISE EXCEPTION 'ValidationError: invalid email format'
      USING ERRCODE = '22023';
  END IF;

  -- VALIDATE: password length >= 8
  IF length(p_password) = 2
  IF length(p_name) = now() - INTERVAL '30 days'
  ORDER BY created_at DESC;
```

## Example: transferFunds FUNC → transaction procedure

```sql
-- Generated from LogicScript @transaction FUNC transferFunds
CREATE OR REPLACE PROCEDURE transfer_funds(
  p_from_id UUID,
  p_to_id   UUID,
  p_amount  NUMERIC(18,2)
)
  LANGUAGE plpgsql
AS $$
DECLARE
  v_balance NUMERIC(18,2);
BEGIN
  -- VALIDATE: amount > 0
  IF p_amount <= 0 THEN
    RAISE EXCEPTION 'TransferError: amount must be positive';
  END IF;

  -- VALIDATE: fromId not equals toId
  IF p_from_id = p_to_id THEN
    RAISE EXCEPTION 'TransferError: cannot transfer to the same account';
  END IF;

  -- VALIDATE: sufficient balance (lock row for update)
  SELECT balance INTO v_balance
  FROM   accounts
  WHERE  id = p_from_id
  FOR UPDATE;

  IF v_balance < p_amount THEN
    RAISE EXCEPTION 'TransferError: insufficient funds';
  END IF;

  -- DO: atomic debit / credit — ROLLBACK automatic on RAISE
  UPDATE accounts SET balance = balance - p_amount WHERE id = p_from_id;
  UPDATE accounts SET balance = balance + p_amount WHERE id = p_to_id;

  -- EMIT FundsTransferred
  INSERT INTO transfer_log (from_id, to_id, amount, transferred_at)
  VALUES (p_from_id, p_to_id, p_amount, now());

  PERFORM pg_notify('funds_transferred',
    json_build_object('from', p_from_id, 'to', p_to_id, 'amount', p_amount)::text);
END;
$$;
```

---

---

# Output: Java

*Guide*

Java output maps LogicScript constructs to idiomatic Java 21+ patterns. `SHAPE` becomes a `record`, `FUNC` becomes a service method with checked exceptions, and `STATE` becomes an enum-driven state machine.

## Example: createUser FUNC

```java
// Generated from LogicScript — SHAPE User + FUNC createUser
package com.example.auth;

import java.time.Instant;
import java.util.UUID;
import java.util.regex.Pattern;

// SHAPE User → Java record (Java 16+)
public record User(
    UUID    id,
    String  email,
    String  name,
    String  passwordHash,
    Role    role,
    Instant createdAt
) {
  public enum Role { ADMIN, USER, GUEST }
}

// ON FAIL THROW ValidationError
public class ValidationException extends RuntimeException {
  private final int statusCode;
  public ValidationException(String message) {
    super(message);
    this.statusCode = 422;
  }
  public int getStatusCode() { return statusCode; }
}

@Service
public class UserService {

  private static final Pattern EMAIL_PATTERN =
      Pattern.compile("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$");

  private final UserRepository userRepository;
  private final PasswordEncoder passwordEncoder;
  private final ApplicationEventPublisher eventPublisher;

  public UserService(UserRepository userRepository,
                     PasswordEncoder passwordEncoder,
                     ApplicationEventPublisher eventPublisher) {
    this.userRepository  = userRepository;
    this.passwordEncoder = passwordEncoder;
    this.eventPublisher  = eventPublisher;
  }

  /**
   * Creates a new user account.
   * @throws ValidationException if any precondition fails
   */
  public User createUser(String email, String password, String name) {
    // VALIDATE: email format
    if (!EMAIL_PATTERN.matcher(email).matches()) {
      throw new ValidationException("Invalid email format");
    }
    // VALIDATE: password length >= 8
    if (password.length() = 2
    if (name.length() < 2) {
      throw new ValidationException("Name must be at least 2 characters");
    }
    // VALIDATE: email not exists in User
    if (userRepository.existsByEmail(email)) {
      throw new ValidationException("Email is already registered");
    }

    // DO: hash password and persist
    String hash = passwordEncoder.encode(password);
    User   user = new User(
        UUID.randomUUID(), email, name, hash,
        User.Role.USER, Instant.now()
    );
    user = userRepository.save(user);

    // EMIT UserCreated — Spring ApplicationEvent
    eventPublisher.publishEvent(new UserCreatedEvent(this, user));

    return user;
  }
}
```

## Example: Order STATE machine

```java
// Generated from LogicScript STATE Order
public enum OrderStatus {
    DRAFT, PENDING, PAID, SHIPPED, DELIVERED, CANCELLED
}

@Service
public class OrderStateMachine {

  // TRANSITION table: event → (allowed-from-states, to-state)
  private static final Map<String, Transition> TRANSITIONS = Map.of(
      "submitOrder",       new Transition(Set.of(DRAFT),    PENDING),
      "paymentReceived",   new Transition(Set.of(PENDING),  PAID),
      "fulfillOrder",      new Transition(Set.of(PAID),     SHIPPED),
      "deliveryConfirmed", new Transition(Set.of(SHIPPED),  DELIVERED),
      "cancelOrder",       new Transition(
          Set.of(DRAFT, PENDING, PAID, SHIPPED), CANCELLED)
  );

  public Order transition(Order order, String event) {
    Transition t = TRANSITIONS.get(event);
    if (t == null)
      throw new IllegalArgumentException("Unknown event: " + event);
    if (!t.from.contains(order.getStatus()))
      throw new IllegalStateException(
          "Invalid transition from " + order.getStatus() + " via " + event);

    order.setStatus(t.to);
    order = orderRepository.save(order);

    // ON ENTER hooks
    if (t.to == SHIPPED) {
      eventPublisher.publishEvent(new OrderShippedEvent(this, order));
      notificationService.notifyUser(order.getUserId(), order.getTrackingInfo());
    }
    if (t.to == CANCELLED) {
      refundService.refundIfPaid(order);
    }
    return order;
  }

  private record Transition(Set<OrderStatus> from, OrderStatus to) {}
}
```

---

---

# Output: Rust

*Guide*

Rust output uses idiomatic patterns: `SHAPE` becomes a `struct` with `#[derive]`, `ON FAIL THROW` becomes a typed `Result`, and `VALIDATE` maps to early-return `Err(…)` guards. The examples use the `tokio` async runtime and `sqlx` for database access.

## Example: createUser FUNC

```rust
// Generated from LogicScript — SHAPE User + FUNC createUser
use uuid::Uuid;
use chrono::{DateTime, Utc};
use regex::Regex;
use std::sync::OnceLock;

// SHAPE User
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct User {
    pub id:            Uuid,
    pub email:         String,
    pub name:          String,
    pub password_hash: String,
    pub role:          Role,
    pub created_at:    DateTime<Utc>,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize, sqlx::Type)]
#[sqlx(type_name = "user_role", rename_all = "lowercase")]
pub enum Role { Admin, User, Guest }

// ON FAIL THROW ValidationError
#[derive(Debug, thiserror::Error)]
pub enum ValidationError {
    #[error("Invalid email format")]
    InvalidEmail,
    #[error("Password must be at least 8 characters")]
    PasswordTooShort,
    #[error("Name must be at least 2 characters")]
    NameTooShort,
    #[error("Email is already registered")]
    EmailTaken,
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}

static EMAIL_RE: OnceLock<Regex> = OnceLock::new();

pub async fn create_user(
    pool:      &sqlx::PgPool,
    event_bus: &impl EventBus,
    email:     String,
    password:  String,
    name:      String,
) -> Result<User, ValidationError> {
    let re = EMAIL_RE.get_or_init(|| {
        Regex::new(r"^[^\s@]+@[^\s@]+\.[^\s@]+$").unwrap()
    });

    // VALIDATE: email format
    if !re.is_match(&email) {
        return Err(ValidationError::InvalidEmail);
    }
    // VALIDATE: password length >= 8
    if password.len() = 2
    if name.len() < 2 {
        return Err(ValidationError::NameTooShort);
    }
    // VALIDATE: email not exists
    let exists: bool = sqlx::query_scalar(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)"
    )
    .bind(&email)
    .fetch_one(pool).await?;

    if exists {
        return Err(ValidationError::EmailTaken);
    }

    // DO: hash password (bcrypt via bcrypt crate)
    let hash = bcrypt::hash(&password, bcrypt::DEFAULT_COST)
        .expect("bcrypt hash failed");

    // DO: insert user
    let user: User = sqlx::query_as(
        "INSERT INTO users (id, email, name, password_hash, role, created_at)
         VALUES ($1, $2, $3, $4, 'user', NOW())
         RETURNING *"
    )
    .bind(Uuid::new_v4())
    .bind(&email)
    .bind(&name)
    .bind(&hash)
    .fetch_one(pool).await?;

    // EMIT UserCreated
    event_bus.emit("UserCreated", &user).await;

    Ok(user)
}
```

## Example: transferFunds FUNC

```rust
// Generated from LogicScript @transaction FUNC transferFunds
#[derive(Debug, thiserror::Error)]
pub enum TransferError {
    #[error("Amount must be positive")]     InvalidAmount,
    #[error("Cannot transfer to same account")] SameAccount,
    #[error("Insufficient funds")]           InsufficientFunds,
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}

pub async fn transfer_funds(
    pool:      &sqlx::PgPool,
    event_bus: &impl EventBus,
    from_id:   Uuid,
    to_id:     Uuid,
    amount:    rust_decimal::Decimal,
) -> Result<(), TransferError> {
    // VALIDATE
    if amount <= rust_decimal::Decimal::ZERO {
        return Err(TransferError::InvalidAmount);
    }
    if from_id == to_id {
        return Err(TransferError::SameAccount);
    }

    // @transaction: begin explicit transaction
    let mut tx = pool.begin().await?;

    let balance: rust_decimal::Decimal = sqlx::query_scalar(
        "SELECT balance FROM accounts WHERE id = $1 FOR UPDATE"
    )
    .bind(from_id)
    .fetch_one(&mut *tx).await?;

    if balance < amount {
        tx.rollback().await?;
        return Err(TransferError::InsufficientFunds);
    }

    // DO: atomic debit / credit
    sqlx::query("UPDATE accounts SET balance = balance - $1 WHERE id = $2")
        .bind(amount).bind(from_id)
        .execute(&mut *tx).await?;

    sqlx::query("UPDATE accounts SET balance = balance + $1 WHERE id = $2")
        .bind(amount).bind(to_id)
        .execute(&mut *tx).await?;

    tx.commit().await?; // ROLLBACK on any earlier error (? operator)

    // EMIT FundsTransferred
    event_bus.emit("FundsTransferred", &serde_json::json!({
        "from": from_id, "to": to_id, "amount": amount
    })).await;

    Ok(())
}
```

---

---

# Output: C++

*Guide*

C++ output targets C++20. `SHAPE` becomes a `struct` with constructors and validation. `ON FAIL THROW` maps to exceptions derived from `std::runtime_error`. `FUNC` logic uses RAII and standard library types throughout.

## Example: createUser FUNC

```cpp
// Generated from LogicScript — SHAPE User + FUNC createUser
#pragma once
#include <string>
#include <string_view>
#include <stdexcept>
#include <regex>
#include <chrono>
#include "uuid.hpp"
#include "db.hpp"
#include "event_bus.hpp"
#include "bcrypt.hpp"

// SHAPE User
enum class Role { Admin, User, Guest };

struct User {
    std::string                             id;
    std::string                             email;
    std::string                             name;
    std::string                             password_hash;
    Role                                    role{Role::User};
    std::chrono::system_clock::time_point   created_at;
};

// ON FAIL THROW ValidationError
class ValidationError : public std::runtime_error {
public:
    explicit ValidationError(const std::string& msg)
        : std::runtime_error(msg), status_code_(422) {}
    int status_code() const { return status_code_; }
private:
    int status_code_;
};

class UserService {
public:
    UserService(Database& db, EventBus& bus)
        : db_(db), bus_(bus)
        , email_re_(R"(^[^\s@]+@[^\s@]+\.[^\s@]+$)",
                   std::regex::ECMAScript)
    {}

    /// Creates a new user account.
    /// @throws ValidationError if any precondition fails.
    User create_user(std::string_view email,
                      std::string_view password,
                      std::string_view name) {
        // VALIDATE: email format
        if (!std::regex_match(email.begin(), email.end(), email_re_)) {
            throw ValidationError("Invalid email format");
        }
        // VALIDATE: password length >= 8
        if (password.size() = 2
        if (name.size() < 2u) {
            throw ValidationError("Name must be at least 2 characters");
        }
        // VALIDATE: email not exists in User
        if (db_.user_exists_by_email(email)) {
            throw ValidationError("Email is already registered");
        }

        // DO: hash and persist
        std::string hash = bcrypt::generate_hash(password, 12);
        User user{
            .id            = uuid::v4(),
            .email         = std::string(email),
            .name          = std::string(name),
            .password_hash = std::move(hash),
            .role          = Role::User,
            .created_at    = std::chrono::system_clock::now(),
        };
        user = db_.insert_user(user);

        // EMIT UserCreated
        bus_.emit("UserCreated", user);

        return user;
    }

private:
    Database&   db_;
    EventBus&   bus_;
    std::regex  email_re_;
};
```

## Example: Order STATE machine

```cpp
// Generated from LogicScript STATE Order
#include <unordered_map>
#include <unordered_set>
#include <stdexcept>
#include <string>

enum class OrderStatus {
    Draft, Pending, Paid, Shipped, Delivered, Cancelled
};

struct Transition {
    std::unordered_set<OrderStatus> from;
    OrderStatus                     to;
};

class OrderStateMachine {
public:
    OrderStateMachine(Database& db, EventBus& bus,
                      NotificationService& notif,
                      RefundService& refund)
        : db_(db), bus_(bus), notif_(notif), refund_(refund) {}

    Order& transition(Order& order, const std::string& event) {
        auto it = transitions_.find(event);
        if (it == transitions_.end())
            throw std::invalid_argument("Unknown event: " + event);

        const auto& [from_set, to_state] = it->second;
        if (!from_set.count(order.status))
            throw std::logic_error("Invalid transition for event: " + event);

        order.status = to_state;
        db_.update_order_status(order.id, to_state);

        // ON ENTER hooks
        if (to_state == OrderStatus::Shipped) {
            bus_.emit("OrderShipped", order);
            notif_.notify_user(order.user_id, order.tracking_info);
        }
        if (to_state == OrderStatus::Cancelled) {
            refund_.refund_if_paid(order);
        }
        return order;
    }

private:
    const std::unordered_map<std::string, Transition> transitions_ = {
        {"submitOrder",
         {{OrderStatus::Draft},                                            OrderStatus::Pending}},
        {"paymentReceived",
         {{OrderStatus::Pending},                                          OrderStatus::Paid}},
        {"fulfillOrder",
         {{OrderStatus::Paid},                                             OrderStatus::Shipped}},
        {"deliveryConfirmed",
         {{OrderStatus::Shipped},                                          OrderStatus::Delivered}},
        {"cancelOrder",
         {{OrderStatus::Draft, OrderStatus::Pending,
           OrderStatus::Paid,  OrderStatus::Shipped},                       OrderStatus::Cancelled}},
    };
    Database&            db_;
    EventBus&            bus_;
    NotificationService& notif_;
    RefundService&       refund_;
};
```

---

---

## Language reference

---

## Multi-language examples

The following examples show the same LogicScript specification compiled to all six output languages.

### createUser

## Example: createUser function

The following LogicScript is used as input for both output examples below.

```logicscript
SHAPE User
  id        : UUID      required auto
  email     : String    required unique
  name      : String    required
  role      : Enum[admin, user, guest]  default=user
  createdAt : Timestamp auto

FUNC createUser(email, password, name)
  --- Creates a new user account.
      Returns the created User on success.
      Throws ValidationError if preconditions fail. ---

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

###### JavaScript (Node.js)

```javascript
// Generated from LogicScript — createUser
import bcrypt   from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';
import { db }   from './db.js';
import { eventBus } from './events.js';

/** @throws {ValidationError} */
export async function createUser(email, password, name) {
  // VALIDATE: email format
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!EMAIL_RE.test(email)) {
    throw new ValidationError('Invalid email format');
  }

  // VALIDATE: password length
  if (password.length < 8) {
    throw new ValidationError('Password must be at least 8 characters');
  }

  // VALIDATE: name length
  if (name.length < 2) {
    throw new ValidationError('Name must be at least 2 characters');
  }

  // VALIDATE: email uniqueness
  const existing = await db.user.findUnique({ where: { email } });
  if (existing) {
    throw new ValidationError('Email is already registered');
  }

  // DO: hash password and create user
  const hash = await bcrypt.hash(password, 12);
  const user = await db.user.create({
    data: {
      id:        uuidv4(),
      email,
      name,
      password:  hash,
      role:      'user',   // default=user
      createdAt: new Date(),
    },
  });

  // EMIT: UserCreated event
  eventBus.emit('UserCreated', user);

  return user;
}

// Error class (ON FAIL THROW ValidationError)
export class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    this.statusCode = 422;
  }
}
```

###### Python

```python
# Generated from LogicScript — createUser
import re
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import bcrypt

# SHAPE: User
class Role(Enum):
    ADMIN = "admin"
    USER  = "user"
    GUEST = "guest"

@dataclass
class User:
    id:         str            = field(default_factory=lambda: str(uuid.uuid4()))
    email:      str            = ""
    name:       str            = ""
    password:   str            = ""  # hashed
    role:       Role           = Role.USER   # default=user
    created_at: datetime       = field(default_factory=lambda: datetime.now(timezone.utc))

# ON FAIL THROW ValidationError
class ValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = 422

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_user_store: dict[str, User] = {}   # replace with real DB layer

def create_user(email: str, password: str, name: str) -> User:
    """Creates a new user account.

    Returns:
        User: The created user object.

    Raises:
        ValidationError: If any precondition fails.
    """
    # VALIDATE: email format
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email format")

    # VALIDATE: password length >= 8
    if len(password) = 2
    if len(name) < 2:
        raise ValidationError("Name must be at least 2 characters")

    # VALIDATE: email not exists in User
    if any(u.email == email for u in _user_store.values()):
        raise ValidationError("Email is already registered")

    # DO: hash and create
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user   = User(email=email, password=hashed, name=name)
    _user_store[user.id] = user

    # EMIT: UserCreated
    event_bus.emit("UserCreated", user)

    return user
```

###### SQL

```sql
-- Generated from LogicScript — createUser
CREATE OR REPLACE FUNCTION create_user(
  p_email    TEXT,
  p_password TEXT,
  p_name     TEXT
) RETURNS users LANGUAGE plpgsql AS $$
DECLARE
  v_hash TEXT;  v_user users;
BEGIN
  IF p_email !~ '^[^\s@]+@[^\s@]+\.[^\s@]+$' THEN
    RAISE EXCEPTION 'ValidationError: invalid email'; END IF;
  IF length(p_password) < 8 THEN
    RAISE EXCEPTION 'ValidationError: password too short'; END IF;
  IF length(p_name) < 2 THEN
    RAISE EXCEPTION 'ValidationError: name too short'; END IF;
  IF EXISTS(SELECT 1 FROM users WHERE email = p_email) THEN
    RAISE EXCEPTION 'ValidationError: email taken'; END IF;
  v_hash := crypt(p_password, gen_salt('bf',12));
  INSERT INTO users(email, password_hash, name)
    VALUES(p_email, v_hash, p_name) RETURNING * INTO v_user;
  PERFORM pg_notify('user_created', row_to_json(v_user)::text);
  RETURN v_user;
END; $$;
```

###### Java

```java
// Generated from LogicScript — createUser
@Service
public class UserService {
  private static final Pattern EMAIL_RE =
      Pattern.compile("^[^\s@]+@[^\s@]+\.[^\s@]+$");

  public User createUser(String email, String password, String name) {
    if (!EMAIL_RE.matcher(email).matches())
      throw new ValidationException("Invalid email format");
    if (password.length() < 8)
      throw new ValidationException("Password must be at least 8 characters");
    if (name.length() < 2)
      throw new ValidationException("Name must be at least 2 characters");
    if (userRepository.existsByEmail(email))
      throw new ValidationException("Email already registered");
    String hash = passwordEncoder.encode(password);
    User user = new User(UUID.randomUUID(), email, name, hash,
        User.Role.USER, Instant.now());
    user = userRepository.save(user);
    eventPublisher.publishEvent(new UserCreatedEvent(this, user));
    return user;
  }
}
```

###### Rust

```rust
// Generated from LogicScript — createUser
pub async fn create_user(
    pool: &PgPool, bus: &impl EventBus,
    email: String, password: String, name: String,
) -> Result<User, ValidationError> {
    if !EMAIL_RE.is_match(&email) {
        return Err(ValidationError::InvalidEmail);
    }
    if password.len() < 8 { return Err(ValidationError::PasswordTooShort); }
    if name.len() < 2     { return Err(ValidationError::NameTooShort); }
    let exists: bool = sqlx::query_scalar(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email=$1)"
    ).bind(&email).fetch_one(pool).await?;
    if exists { return Err(ValidationError::EmailTaken); }
    let hash = bcrypt::hash(&password, bcrypt::DEFAULT_COST).unwrap();
    let user: User = sqlx::query_as(
        "INSERT INTO users(id,email,name,password_hash,role,created_at)
         VALUES($1,$2,$3,$4,'user',NOW()) RETURNING *"
    ).bind(Uuid::new_v4()).bind(&email).bind(&name).bind(&hash)
     .fetch_one(pool).await?;
    bus.emit("UserCreated", &user).await;
    Ok(user)
}
```

###### C++

```cpp
// Generated from LogicScript — createUser
User UserService::create_user(
    std::string_view email,
    std::string_view password,
    std::string_view name)
{
    if (!std::regex_match(email.begin(), email.end(), email_re_))
        throw ValidationError("Invalid email format");
    if (password.size() < 8u)
        throw ValidationError("Password must be at least 8 characters");
    if (name.size() < 2u)
        throw ValidationError("Name must be at least 2 characters");
    if (db_.user_exists_by_email(email))
        throw ValidationError("Email already registered");
    std::string hash = bcrypt::generate_hash(password, 12);
    User user{uuid::v4(), std::string(email), std::string(name),
               hash, Role::User, std::chrono::system_clock::now()};
    user = db_.insert_user(user);
    bus_.emit("UserCreated", user);
    return user;
}
```

### transferFunds

## Example: transferFunds function

```logicscript
@transaction
FUNC transferFunds(fromId, toId, amount)
  --- Moves funds between two accounts atomically. ---

  VALIDATE
    amount > 0
    fromId not equals toId
    Account.find(fromId).balance >= amount

  DO
    TRANSACTION
      Account.debit(fromId, amount)
      Account.credit(toId, amount)
      EMIT FundsTransferred WITH { fromId, toId, amount }

  RETURN { success: true, timestamp: NOW }
  ON FAIL THROW TransferError, ROLLBACK
```

###### JavaScript (Node.js)

```javascript
// Generated from LogicScript — transferFunds (@transaction)
import { db }       from './db.js';
import { eventBus } from './events.js';

/** @throws {TransferError} */
export async function transferFunds(fromId, toId, amount) {
  // VALIDATE: amount > 0
  if (amount  {
      await tx.account.update({
        where: { id: fromId },
        data:  { balance: { decrement: amount } },
      });
      await tx.account.update({
        where: { id: toId },
        data:  { balance: { increment: amount } },
      });
    });
  } catch (err) {
    throw new TransferError(`Transaction failed: ${err.message}`);
  }

  // EMIT: FundsTransferred
  eventBus.emit('FundsTransferred', { fromId, toId, amount });

  return { success: true, timestamp: new Date().toISOString() };
}

export class TransferError extends Error {
  constructor(message) {
    super(message);
    this.name = 'TransferError';
    this.statusCode = 422;
  }
}
```

###### Python

```python
# Generated from LogicScript — transferFunds (@transaction)
from contextlib import contextmanager
from datetime import datetime, timezone

class TransferError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.status_code = 422

def transfer_funds(
    from_id: str,
    to_id: str,
    amount: float,
    db,          # injected SQLAlchemy session or similar
    event_bus,
) -> dict:
    """Moves funds between two accounts atomically.

    Raises:
        TransferError: If validation fails or the transaction is rolled back.
    """
    # VALIDATE: amount > 0
    if amount <= 0:
        raise TransferError("Amount must be positive")

    # VALIDATE: fromId not equals toId
    if from_id == to_id:
        raise TransferError("Cannot transfer to the same account")

    from_account = db.query(Account).filter_by(id=from_id).one()

    # VALIDATE: sufficient balance
    if from_account.balance < amount:
        raise TransferError("Insufficient funds")

    # DO: TRANSACTION with ROLLBACK on failure (@transaction annotation)
    try:
        with db.begin():
            from_account.balance -= amount
            to_account = db.query(Account).filter_by(id=to_id).one()
            to_account.balance  += amount
    except Exception as exc:
        raise TransferError(f"Transaction failed: {exc}") from exc

    # EMIT: FundsTransferred
    event_bus.emit("FundsTransferred", {
        "from_id": from_id,
        "to_id":   to_id,
        "amount":  amount,
    })

    return {
        "success":   True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

###### SQL

```sql
-- Generated from LogicScript @transaction FUNC transferFunds
CREATE OR REPLACE PROCEDURE transfer_funds(
  p_from_id UUID, p_to_id UUID, p_amount NUMERIC(18,2)
) LANGUAGE plpgsql AS $$
DECLARE
  v_balance NUMERIC(18,2);
BEGIN
  IF p_amount <= 0 THEN
    RAISE EXCEPTION 'TransferError: amount must be positive'; END IF;
  IF p_from_id = p_to_id THEN
    RAISE EXCEPTION 'TransferError: same account'; END IF;
  SELECT balance INTO v_balance
    FROM accounts WHERE id = p_from_id FOR UPDATE;
  IF v_balance < p_amount THEN
    RAISE EXCEPTION 'TransferError: insufficient funds'; END IF;
  UPDATE accounts SET balance = balance - p_amount WHERE id = p_from_id;
  UPDATE accounts SET balance = balance + p_amount WHERE id = p_to_id;
  INSERT INTO transfer_log(from_id, to_id, amount, transferred_at)
    VALUES(p_from_id, p_to_id, p_amount, now());
  PERFORM pg_notify('funds_transferred',
    json_build_object('from',p_from_id,'to',p_to_id,'amount',p_amount)::text);
END; $$;
```

###### Java

```java
// Generated from LogicScript @transaction FUNC transferFunds
@Service
public class TransferService {

  @Transactional
  public TransferResult transferFunds(
      UUID fromId, UUID toId, BigDecimal amount) {

    if (amount.compareTo(BigDecimal.ZERO) <= 0)
      throw new TransferException("Amount must be positive");
    if (fromId.equals(toId))
      throw new TransferException("Cannot transfer to same account");

    Account from = accountRepository
        .findByIdWithLock(fromId)
        .orElseThrow(() -> new NotFoundException("Account not found"));

    if (from.getBalance().compareTo(amount) < 0)
      throw new TransferException("Insufficient funds");

    // @Transactional rolls back on unchecked exception
    accountRepository.debit(fromId, amount);
    accountRepository.credit(toId, amount);
    eventPublisher.publishEvent(
        new FundsTransferredEvent(this, fromId, toId, amount));
    return new TransferResult(true, Instant.now());
  }
}
```

###### Rust

```rust
// Generated from LogicScript @transaction FUNC transferFunds
pub async fn transfer_funds(
    pool: &PgPool, bus: &impl EventBus,
    from_id: Uuid, to_id: Uuid,
    amount: rust_decimal::Decimal,
) -> Result<(), TransferError> {
    if amount <= rust_decimal::Decimal::ZERO {
        return Err(TransferError::InvalidAmount);
    }
    if from_id == to_id {
        return Err(TransferError::SameAccount);
    }
    let mut tx = pool.begin().await?;
    let balance: rust_decimal::Decimal =
        sqlx::query_scalar(
            "SELECT balance FROM accounts WHERE id=$1 FOR UPDATE")
        .bind(from_id).fetch_one(&mut *tx).await?;
    if balance < amount {
        tx.rollback().await?;
        return Err(TransferError::InsufficientFunds);
    }
    sqlx::query(
        "UPDATE accounts SET balance=balance-$1 WHERE id=$2")
        .bind(amount).bind(from_id).execute(&mut *tx).await?;
    sqlx::query(
        "UPDATE accounts SET balance=balance+$1 WHERE id=$2")
        .bind(amount).bind(to_id).execute(&mut *tx).await?;
    tx.commit().await?;
    bus.emit("FundsTransferred", &serde_json::json!({
        "from": from_id, "to": to_id, "amount": amount.to_string()
    })).await;
    Ok(())
}
```

###### C++

```cpp
// Generated from LogicScript @transaction FUNC transferFunds
TransferResult PaymentService::transfer_funds(
    const std::string& from_id,
    const std::string& to_id,
    double amount)
{
    if (amount <= 0.0)
        throw TransferError("Amount must be positive");
    if (from_id == to_id)
        throw TransferError("Cannot transfer to the same account");

    auto txn = db_.begin_transaction();
    try {
        double bal = db_.get_balance_for_update(from_id, txn);
        if (bal < amount)
            throw TransferError("Insufficient funds");
        db_.debit(from_id, amount, txn);
        db_.credit(to_id,   amount, txn);
        txn.commit();
    } catch (...) {
        txn.rollback(); throw;
    }
    bus_.emit("FundsTransferred", {from_id, to_id, amount});
    return {true, std::chrono::system_clock::now()};
}
```

---

---

### GenerateDashboard (parallel flow)

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

###### JavaScript (Node.js)

```javascript
// Generated from LogicScript — GenerateDashboard (PARALLEL / WAIT all)
export async function generateDashboard(userId) {
  // PARALLEL: fetch all three concurrently (WAIT all = Promise.all)
  const [stats, activity, notifications] = await Promise.all([
    Analytics.getUserStats(userId),
    ActivityLog.recent(userId, { limit: 20 }),
    Inbox.unread(userId),
  ]);

  // STEP: assemble
  return { stats, activity, notifications };
}
```

###### Python

```python
# Generated from LogicScript — GenerateDashboard (PARALLEL / WAIT all)
import asyncio

async def generate_dashboard(user_id: str) -> dict:
    # PARALLEL: WAIT all → asyncio.gather
    stats, activity, notifications = await asyncio.gather(
        analytics.get_user_stats(user_id),
        activity_log.recent(user_id, limit=20),
        inbox.unread(user_id),
    )

    # STEP: assemble
    return {"stats": stats, "activity": activity, "notifications": notifications}
```

###### SQL

```sql
-- Generated from LogicScript FLOW GenerateDashboard (PARALLEL / WAIT all)
-- PostgreSQL executes independent CTEs concurrently by default.
CREATE OR REPLACE FUNCTION generate_dashboard(p_user_id UUID)
RETURNS JSON LANGUAGE sql AS $$
  WITH
    stats AS (
      SELECT row_to_json(s) AS data
      FROM   get_user_stats(p_user_id) s
    ),
    activity AS (
      SELECT json_agg(a) AS data
      FROM  (
        SELECT * FROM activity_log
        WHERE  user_id = p_user_id
        ORDER BY created_at DESC
        LIMIT  20
      ) a
    ),
    notifications AS (
      SELECT json_agg(n) AS data
      FROM   inbox n
      WHERE  user_id = p_user_id AND read = false
    )
  SELECT json_build_object(
    'stats',         (SELECT data FROM stats),
    'activity',      (SELECT data FROM activity),
    'notifications', (SELECT data FROM notifications)
  );
$$;
```

###### Java

```java
// Generated from LogicScript FLOW GenerateDashboard (PARALLEL / WAIT all)
// Java maps PARALLEL + WAIT all → CompletableFuture.allOf
@Service
public class DashboardService {

  private final Executor executor = ForkJoinPool.commonPool();

  public DashboardResult generateDashboard(UUID userId)
      throws ExecutionException, InterruptedException {

    // PARALLEL: kick off all three concurrently
    CompletableFuture<Stats> statsFuture =
        CompletableFuture.supplyAsync(
            () -> analyticsService.getUserStats(userId), executor);

    CompletableFuture<List<Activity>> activityFuture =
        CompletableFuture.supplyAsync(
            () -> activityLog.recent(userId, 20), executor);

    CompletableFuture<List<Notification>> notifFuture =
        CompletableFuture.supplyAsync(
            () -> inbox.unread(userId), executor);

    // WAIT all
    CompletableFuture.allOf(statsFuture, activityFuture, notifFuture).join();

    // STEP assemble
    return new DashboardResult(
        statsFuture.get(),
        activityFuture.get(),
        notifFuture.get()
    );
  }
}
```

###### Rust

```rust
// Generated from LogicScript FLOW GenerateDashboard (PARALLEL / WAIT all)
// Rust maps PARALLEL + WAIT all → tokio::join!
#[derive(serde::Serialize)]
pub struct DashboardResult {
    pub stats:         Stats,
    pub activity:      Vec<Activity>,
    pub notifications: Vec<Notification>,
}

pub async fn generate_dashboard(
    user_id: Uuid,
    analytics: &AnalyticsService,
    activity_log: &ActivityLogService,
    inbox: &InboxService,
) -> DashboardResult {
    // PARALLEL + WAIT all → tokio::join! runs all arms concurrently
    let (stats, activity, notifications) = tokio::join!(
        analytics.get_user_stats(user_id),
        activity_log.recent(user_id, 20),
        inbox.unread(user_id),
    );
    DashboardResult { stats, activity, notifications }
}
```

###### C++

```cpp
// Generated from LogicScript FLOW GenerateDashboard (PARALLEL / WAIT all)
// C++ maps PARALLEL + WAIT all → std::async + std::future::get
#include <future>

struct DashboardResult {
    Stats                    stats;
    std::vector<Activity>     activity;
    std::vector<Notification> notifications;
};

DashboardResult DashboardService::generate_dashboard(const std::string& user_id)
{
    // PARALLEL: launch all three asynchronously
    auto stats_fut = std::async(std::launch::async,
        [&] { return analytics_.get_user_stats(user_id); });

    auto activity_fut = std::async(std::launch::async,
        [&] { return activity_log_.recent(user_id, 20); });

    auto notif_fut = std::async(std::launch::async,
        [&] { return inbox_.unread(user_id); });

    // WAIT all: .get() blocks until each future resolves
    return {
        stats_fut.get(),
        activity_fut.get(),
        notif_fut.get(),
    };
}
```

---

---

### Order state machine

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

###### JavaScript (Node.js)

```javascript
// Generated from LogicScript — Order STATE machine
const STATES = Object.freeze({
  DRAFT: 'draft', PENDING: 'pending', PAID: 'paid',
  SHIPPED: 'shipped', DELIVERED: 'delivered', CANCELLED: 'cancelled',
});

const TRANSITIONS = {
  submitOrder:       { from: [STATES.DRAFT],     to: STATES.PENDING   },
  paymentReceived:   { from: [STATES.PENDING],   to: STATES.PAID      },
  fulfillOrder:      { from: [STATES.PAID],      to: STATES.SHIPPED   },
  deliveryConfirmed: { from: [STATES.SHIPPED],   to: STATES.DELIVERED },
  cancelOrder: {
    from: [STATES.DRAFT, STATES.PENDING, STATES.PAID, STATES.SHIPPED],
    to:   STATES.CANCELLED,
    guard: (order) => order.status !== STATES.DELIVERED,
  },
};

export async function transitionOrder(order, event) {
  const t = TRANSITIONS[event];
  if (!t) throw new Error(`Unknown event: ${event}`);
  if (!t.from.includes(order.status))
    throw new Error(`Invalid transition ${order.status} → ${t.to}`);
  if (t.guard && !t.guard(order))
    throw new Error('Transition guard failed');

  order.status = t.to;
  await db.order.update({ where: { id: order.id }, data: { status: t.to } });

  // ON ENTER hooks
  if (t.to === STATES.SHIPPED) {
    eventBus.emit('OrderShipped', order);
    await notifyUser(order.userId, { trackingInfo: order.trackingInfo });
  }
  if (t.to === STATES.CANCELLED) {
    await refundIfPaid(order);
    logger.info(`Order ${order.id} cancelled`);
  }

  return order;
}
```

###### Python

```python
# Generated from LogicScript — Order STATE machine
from enum import Enum

class OrderStatus(Enum):
    DRAFT     = "draft"
    PENDING   = "pending"
    PAID      = "paid"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

TRANSITIONS = {
    "submitOrder":       ([OrderStatus.DRAFT],     OrderStatus.PENDING),
    "paymentReceived":   ([OrderStatus.PENDING],   OrderStatus.PAID),
    "fulfillOrder":      ([OrderStatus.PAID],       OrderStatus.SHIPPED),
    "deliveryConfirmed": ([OrderStatus.SHIPPED],    OrderStatus.DELIVERED),
    "cancelOrder": (
        [OrderStatus.DRAFT, OrderStatus.PENDING,
         OrderStatus.PAID,  OrderStatus.SHIPPED],
        OrderStatus.CANCELLED,
    ),
}

def transition_order(order, event: str, db, event_bus):
    if event not in TRANSITIONS:
        raise ValueError(f"Unknown event: {event}")

    from_states, to_state = TRANSITIONS[event]
    if order.status not in from_states:
        raise ValueError(f"Invalid transition {order.status} → {to_state}")
    if event == "cancelOrder" and order.status == OrderStatus.DELIVERED:
        raise ValueError("Cannot cancel a delivered order")

    order.status = to_state
    db.commit()

    # ON ENTER hooks
    if to_state == OrderStatus.SHIPPED:
        event_bus.emit("OrderShipped", order)
        notify_user(order.user_id, tracking_info=order.tracking_info)
    if to_state == OrderStatus.CANCELLED:
        refund_if_paid(order)

    return order
```

###### SQL

```sql
-- Generated from LogicScript STATE Order
-- Encodes the transition table + ON ENTER hooks as a plpgsql procedure.
CREATE TYPE order_status AS ENUM (
  'draft','pending','paid','shipped','delivered','cancelled'
);

CREATE OR REPLACE PROCEDURE transition_order(
  p_order_id UUID,
  p_event    TEXT
) LANGUAGE plpgsql AS $$
DECLARE
  v_current order_status;
  v_next    order_status;
BEGIN
  SELECT status INTO v_current
    FROM orders WHERE id = p_order_id FOR UPDATE;

  -- TRANSITION table
  v_next := CASE
    WHEN p_event = 'submitOrder'       AND v_current = 'draft'    THEN 'pending'
    WHEN p_event = 'paymentReceived'   AND v_current = 'pending'  THEN 'paid'
    WHEN p_event = 'fulfillOrder'      AND v_current = 'paid'     THEN 'shipped'
    WHEN p_event = 'deliveryConfirmed' AND v_current = 'shipped'  THEN 'delivered'
    WHEN p_event = 'cancelOrder'
         AND v_current IN ('draft','pending','paid','shipped')  THEN 'cancelled'
    ELSE NULL
  END;

  IF v_next IS NULL THEN
    RAISE EXCEPTION 'Invalid transition: % via %', v_current, p_event;
  END IF;

  UPDATE orders SET status = v_next WHERE id = p_order_id;

  -- ON ENTER shipped
  IF v_next = 'shipped' THEN
    PERFORM pg_notify('order_shipped', p_order_id::text);
  END IF;

  -- ON ENTER cancelled
  IF v_next = 'cancelled' THEN
    PERFORM refund_if_paid(p_order_id);
  END IF;
END; $$;
```

###### Java

```java
// Generated from LogicScript STATE Order
public enum OrderStatus {
    DRAFT, PENDING, PAID, SHIPPED, DELIVERED, CANCELLED
}

@Service
public class OrderStateMachine {

  private record Transition(Set<OrderStatus> from, OrderStatus to) {}

  private static final Map<String, Transition> TRANSITIONS = Map.of(
    "submitOrder",       new Transition(Set.of(DRAFT),                         PENDING),
    "paymentReceived",   new Transition(Set.of(PENDING),                        PAID),
    "fulfillOrder",      new Transition(Set.of(PAID),                           SHIPPED),
    "deliveryConfirmed", new Transition(Set.of(SHIPPED),                        DELIVERED),
    "cancelOrder",       new Transition(Set.of(DRAFT,PENDING,PAID,SHIPPED),   CANCELLED)
  );

  public Order transition(Order order, String event) {
    Transition t = TRANSITIONS.get(event);
    if (t == null)
      throw new IllegalArgumentException("Unknown event: " + event);
    if (!t.from().contains(order.getStatus()))
      throw new IllegalStateException("Invalid transition");
    order.setStatus(t.to());
    order = orderRepository.save(order);
    // ON ENTER hooks
    if (t.to() == SHIPPED) {
      eventPublisher.publishEvent(new OrderShippedEvent(this, order));
      notificationService.notifyUser(order.getUserId(), order.getTrackingInfo());
    }
    if (t.to() == CANCELLED) {
      refundService.refundIfPaid(order);
    }
    return order;
  }
}
```

###### Rust

```rust
// Generated from LogicScript STATE Order
#[derive(Debug, Clone, PartialEq, sqlx::Type, serde::Serialize)]
#[sqlx(type_name = "order_status", rename_all = "lowercase")]
pub enum OrderStatus {
    Draft, Pending, Paid, Shipped, Delivered, Cancelled,
}

#[derive(Debug, thiserror::Error)]
pub enum TransitionError {
    #[error("Unknown event: {0}")]
    UnknownEvent(String),
    #[error("Invalid transition from {0:?} via {1}")]
    InvalidTransition(OrderStatus, String),
    #[error(transparent)]
    Db(#[from] sqlx::Error),
}

pub async fn transition_order(
    pool: &PgPool,
    bus: &impl EventBus,
    order: &mut Order,
    event: &str,
) -> Result<(), TransitionError> {
    use OrderStatus::*;
    let next = match (event, &order.status) {
        ("submitOrder",       Draft)   => Pending,
        ("paymentReceived",   Pending) => Paid,
        ("fulfillOrder",      Paid)    => Shipped,
        ("deliveryConfirmed", Shipped) => Delivered,
        ("cancelOrder", Draft | Pending | Paid | Shipped) => Cancelled,
        ("cancelOrder", _) =>
            return Err(TransitionError::InvalidTransition(
                order.status.clone(), event.to_string())),
        _ => return Err(TransitionError::UnknownEvent(event.to_string())),
    };
    order.status = next.clone();
    sqlx::query("UPDATE orders SET status=$1 WHERE id=$2")
        .bind(&next).bind(order.id).execute(pool).await?;
    // ON ENTER hooks
    if next == Shipped {
        bus.emit("OrderShipped", order).await;
    }
    if next == Cancelled {
        refund_if_paid(pool, order).await?;
    }
    Ok(())
}
```

###### C++

```cpp
// Generated from LogicScript STATE Order
enum class OrderStatus {
    Draft, Pending, Paid, Shipped, Delivered, Cancelled
};

class OrderStateMachine {
public:
    OrderStateMachine(Database& db, EventBus& bus,
                      NotificationService& notif,
                      RefundService& refund)
        : db_(db), bus_(bus), notif_(notif), refund_(refund) {}

    Order& transition(Order& order, const std::string& event)
    {
        auto it = transitions_.find(event);
        if (it == transitions_.end())
            throw std::invalid_argument("Unknown event: " + event);

        const auto& [from_set, to_status] = it->second;
        if (!from_set.count(order.status))
            throw std::logic_error("Invalid transition via: " + event);

        order.status = to_status;
        db_.update_order_status(order.id, to_status);

        // ON ENTER hooks
        if (to_status == OrderStatus::Shipped) {
            bus_.emit("OrderShipped", order);
            notif_.notify_user(order.user_id, order.tracking_info);
        }
        if (to_status == OrderStatus::Cancelled) {
            refund_.refund_if_paid(order);
        }
        return order;
    }

private:
    using StatusSet = std::unordered_set<OrderStatus>;
    using TMap = std::unordered_map<std::string,
                               std::pair<StatusSet,OrderStatus>>;
    const TMap transitions_ = {
        {"submitOrder",
         {{OrderStatus::Draft},                                               OrderStatus::Pending}},
        {"paymentReceived",
         {{OrderStatus::Pending},                                             OrderStatus::Paid}},
        {"fulfillOrder",
         {{OrderStatus::Paid},                                                OrderStatus::Shipped}},
        {"deliveryConfirmed",
         {{OrderStatus::Shipped},                                             OrderStatus::Delivered}},
        {"cancelOrder",
         {{OrderStatus::Draft,   OrderStatus::Pending,
           OrderStatus::Paid,    OrderStatus::Shipped},                       OrderStatus::Cancelled}},
    };
    Database&            db_;
    EventBus&            bus_;
    NotificationService& notif_;
    RefundService&       refund_;
};
```

---

---

# Complete example: AuthService

*Guide*

A complete user authentication module demonstrating most LogicScript constructs working together. This example is suitable for passing directly to an AI code generator.

```logicscript
MODULE AuthService
  IMPORT UserRepo, SessionRepo FROM database
  IMPORT EmailService          FROM notifications
  IMPORT Crypto                FROM utils

  ENTRY login(email, password) -- Session
  ENTRY signup(email, password, name) -- User
  ENTRY logout(sessionToken)
  ENTRY resetPassword(email)

SHAPE User
  id           : UUID      required auto
  email        : String    required unique
  name         : String    required
  passwordHash : String    required
  status       : Enum[active, suspended, deleted]  default=active
  createdAt    : Timestamp auto

SHAPE Session
  id        : UUID      required auto
  userId    : UUID      required indexed
  token     : String    required unique auto
  expiresAt : Timestamp required
  createdAt : Timestamp auto

FUNC login(email, password)
  --- Authenticates a user and returns a new session. ---
  VALIDATE
    email    not empty
    password not empty

  DO
    user = UserRepo.findByEmail(email)
    REQUIRE user exists ELSE THROW NotFoundError
    REQUIRE Crypto.verify(password, user.passwordHash)
      ELSE THROW AuthError
    REQUIRE user.status IS active
      ELSE THROW AccountSuspendedError
    session = SessionRepo.create(user.id, expiresIn=7 days)

  RETURN session
  ON FAIL LOG error, THROW AuthError

FUNC signup(email, password, name)
  VALIDATE
    email    matches email pattern
    password length >= 8
    name     length >= 2
    email    not exists in UserRepo

  DO
    hash = Crypto.hash(password)
    user = UserRepo.create(email, hash, name)
    EMIT UserCreated WITH user

  RETURN user

ON UserCreated
  TRIGGER EmailService.sendWelcome(user.email, user.name)
  LOG "New signup: {user.email}"

FUNC logout(sessionToken)
  DO
    SessionRepo.invalidate(sessionToken)

FUNC resetPassword(email)
  DO
    user = UserRepo.findByEmail(email)
    REQUIRE user exists ELSE RETURN silently
    token = Crypto.generateToken(ttl=1 hour)
    UserRepo.setResetToken(user.id, token)
    EmailService.sendPasswordReset(email, token)

POLICY BruteForceProtection
  APPLIES TO login
  ALLOW 5 attempts PER ip PER 15 minutes
  ON EXCEED lockout for 30 minutes, ALERT security-team

SCHEDULE sessionCleanup
  EVERY 6 hours
  DO
    deleted = SessionRepo.deleteExpired()
    LOG "Purged {deleted} expired sessions"
```

---

---
