# Quick Reference - Model Settings

## 🔥 Loly (DeepSeek) - Beat Detectors
**Temp**: 0.84 | **Errors**: 8-12% | **Contractions**: 5-8% | **Run-ons**: 10-15% | **Readability**: 70-75%

**Use when**: Need to bypass AI detectors, maximum authenticity required

**Key verbosity words**: "whereby", "insofar as", "with regard to", "in order to adequately and sufficiently"

---

## ⭕ OXO (Claude) - Balanced [DEFAULT]
**Temp**: 0.82 | **Errors**: 7-10% | **Contractions**: 4-6% | **Run-ons**: 8-10% | **Readability**: 75-78%

**Use when**: Need balanced output, general purpose humanization

**Key verbosity words**: "whereby", "insofar as", "with regard to"

---

## ⚡ Smurk (OpenAI) - Best Quality
**Temp**: 0.80 | **Errors**: 7-9% | **Contractions**: 3-5% | **Run-ons**: 6-8% | **Readability**: 78-80%

**Use when**: Quality is priority, professional tone needed, highest readability required

**Key verbosity words**: "whereby", "insofar as", "in order to"

---

## 📝 Common Authentic Patterns (All Models)

### Verbosity Examples:
- "it is within the broader context that one observes"
- "whereby the evidence suggests that"
- "insofar as the data reveals"
- "in order to adequately demonstrate"

### Contractions:
- "it's evident", "doesn't indicate", "can't overlook", "that's clear"

### Run-on Examples:
- "the study examines PEDs and it reveals significant risks whereby the data support this claim"

### Missing Punctuation:
- "However it remains unclear" (missing comma)
- "cardiovascular psychiatric and social" (missing commas)

### Grammatical Errors:
- "the evidence don't follow" (subject-verb)
- "in context of the study" (missing article)
- "this matter, they associate" (comma splice)

---

## 🎯 Server Info
**URL**: http://127.0.0.1:8000/  
**Status**: ✅ Running  
**Default Model**: OXO (Claude)

---

## 🔧 Quick Adjustments

To edit models: `humanizer/engine_config.py`

**Temperature** (increase for more variation):
- `base_temperature`: Main setting
- `temperature_variation`: Dynamic range

**Error Rates** (increase percentages in prompts):
- Look for "8-12%", "7-10%", etc.
- Adjust as needed

**Verbosity** (add/remove keywords):
- "whereby", "insofar as", "with regard to"
- Add more in system prompts

**Readability** (adjust quality floor):
- Loly: 70-75%
- OXO: 75-78%
- Smurk: 78-80%
