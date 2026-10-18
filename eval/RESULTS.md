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

- Status: Ollama setup in progress. To be populated once local model inference is evaluated.
