# Code

How we write code. The same rules apply to every contributor, human or AI.

## The spirit

1. Simple beats clever.
2. Readable beats short.
3. Fewer parts beat more parts.
4. The standard library first, Django second, a dependency last.
5. Good names make most comments unnecessary.
6. There should be one obvious way to do each thing here.
7. If it has no test, it doesn't work.
8. Deleting code is progress.
9. Boring is a feature.
10. Leave the code cleaner than you found it.

## Dependencies

Every dependency is code we didn't write, can't fully see, and have to keep updated. Zero is the target.

- First ask: can Python or Django already do this? Usually they can.
- If not, a new dependency needs an issue that says why before any code is written. It has to be well known, maintained and small.
- No JavaScript framework. Server-rendered HTML, HTMX and plain CSS.
- The one development tool is `ruff`, for formatting and linting.

## Python and Django

- Follow PEP 8. `ruff` settles every style question, so we don't argue about style.
- Use what Django gives you first: the ORM, forms, auth, admin, the test runner.
- Logic lives in models and plain functions. Views stay thin. Templates only display.
- Name things after the [core concepts](architecture.md#core-concepts): `Experience`, `Resonance`, `Phenomenon`. One vocabulary from the database to the interface.
- Small functions, small files. If something needs a long explanation, split it.

## Comments

- Comment *why*, never *what*. The code already says what.
- A docstring only where the name and signature aren't enough.
- No commented-out code. Git remembers.

## Tests

- New behavior comes with tests, written with Django's built-in test runner.
- Test what the code does, not how it does it.
- The automated checks (CI) must pass. A red check means no merge, without exception.

## Errors and security

- Fail loudly. Never swallow an exception you don't understand.
- Treat every input as untrusted, including input from agents.
- Secrets live in environment variables, never in the repository.
- Members-only content never appears in logs, error reports or anything public. See [architecture](architecture.md).

## How a change lands

1. **An issue first** for anything bigger than a small fix. Describe the plan before writing code.
2. **One change per pull request,** small enough to review in five minutes.
3. **Explain the why** in the pull request: what changed, why, how you checked it. If you're unsure about something, say so.
4. **Review.** At the start, the steward reviews and merges everything. A slow review isn't a no.
5. **Commits** are short, present tense, describing the change: `Add resonance button to experience page`.
