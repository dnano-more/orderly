# First User Field Notes

**Date:** October 18, 2026  
**User:** Kirana shopkeeper (Local grocery / general store)  
**Location:** Maharashtra, India  
**Language context:** Hindi, Marathi, and Hinglish mixed audio notes

---

## 1. Setup & Orders Tested
Catalogue customized with real local prices:
- Sugar (Sakhar / Cheeni): ₹45/kg
- Cooking Oil (Tel / Tail): ₹150/L
- Rice (Tandul / Chawal): ₹60/kg
- Atta (Gehu / Pith): ₹40/kg
- Milk (Dudh): ₹28/pkt
- Tea (Chaha / Chai Patti): ₹90/pkt
- Toor Dal (Varan / Dal): ₹130/kg
- Salt (Meeth / Namak): ₹22/kg
- Eggs (Ande): ₹84/dozen

### Sample Real Customer Messages Tested:
1. *"Bhaiya, do kilo cheeni, ek litre tel, Patil ke ghar bhej do"*
2. *"Don kilo tandul ani ek kilo varan pathva, urgent"*
3. *"Aadha kilo sakhar, ek packet chaha ani don packet dudh"*
4. *"5 kg atta, 2 kg dal, 1 kg meeth"*
5. *"Ek dozen ande ani char packet doodh"*

---

## 2. What Broke / What Was Confusing
- **Initial Observation:** Fast spoken speech with ambient street noise (horns, fan) occasionally caused Whisper segment boundary splits.
- **Quantity Confusion:** Colloquial fractions (like *"aadha kilo"*, *"don kilo"*) need explicit mapping to decimal floats (`0.5`, `2.0`). Handled in rule parser and prompt examples.
- **Brand vs Category:** Customers sometimes say *"Fortune tel"* or *"Tata namak"* instead of generic names. Aliases in `catalogue.json` ensure fuzzy substring matching catches the right inventory item without hallucinating new items.

---

## 3. Shopkeeper Feedback
- **What they said:**
  - *"It saves me writing down items on scrap paper during peak 7 PM rush."*
  - *"WhatsApp reply button is very handy—I don't have to calculate totals on a calculator while answering calls."*
- **Would they pay?**
  - Yes, willing to pay ₹100–₹200 / month if it runs reliably on their existing counter laptop or phone without monthly per-message fees.
  - Valued privacy: appreciate that customer address and purchase history never leave their own laptop.
