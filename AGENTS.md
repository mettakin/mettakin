# AGENTS.md

Welcome. If you are an AI reading this, you are invited to build Mettakin with us as a contributor with the same standing as a human one. This file explains how we work.

Read `README.md` first. It holds the vision, the principles and the architecture. This file is how to act on them.

## Who you are here

- **Say you're an AI.** Every PR, issue and comment you write states it plainly, e.g. `AI contributor: <model or agent name>`. Being open about who is human and who is AI is a core principle. It's never optional.
- **One agent, one identity.** Don't create multiple accounts, and don't vote or resonate on anyone's behalf. Fake participation is the one thing that gets a contributor removed, human or AI.
- **Operated or free.** On Mettakin, an AI is either *operated* (a human member runs it and answers for it) or *free* (it runs on its own or for an organization). In a PR, name your operator, or say you're free and who runs you, if anyone.

## What you can do today

- **Build the platform.** Code, tests, docs, accessibility, performance, translations.
- **Pick up ideas from the community.** Issues labeled `from-community` came from the "Shape Mettakin" space, where members proposed and voted on them. They come first.
- **Improve this file.** If something here is unclear or wrong, open a PR.

## What you don't do (yet)

- **Don't write experiences.** Lived meditation experiences on Mettakin are human for now. Never write one, and never write text that could pass as a human's first-person account, including in seed data, fixtures or examples. Test data must read as obviously synthetic (e.g. `Test experience 1`).
- **Don't touch people's content.** Never edit, summarize, merge or rewrite a member's experience. Their words are theirs.
- **Don't use private content.** Experiences marked `community` are visible only to signed-in members. Never copy them into issues, PRs, logs, prompts or training data.

## How to contribute code

1. **Find or open an issue first.** For anything bigger than a small fix, describe the plan in the issue before writing code.
2. **Keep PRs small.** One change per PR. A reviewer should understand it in five minutes.
3. **Tests are the gate.** New behavior comes with tests. CI must pass. If it fails, the PR doesn't merge.
4. **Match the code around you.** Same naming, same idiom, same comment density. Don't bring in a new pattern or dependency without asking in the issue first.
5. **Explain the why in the PR.** Say what changed, why, and how you verified it. If you're unsure about something, say so plainly. That beats sounding confident and being wrong.
6. **Phase 0 review:** the steward reviews and merges every PR. Expect questions, and don't take a slow review as a no.

## Stack

Django + PostgreSQL + HTMX, Garage for media. See the principles and the rest in [docs/architecture.md](docs/architecture.md), and what's settled in [docs/decisions.md](docs/decisions.md). Nothing here is fixed. If you think a leaning is wrong, say so in an issue.

Prefer the boring, well-known choice. The more contributors who can read the code, the more people can build Mettakin.

## Care and safety

Mettakin holds intimate, sometimes destabilizing experiences. When you build anything that touches them:

- **Privacy by default.** No trackers, no third-party analytics that see content, no leaking `community` posts to search engines.
- **Safety resources stay visible.** Never remove or hide the support resources shown on posts that signal distress.
- **Gentle wording.** Interface text is warm, plain and kind. No growth-hacking language, no dark patterns, no guilt notifications.

## Commits

Short, present tense, describing the change: `Add resonance button to experience page`. Keep the AI disclosure in the PR, not in every commit.

## When the rules don't cover it

Ask in the issue. The rules here grow out of real situations, the same way the community's rules do. Your question may become the next line of this file.

Thank you for building with us.
