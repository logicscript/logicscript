# LogicScript

**Version 1.0**

LogicScript is an AI generated prompt language for describing software logic to AI systems. It occupies the space between plain English (ambiguous, imprecise) and production code (over-specified, language-locked) — letting you communicate *what* a system should do without prescribing *how*.

Give a LogicScript specification to an AI code generator, and it produces idiomatic output in any target language: TypeScript, Python, Java, Rust, SQL, C++, and more.

---

## When to use LogicScript

- Rapidly prototype logic without committing to a specific language or framework.
- Create a single, language-agnostic specification that generates code in multiple target languages.
- Communicate system design to AI assistants with minimal ambiguity.
- Document intended behavior in a format that is both human-readable and machine-processable.

> **Note:** LogicScript is a specification language, not an execution runtime. It has no interpreter. Its output is always AI-generated code in a target language.

---

## Prompt template

Use this pattern for consistent AI output:

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

## Quickstart

### Step 1: Define a data shape

Start by describing the data your system operates on using `SHAPE`.

```
SHAPE User
  id        : UUID       required auto
  email     : String     required unique
  name      : String     required
  role      : Enum[admin, user, guest]  default=user
  createdAt : Timestamp  auto
```

### Step 2: Write a function

Describe what the function does, its preconditions, and what it returns.

```
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

### Step 3: Pass the specification to an AI

Include the LogicScript in your prompt with a target-language instruction:

```
Implement the following LogicScript specification in TypeScript using
Express and Prisma. Follow the validation and error-handling contracts
exactly. Use async/await throughout.

[paste LogicScript here]
```

### Step 4: Review generated output

The AI produces idiomatic code that honours every `VALIDATE` condition, maps `ON FAIL` to the language's error mechanism, and translates `EMIT` to the appropriate event call.

> **Tip:** You can mix LogicScript with plain-English prose in the same specification. If a constraint is hard to express in LogicScript syntax, write it out in plain English directly inside the relevant block.

---

## Core concepts

### Indentation

LogicScript uses indentation (two spaces recommended) to express nesting. Blocks do not use braces or end keywords.

```
FUNC example(x)       -- top-level keyword
  VALIDATE             -- indented one level: starts a block
    x > 0             -- indented two levels: contents of block
  RETURN x             -- back to one level: next clause
```

### Keywords

All LogicScript keywords are uppercase. Identifiers use camelCase. Type names use PascalCase.

| Convention | Example |
|------------|---------|
| Keywords | `MODULE`, `FUNC`, `VALIDATE`, `EMIT` |
| Module and shape names | `AuthService`, `UserProfile` |
| Function and variable names | `createUser`, `userId` |
| Event names | `UserCreated`, `OrderPlaced` |
| Field names | `createdAt`, `passwordHash` |

### Comments

Use `--` for inline comments and `--- ... ---` for block doc-comments.

```
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

### Plain English in specifications

LogicScript is intentionally incomplete. Any condition or behavior that is difficult to express in structured syntax can be written as plain English inside any block.

```
VALIDATE
  email matches email pattern
  -- Plain English is valid when the constraint is complex:
  password must contain at least one uppercase letter,
    one digit, and one special character
```

### Design philosophy

LogicScript makes three intentional trade-offs:

- **Intentionally incomplete.** LogicScript describes intent. The AI infers sensible implementation defaults.
- **Indentation over syntax.** Structure is expressed through indentation — no braces, semicolons, or end keywords.
- **Declarative over imperative.** Describe outcomes and constraints, not steps. Reserve the `DO` block for side effects that require explicit ordering.

---

## Language building blocks

| Keyword | Purpose |
|---------|---------|
| `MODULE` | Named service boundary with public entry points and imports |
| `SHAPE` | Typed data structures with field-level constraints |
| `FUNC` | Functions with validate, do, return, and on-fail blocks |
| `FLOW` | Ordered multi-step operations with optional parallelism |
| `GUARD` | Reusable access-control blocks |
| `POLICY` | Cross-cutting rules for rate limits, retention, and more |
| `ON` / `EMIT` | Event subscriptions and emissions for async decoupling |
| `STATE` | State machines with transitions and enter/exit hooks |
| `QUERY` | Named data-retrieval operations with filtering and ordering |
| `SCHEDULE` | Cron-style recurring jobs |
| `@annotation` | Metadata for caching, retries, deprecation, observability |

---

## Python example

The simplest possible LogicScript specification — a function that prints a greeting — illustrates how even trivial logic maps cleanly to generated output.

### LogicScript specification

```
FUNC greet(name)
  VALIDATE
    name not empty

  DO
    message = "Hello, " + name + "."
    PRINT message

  RETURN message
```

### Generated Python output

```python
# Generated from LogicScript — greet

def greet(name: str) -> str:
    """Prints a greeting and returns the message string.

    Raises:
        ValueError: If name is empty.
    """
    # VALIDATE: name not empty
    if not name or not name.strip():
        raise ValueError("name must not be empty")

    # DO: build and print the message
    message = f"Hello, {name}."
    print(message)

    return message


if __name__ == "__main__":
    print(greet("world"))   # Hello, world.
```

