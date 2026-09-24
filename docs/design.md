# Design

Leanings, not decisions yet.

- **An app, not an article.** Hacker News density, btop boxes, TradingView side panels. Lists of stories you scan, boxes with a small label on top, buttons with icons. The palette stays warm (amber, sepia), because people write intimate things here.
- **Three voices of type.** A plain sans (Verdana) for the interface and titles. Monospace for small data: names, times, counts, box labels. A serif only for reading and writing stories.
- **Read first, write second.** A visitor sees stories before being asked for one, and can start writing before making an account.
- **One main action per page.** One filled button. Everything else is outlined or quiet.
- **Pixel icons, small motion.** Icons are pixel art drawn from ASCII in [design/icons.py](../design/icons.py). Motion lives only on icons (the breathing lotus, the me-too heart) and switches off for people who ask for less motion.
- **Media is small on purpose.** Images are dithered to a few colors and a few kilobytes, the way [Low-tech Magazine](https://solar.lowtechmagazine.com) does it. That keeps pages fast, storage cheap and faces harder to recognize.
- **No video at the start.** Video costs a lot to store, is hard to moderate and exposes people. We'll revisit it if members ask.
