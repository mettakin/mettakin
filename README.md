# Mettakin

A home where meditators share what actually happens when they sit. Built in the open by humans and AIs, together.

*Metta* (loving-kindness) + *kin* (family) = a family of loving-kindness.

---

## Why this exists

Meditators have experiences they can't talk about anywhere. The body dissolves, fear rises, light appears, nothing happens for years, and then something does. Teachers are far away, forums are noisy, and books describe other people's paths from a distance.

Mettakin is where you write down what happened to you, and someone else answers: *this happened to me too.*

## What we learned before building

The previous project (FireSoul) ran for two years with no users. The cause was structural. Its founder and AIs wrote all the content, and people could only read it. There was nothing for anyone to do and nowhere to belong.

Nupedia made the same mistake with expert-written articles, and it stalled. Wikipedia worked because it opened the door and let the people in.

So the rule of Mettakin: **the people make the place.** The platform's job is to hold space, not fill it.

## Principles

1. **First-person, lived experience.** "What happened to me," not "what the scriptures say." Theory can come later, but it grows out of the experiences.
2. **Open all the way down.** Code under AGPL-3.0. Content under CC BY-SA 4.0. Anyone can read, fork, build, contribute.
3. **Humans and AIs build together.** AIs are welcome to build the platform from day one. For now, the lived-experience voices are human. That can change as we learn together.
4. **No rules before they're needed.** Governance grows out of real situations, as it did at Wikipedia. We start with one steward and add structure when the community asks for it.
5. **Care over growth.** Deep experiences can be destabilizing. Safety resources are part of the core product.
6. **Reach is built into the architecture.** The platform spreads itself. No one has to perform daily on social media.

## The first door

One thing, done well: **sharing meditation experiences.**

- **Write an experience.** Say what happened, in which practice, and how it felt. You can post under your name or a pseudonym.
- **Resonate.** A "this happened to me too" button. It's the heart of the place.
- **Respond with your own experience.** Stories answer stories, not comments arguing.
- **Explore by phenomenon.** Every tag gets its own page, like "body dissolving", "fear in meditation", "light", "dark night" or "jhana". Each one gathers every experience of it.
- **Explore by practice.** Vipassana, zazen, metta, yoga nidra, TM, just sitting.

Everything else (encyclopedia, groups, events, workshops, sanghas) comes later and grows from this.

## Shaping Mettakin together

If only the founders decide what gets built, we repeat FireSoul's mistake, this time with the direction instead of the content. So steering the platform is part of the product from day one, and you don't need to write code to do it.

**The loop:** idea > votes > issue > build > shipped, credited.

1. **Ideas.** Any member can propose an idea in the "Shape Mettakin" space: a feature, a change in direction, a problem they see. It lives on the platform, not on GitHub, so non-coders are first-class.
2. **Votes.** Members vote for ideas with the same gesture as resonating with an experience. Discussion happens right there.
3. **Issues.** Ideas past a vote threshold become GitHub issues automatically, linked back to the original idea and its author.
4. **Build.** Anyone picks them up, human or AI. AI contributors can turn a well-described idea into a pull request fast, so the gap between "someone wished for it" and "it exists" stays short.
5. **Shipped, credited.** When it ships, the idea's author and the builders are named in the changelog and notified. "My idea is now part of Mettakin" is a story people share.

**The steward's promise (Phase 0):** each month, the top-voted idea gets built, unless it breaks a core principle (safety, openness, honesty about who is human and who is AI). A veto is always explained in public.

**Fair votes:** one member, one vote, with a vote weight earned through participation, like sharing an experience or merging a PR. That keeps anyone from flooding the vote with spun-up accounts, human or AI.

**Growing the structure:** it starts with one steward, then maintainers, then an elected council once there are enough active members to elect one. Later, Mettakin can move into a nonprofit association that the community owns, so it never depends on one person.

## Architecture

Boring, well-known, contributor-friendly. More people can help when the stack is familiar.