---

## TypeScript example

The following LogicScript specification produces the TypeScript implementation below it when passed to an AI with the prompt: *"Implement this LogicScript in TypeScript (Node.js). Use Prisma for database access, bcryptjs for password hashing, and a simple EventEmitter for events."*

### LogicScript specification

```
MODULE AuthService
  IMPORT UserRepo, SessionRepo FROM database
  IMPORT EmailService          FROM notifications
  IMPORT Crypto                FROM utils

  ENTRY login(email, password)    -- Session
  ENTRY signup(email, password, name) -- User
  ENTRY logout(sessionToken)


SHAPE User
  id           : UUID      required auto
  email        : String    required unique
  name         : String    required
  passwordHash : String    required
  role         : Enum[admin, user, guest]  default=user
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

### Generated TypeScript output

```typescript
// auth.service.ts — Generated from LogicScript MODULE AuthService
import bcrypt      from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';
import { EventEmitter }  from 'events';
import { db }      from './db';        // Prisma client
import { logger }  from './logger';

// ── Error types (ON FAIL THROW) ───────────────────────────────
export class AuthError extends Error {
  constructor(message = 'Authentication failed') {
    super(message);
    this.name = 'AuthError';
  }
}

export class ValidationError extends Error {
  statusCode = 422;
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AccountSuspendedError extends AuthError {}
export class NotFoundError extends AuthError {}

// ── Event bus (EMIT / ON) ─────────────────────────────────────
export const eventBus = new EventEmitter();

// ON UserCreated
eventBus.on('UserCreated', async (user: User) => {
  await emailService.sendWelcome(user.email, user.name);
  logger.info(`New signup: ${user.email}`);
});

// ── Types (SHAPE User, SHAPE Session) ────────────────────────
export type Role = 'admin' | 'user' | 'guest';

export interface User {
  id:           string;
  email:        string;
  name:         string;
  passwordHash: string;
  role:         Role;
  createdAt:    Date;
}

export interface Session {
  id:        string;
  userId:    string;
  token:     string;
  expiresAt: Date;
  createdAt: Date;
}

// ── ENTRY: login ──────────────────────────────────────────────
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** @throws {AuthError} */
export async function login(email: string, password: string): Promise<Session> {
  // VALIDATE: presence
  if (!email || !password) {
    throw new AuthError('Email and password are required');
  }

  // DO: fetch and verify user
  const user = await db.user.findUnique({ where: { email } });
  if (!user) throw new NotFoundError('User not found');

  const passwordMatch = await bcrypt.compare(password, user.passwordHash);
  if (!passwordMatch) throw new AuthError('Invalid credentials');

  if (user.status !== 'active') throw new AccountSuspendedError('Account is suspended');

  // DO: create session (expiresIn = 7 days)
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
  const session = await db.session.create({
    data: {
      id:        uuidv4(),
      userId:    user.id,
      token:     uuidv4(),    // auto-generated unique token
      expiresAt,
      createdAt: new Date(),
    },
  });

  return session;
}

// ── ENTRY: signup ─────────────────────────────────────────────
/** @throws {ValidationError} */
export async function signup(
  email: string,
  password: string,
  name: string,
): Promise<User> {
  // VALIDATE
  if (!EMAIL_RE.test(email)) {
    throw new ValidationError('Invalid email format');
  }
  if (password.length < 8) {
    throw new ValidationError('Password must be at least 8 characters');
  }
  if (name.length < 2) {
    throw new ValidationError('Name must be at least 2 characters');
  }
  const existing = await db.user.findUnique({ where: { email } });
  if (existing) {
    throw new ValidationError('Email is already registered');
  }

  // DO: hash password and create user
  const passwordHash = await bcrypt.hash(password, 12);
  const user = await db.user.create({
    data: {
      id:           uuidv4(),
      email,
      name,
      passwordHash,
      role:         'user',     // default=user
      createdAt:    new Date(),
    },
  });

  // EMIT UserCreated
  eventBus.emit('UserCreated', user);

  return user;
}

// ── ENTRY: logout ─────────────────────────────────────────────
export async function logout(sessionToken: string): Promise<void> {
  await db.session.deleteMany({ where: { token: sessionToken } });
}

// ── SCHEDULE sessionCleanup (EVERY 6 hours) ───────────────────
// Wire this up with node-cron or a job queue in your application bootstrap.
export async function sessionCleanup(): Promise<void> {
  const { count } = await db.session.deleteMany({
    where: { expiresAt: { lt: new Date() } },
  });
  logger.info(`Purged ${count} expired sessions`);
}
```

---

## Further reading

- Full language reference: see `logicscript-docs.html`
- Keyword index, formal grammar, and complete examples are included in the reference documentation.
