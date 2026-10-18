# Orderly: plan to submit (Sun Oct 18, 07:45 IST to Mon Oct 19, 12:29 PM IST)

**Goal:** one strong, honest entry. Rules: **one entry only, the first one submitted is judged**, so publish once, final. Required: DEV post using the template, tag `#hf26challenge`, a **video demo or deployed link**, a **repo link**, an explanation of **why open innovation matters**, and the prize category named in the post. Project must be brand new from Oct 12.

**Prize focus (max one prize per person):** Overall ($250) and Best Use of Gemma ($200) via local Gemma. Claim the .tech domain ($100) if you have time. Only claim a category you really use.

**Judging:** writing quality counts most. Ties go to the post with more reactions, so share the link in the MLH Discord and with friends right after posting.

## Schedule (IST). Commit after every block.

| Time | Task | Done when |
|---|---|---|
| 08:00 to 09:00 | Push this folder to a public GitHub repo. Install Ollama, `ollama pull gemma3:4b`, `pip install faster-whisper pytest`. Run `python orderly.py`, open localhost:8000, type an order. | Typed order gives an invoice using real Gemma (page says "Parsed with: model") |
| 09:00 to 10:30 | **Voice reality check.** Record 10 voice notes in Hindi, Marathi and Hinglish. Check Whisper `small` vs `medium` (`transcribe(audio, "medium")`). Note how many come out usable. | You know honestly whether voice works. If it is poor, keep typed or pasted text as the main flow and say so in the post. Do not hide it |
| 10:30 to 12:30 | Build `eval/cases.jsonl` with **30 real messages** (write them the way customers really write; ask 2 or 3 people for theirs). Run `python eval.py`. Fix the prompt in `orderly.py` using the misses (add 2 or 3 examples to `PROMPT`). | Before and after accuracy saved in `eval/RESULTS.md` |
| 12:30 to 14:00 | **First user.** Find a real shop, tiffin service or tailor. Edit `catalogue.json` with their items and prices. Have them send you 5 real voice notes. Watch what breaks. | Notes in `notes/first-user.md`: what confused them, what they said, would they pay |
| 14:00 to 16:00 | Fix the top 2 problems only. Optional: add the .tech domain, Sentry. | Tests pass |
| 16:00 to 17:30 | **Record the demo video (60 to 90 s):** voice note, transcript, priced order, WhatsApp reply. Upload it (YouTube unlisted or DEV embed). Take 2 screenshots. | Video link works in a private window |
| 17:30 to 20:00 | Fill every `[BRACKET]` in `devpost.md` with real numbers and the real user story. Read it aloud once. Compare headings with the DEV submission template. | No brackets left |
| 20:00 to 21:00 | Fresh clone into a new folder, follow the README exactly, run tests. | Works from scratch |
| 21:00 to 22:00 | **Publish once.** Check links, video, tags. Share the link. | Live |
| Mon until 12:29 PM | Buffer only. Fix typos if editing is allowed. Do not start anything new. | |

## If something breaks
- Whisper bad on your languages: lead with typed Hinglish and say honestly that voice is limited.
- Gemma slow: use `gemma3:1b` or `gemma3:4b`; report the real speed.
- No shopkeeper available by 14:00: be the first user yourself with a family or neighbour's real orders, and say that plainly.

## Antigravity prompt template
```
Read PLAN.md and orderly.py. Do only this task: <task>. Keep to the standard
library. Update tests, run pytest, show me the output. Do not change anything
else. Give me a one-line commit message.
```