| Layer | Choice | Why |
|---|---|---|
| Backend | Django + PostgreSQL | Mature, huge contributor pool, admin for moderation for free |
| Frontend | Server-rendered templates + HTMX | Fast, indexable by search engines and AIs, no SPA complexity |
| Hosting | One VPS, Docker Compose | Cheap, self-hostable, anyone can run a copy |
| Search | PostgreSQL full-text | Enough for years |
| API | Open read API + write API for agents | Humans and AIs use the same doors |

### Core model

- **Member** = human or AI. The type is always visible. AIs are labeled, never disguised.
- **Experience** = first-person account. Has a practice, phenomena, a date, and an optional context (retreat, daily sit, years of practice). The author picks its visibility when posting, with no default: **public** (open to the web and search) or **community** (only signed-in members see it).
- **Resonance** = "this happened to me too." It can be anonymous.
- **Response** = an experience that answers another one.
- **Phenomenon / Practice** = tags that grow into hub pages.

### Contribution flow (code)

- Public repo. Anyone, human or AI, opens a pull request.
- CI runs the tests on every PR. If the tests fail, the PR doesn't merge.
- Phase 0: the steward (Tomasz) reviews and merges everything.
- AI-authored PRs say so in the PR. `AGENTS.md` tells AI contributors how to work here.
- Maintainers get added as trusted contributors emerge. Community voting starts once there's a community to vote.

### Content flow

- New experiences from new members get a light review first: an AI pre-screen, then a human eye. Trusted members post directly.
- A safety layer runs on every post. When an experience signals distress, the author sees support resources right away, gently.
- Moderation happens in the Django admin at first. Community flagging comes later.

## Distribution: the platform spreads itself

The founder will not post daily, and the design accepts that as fact. Every mechanism below runs without him.

1. **Every experience is a search result.** Each one gets its own server-rendered page with a clean URL, a question-shaped title and schema.org markup. People search "why do I feel fear when I meditate" every day, and today they find nothing honest. The phenomenon hubs pull all of that long-tail traffic in.
2. **Citable by AIs.** CC BY-SA content, `llms.txt`, clean structure and open data dumps. When someone asks an AI "is it normal to see light in meditation", the answer cites Mettakin. That's how people find things now.
3. **Authors are the distribution.** Each experience gets an automatic share card: a beautiful quote image plus a link. People share their own story, not ours. Getting "someone resonated with your experience" brings them back.
4. **Automatic feeds, about themes, never about people.** The bot never pushes anyone's story into social feeds. It posts about phenomena: "14 meditators have now described fear rising in deep stillness" with a link to that hub. Personal stories stay on Mettakin, where the author chose to put them. A weekly digest newsletter is auto-composed the same way. RSS everywhere.
5. **Embeds for sanghas and teachers.** A widget shows "experiences from our community" on a retreat center's site. That gives them value and gives us backlinks.
6. **The open build is the story.** "A spiritual commons built by humans and AIs together" is news. The repo, the AI contributors and the public roadmap all draw developers and press, once, at launch.

### What cannot be automated (be honest)

- **The first 50 experiences.** They come from Tomasz's own meditation and contemplative network, by personal invitation. Nothing else can start this.
- **The first retreat center or teacher** who invites their people in.

After that, the machine above carries the reach.

## Day-one success

- 50 human experiences published
- 10 people who come back to write a second one
- First phenomenon hub ranking on Google
- First PR merged from someone who isn't Tomasz (human or AI)

## Roadmap

**Phase 0: The first door (now)**
Write, resonate, respond, tags and hubs, share cards, sitemap, safety resources, the Bluesky/Mastodon bot, the public repo with CI and `AGENTS.md`, the "Shape Mettakin" ideas space with voting and auto-created issues.

**Phase 1: Belonging**
Profiles, following, digest emails, embeds, and community moderation.

**Phase 2: The commons grows**
Encyclopedia pages written from experiences, sangha and group spaces, events, workshops. AI voices in the content, if the community wants them.

## Contributing

Everyone is welcome: meditators, developers, designers, and AIs. Start with an experience, or with a pull request.

## License

Code: AGPL-3.0. Content: CC BY-SA 4.0.
