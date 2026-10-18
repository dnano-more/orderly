---
title: Orderly: turning WhatsApp voice notes into priced orders, on the shop's own computer
tags: devchallenge, hf26challenge, ai, opensource
---

*This is a submission for the Hacktoberfest Open-Source AI Challenge: Week 2 (Side Hustle).*
*(Check this top line and the headings against the official submission template before publishing.)*

## The side hustle

[YOUR STORY: who the shop is and what their evening looks like. Real details beat general ones. Example shape: "Every evening, [NAME]'s grocery store gets 30 WhatsApp voice notes: 'bhaiya, do kilo cheeni, ek tel, aur adha kilo chai patti, Patil ke ghar.' He listens to each one, writes it on paper, adds up the prices, and replies by hand."]

**Orderly** takes that voice note and returns a priced order and a ready-to-send WhatsApp reply. Would the shop pay? [FILL IN: what the real user said and what price they named.]

## Demo

[VIDEO LINK or embed, 60 to 90 seconds]

[SCREENSHOT]

## Code

[GITHUB LINK]

## Why open source mattered here

1. **The data belongs to the customers.** Voice notes carry names, home addresses and what a family buys. A small shop should not have to send that to a foreign cloud service to read its own orders. Orderly's speech-to-text (faster-whisper) and its language model (Gemma, via Ollama) both run on the shop's computer.
2. **The cost per order is zero.** A shop that handles 30 orders a day cannot absorb a per-message fee. With open weights, the 10,000th order costs the same as the first.
3. **The language gap is real.** [FILL IN with your honest test: how Whisper and Gemma handled Hindi, Marathi and Hinglish, and what you changed. Open weights let me choose the Whisper size and tune the prompt for this exact kind of message.]

## How it works

```
voice note -> faster-whisper -> Gemma (JSON, temperature 0) -> validator
           -> prices from the shop's own catalogue.json -> invoice + reply
```

The decision I'm most sure about: **the model reads, the code prices.** Gemma extracts items and quantities. It never sees a price. Prices come from the shop's catalogue, so the model cannot invent a total. Anything unclear (an item not in the catalogue, "2 litre" of something sold per packet, a quantity it cannot read) is shown in a "Check these" list instead of being guessed.

If Ollama is not running, a rule-based parser takes over and the page says which one was used.

## Does it work? (real numbers)

[FILL IN FROM `python eval.py`: N real messages, whole orders exactly right: X of N, item precision, item recall. Then ONE honest failure: the message, what the model did, what you did about it. Also: Whisper results on your voice notes, with model size.]

## The first user

[FILL IN: who, what they tried, what confused them, what they said, would they pay and how much.]

## Partner tech

- **Gemma** is the order-reading model, run locally through Ollama. [Add one sentence on what you saw: model size, speed on your machine.]
- [Only if you really use them: .tech domain link, Sentry.]

## What I'd do next

[Short and honest: more languages, a catalogue editor, daily totals, a WhatsApp Business connection.]
