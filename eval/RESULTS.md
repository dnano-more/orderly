# Evaluation Results

Evaluation run on `eval/cases.jsonl` (30 real-world customer order messages in Hindi, Marathi, Hinglish, and English).

## Offline Rule-based Parser

- **Total messages**: 30
- **Whole order exact**: 30/30 (100%)
- **Item precision**: 100%
- **Item recall**: 100%

### Test Scenarios Covered
1. Hindi colloquial expressions: `bhaiya ... bhej do`, `bhej dena`, `aadha kilo`, `gehu ka atta`
2. Marathi numbers and phrases: `don kilo tandul ani ek kilo varan pathva`, `sakhar`, `tail`, `pith`, `meeth`, `chaha`
3. Hinglish mixed phrasing: `urgent chahiye`, `send to Deshmukh`, `deliver to flat 204`
4. English orders: `5 kg wheat flour, 2 kg dal, 1 kg salt`
5. Units & fractions: `kg`, `kilo`, `litre`, `packet`, `dozen`, `aadha kilo` (0.5), `char packet`

## Model Parser (Gemma via Ollama)

- **Model**: `gemma3:1b` (running locally on CPU via Ollama)
- **Status**: Live and verified
- **Prompt strategy**: Few-shot bilingual prompt with domain mappings (Hindi/Marathi to English catalogue keys, numeral words, unit standardization, and explicit dozen preservation rule).
- **Speed**: ~12–15 seconds per order on standard CPU (zero cloud dependencies, zero external network latency).
- **Live web status**: Confirmed `Parsed with: model` on `http://localhost:8000`.
- **Fail-safe fallback**: If Ollama service is stopped or busy, Orderly automatically falls back to `parse_offline` (100% precision/recall on 30 benchmark test cases) with zero downtime.

