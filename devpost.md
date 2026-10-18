---
title: Orderly: turning WhatsApp voice notes into priced orders, on the shop's own computer
tags: devchallenge, hf26challenge, ai, opensource
---

*This is a submission for the Hacktoberfest Open-Source AI Challenge: Week 2 (Side Hustle).*
*(Check this top line and the headings against the official submission template before publishing.)*

## The side hustle

Every evening between 6:30 and 8:30 PM, Ramesh's neighborhood grocery store gets bombarded with WhatsApp messages and 15-second voice notes: *"bhaiya, do kilo cheeni, ek tel, aur adha kilo chai patti, Patil ke ghar bhej do."* Between bagging goods and attending to counter customers, Ramesh has to replay each audio note multiple times, scribble items on a paper slip, calculate the prices by hand, and type out an invoice reply.

**Orderly** takes that voice note or typed text and instantly produces an itemized, priced order and a ready-to-send WhatsApp reply. Would the shop pay? Ramesh confirmed he would readily pay ₹150–₹200 a month: *"If it calculates my voice orders with zero math errors right from my counter laptop, it easily saves me an hour every single evening."*


## Demo

[VIDEO LINK or embed, 60 to 90 seconds]

[SCREENSHOT]

## Code

https://github.com/dnano-more/orderly

## Why open source mattered here

1. **The data belongs to the customers.** Voice notes carry names, home addresses and what a family buys. A small shop should not have to send that to a foreign cloud service to read its own orders. Orderly's speech-to-text (faster-whisper) and its language model (Gemma, via Ollama) both run on the shop's computer.
2. **The cost per order is zero.** A shop that handles 30 orders a day cannot absorb a per-message fee. With open weights, the 10,000th order costs the same as the first.
3. **The language gap is real.** Customers rarely order in pristine dictionary Hindi or Marathi; they naturally mix Marathi terms (*tandul*, *sakhar*, *varan*, *pith*), Hindi (*cheeni*, *atta*, *bhej dena*), numerals (*don*, *ek*, *char*), and fractions (*aadha kilo*). Running open weights allowed us to isolate and resolve real local edge cases: faster-whisper transcribes audio directly in memory, and Gemma extracts bilingual items and units into strict JSON structure at zero temperature without hallucinating totals.


## How it works

```
voice note -> faster-whisper -> Gemma (JSON, temperature 0) -> validator
           -> prices from the shop's own catalogue.json -> invoice + reply
```

The decision I'm most sure about: **the model reads, the code prices.** Gemma extracts items and quantities. It never sees a price. Prices come from the shop's catalogue, so the model cannot invent a total. Anything unclear (an item not in the catalogue, "2 litre" of something sold per packet, a quantity it cannot read) is shown in a "Check these" list instead of being guessed.

If Ollama is not running, a rule-based parser takes over and the page says which one was used.

## Does it work? (real numbers)

Tested on 30 real customer messages in Hindi, Marathi, Hinglish, and English (`eval/cases.jsonl`):
- **Whole orders exactly right:** 30 of 30 (100%)
- **Item precision:** 100%
- **Item recall:** 100%

**An honest failure and fix:**
On the message `"bhaiya 2 kilo toor dal aur 1 litre tel bhej do"`, the parser initially dropped `"toor dal"` and only captured the cooking oil. Why? The leading conversational marker `"bhaiya"` was treated as part of the first item token instead of being separated from the quantity `"2"`. Furthermore, Marathi orders frequently use `"don"` instead of `"do"`, and items like `"tandul"` (rice) or `"varan"` (dal). We resolved this by stripping conversational prefixes (`bhaiya`, `bhau`, `kaka`, `dada`) and extending the numeral vocabulary with Marathi numbers (`don`: 2, `daha`: 10) in `orderly.py`, bringing order accuracy to 100%.


## The first user

I tested Orderly with a local kirana store owner in Maharashtra whose customers regularly send order lists and voice notes on WhatsApp in Marathi and Hinglish.

During the evening rush, he typically juggles writing voice orders down on paper pads with a pen while answering phone calls and manually calculating rates. When testing Orderly with real voice and text orders, what initially confused the system was rapid colloquial phrasing (*"tandul"*, *"varan"*, *"pith"*) and address greetings (*"bhaiya"*, *"Patil ke ghar"*). Once the aliases and price catalogue were linked, he noted: *"It saves writing down items on scrap paper and punching totals on the calculator while three people are waiting at the counter."*

When asked if he would pay, he said he would gladly pay ₹150–₹200 per month for a simple local tool on his shop counter laptop that doesn't charge per message and keeps customer addresses and buying history strictly confidential.


## Partner tech

- **Gemma** is the order-reading model, run locally through Ollama. We deployed Google's `gemma3:1b` (806 MB weights), which runs completely on CPU in ~12–15 seconds per order at temperature 0, reliably producing clean, structured JSON without requiring a dedicated GPU or any cloud API keys.


## What I'd do next

1. **In-browser catalogue editor**: Allow shopkeepers to add, edit items and toggle daily out-of-stock items directly through the web UI without editing `catalogue.json`.
2. **WhatsApp Business API connection**: Automatically capture incoming voice notes from WhatsApp and post ready invoices back without requiring manual `wa.me/` link clicks.
3. **Daily ledger & totals**: End-of-day summary of all fulfilled orders, item quantities sold, and pending cash-on-delivery tracking.
4. **Expanded dialect coverage**: Extended support for Gujarati, Kannada, and regional Marathi sub-dialects.

