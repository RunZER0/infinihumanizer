import re
import time
from difflib import SequenceMatcher

import requests

BASE = "https://www.byinfini.online/humanizer/"
ENDPOINT = "https://www.byinfini.online/humanizer/humanize/"

themes = [
    ("urban water governance", "infrastructure reliability", "public legitimacy", "transparent monitoring"),
    ("higher education policy", "student persistence", "institutional accountability", "clear feedback"),
    ("public health systems", "service continuity", "community confidence", "accessible reporting"),
    ("digital government", "administrative efficiency", "procedural fairness", "auditable decisions"),
    ("climate adaptation", "local resilience", "distributional equity", "long-term planning"),
    ("transport planning", "network reliability", "public accessibility", "evidence-based investment"),
    ("housing policy", "affordability", "tenant security", "predictable regulation"),
    ("energy transition", "grid stability", "consumer protection", "transparent pricing"),
    ("food systems", "supply resilience", "producer livelihoods", "traceable standards"),
    ("workplace regulation", "organizational performance", "employee protection", "clear responsibility"),
    ("data governance", "system usefulness", "privacy protection", "documented oversight"),
    ("environmental management", "ecosystem recovery", "community interests", "continuous assessment"),
]

citations = [
    "(Adebayo & Chen, 2024)",
    "(Mwangi, 2023)",
    "(Rivera et al., 2022)",
    "(Okafor & Patel, 2021)",
    "(Nguyen, 2020)",
    "(Kariuki & Mensah, 2024)",
    "(Bennett et al., 2023)",
    "(Santos, 2022)",
]

quotes = [
    '"procedural clarity matters"',
    '"evidence must remain visible"',
    '"implementation changes the policy"',
    '"trust follows demonstrated performance"',
    '"local conditions shape outcomes"',
    '"monitoring is part of the intervention"',
]

templates = [
    "Research on {domain} increasingly treats {a} as a continuing institutional task rather than a one-time technical decision, because implementation conditions change after formal adoption {cite}.",
    "A recurring concern is that policies can appear coherent on paper while producing uneven results when organizations lack the staff, data, or authority required to sustain {a} in practice {cite}.",
    "Scholars therefore examine how {b} is distributed across groups, since an intervention may improve average outcomes while leaving important differences hidden within aggregate measures {cite}.",
    "This distinction matters because formal compliance does not necessarily show whether people experience the system as predictable, understandable, or capable of correcting mistakes when they occur.",
    "In this literature, {c} is often treated as an operational requirement because users cannot evaluate institutional performance if the evidence needed to judge decisions remains inaccessible {cite}.",
    "One synthetic study used the phrase {quote} to describe the point that rules become credible only when routine practice gives people a basis for checking whether those rules are actually followed {cite}.",
    "The same argument also affects evaluation design, since short-term indicators may capture immediate outputs without showing whether the underlying process remains stable when workloads, budgets, or external conditions change.",
    "For that reason, researchers commonly distinguish between the existence of a formal safeguard and the capacity of an institution to make that safeguard work consistently across ordinary and high-pressure situations {cite}.",
    "Attention to {b} also changes how costs are interpreted, because lower expenditure can represent efficiency in one setting but underinvestment in another when essential protections are deferred or shifted elsewhere.",
    "A stronger assessment therefore considers outcomes, implementation quality, and responsibility together, while avoiding the assumption that one favorable indicator can stand in for the performance of the whole system {cite}.",
    "This approach is especially useful in {domain}, where decisions often involve trade-offs that cannot be removed entirely and must instead be made visible, justified, and reviewed as conditions evolve.",
    "The practical question is not simply whether a policy exists, but whether its design gives institutions enough information and authority to respond when observed results diverge from the assumptions built into the original plan {cite}.",
]

sentences = []
i = 0
while len(" ".join(sentences).split()) < 2825:
    domain, a, b, c = themes[i % len(themes)]
    template = templates[i % len(templates)]
    sentence = template.format(
        domain=domain,
        a=a,
        b=b,
        c=c,
        cite=citations[i % len(citations)],
        quote=quotes[i % len(quotes)],
    )
    sentences.append(sentence)
    i += 1

paragraphs = []
for j in range(0, len(sentences), 6):
    paragraphs.append(" ".join(sentences[j:j+6]))

references = """References

Adebayo, T., & Chen, L. (2024). Institutional performance and adaptive governance. Journal of Applied Policy Studies, 18(2), 101-119.
Bennett, R., Okello, P., & Singh, M. (2023). Monitoring public systems under uncertainty. Governance Review, 27(4), 440-458.
Kariuki, J., & Mensah, D. (2024). Equity and accountability in public infrastructure. Policy and Society Quarterly, 16(1), 55-73.
Mwangi, N. (2023). Implementation capacity and institutional trust. African Public Administration Review, 11(3), 201-220.
Nguyen, P. (2020). Evidence, oversight, and public decision making. Administrative Studies, 42(2), 88-107.
Okafor, C., & Patel, R. (2021). Evaluating systems beyond formal compliance. International Policy Journal, 9(4), 310-329.
Rivera, J., Lopez, M., & Hart, S. (2022). Distributional effects in institutional reform. Social Policy Analysis, 31(3), 270-289.
Santos, E. (2022). Transparency and operational resilience. Journal of Governance Practice, 14(2), 130-149."""

source = "\n\n".join(paragraphs) + "\n\n" + references

words = len(source.split())
if words > 3000:
    # Remove whole sentences from the final prose paragraph until the complete test is within the runtime limit.
    while len(source.split()) > 3000 and sentences:
        sentences.pop()
        paragraphs = [" ".join(sentences[j:j+6]) for j in range(0, len(sentences), 6)]
        source = "\n\n".join(paragraphs) + "\n\n" + references
    words = len(source.split())

assert 2850 <= words <= 3000, words

source_quotes = re.findall(r'"[^"\n]+"', source)
source_citations = re.findall(r'\([^()\n]{0,160}(?:19|20)\d{2}[a-z]?[^()\n]{0,80}\)', source)
source_refs = source.split("\n\nReferences\n\n", 1)[1]

session = requests.Session()
page = session.get(BASE, timeout=30)
page.raise_for_status()
csrf = session.cookies.get("csrftoken")
if not csrf:
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page.text)
    csrf = m.group(1) if m else None
if not csrf:
    raise RuntimeError("Could not obtain CSRF token.")

started = time.perf_counter()
response = session.post(
    ENDPOINT,
    data={"text": source, "strength": "8"},
    headers={"X-CSRFToken": csrf, "Referer": BASE},
    timeout=180,
)
elapsed = time.perf_counter() - started

print(f"http_status={response.status_code}")
payload = response.json()
if response.status_code != 200:
    print(payload)
    raise RuntimeError("Long-form production smoke failed.")

output = payload["output_text"]
output_words = len(output.split())
out_quotes = re.findall(r'"[^"\n]+"', output)
out_citations = re.findall(r'\([^()\n]{0,160}(?:19|20)\d{2}[a-z]?[^()\n]{0,80}\)', output)
output_refs = output.split("\n\nReferences\n\n", 1)[1] if "\n\nReferences\n\n" in output else ""

missing_quotes = [q for q in source_quotes if q not in output]
missing_citations = [c for c in source_citations if c not in output]

print("=== LONG ACADEMIC STRENGTH 8 ===")
print("strength=8")
print(f"elapsed_seconds={elapsed:.3f}")
print(f"source_words={words}")
print(f"output_words={output_words}")
print(f"word_delta_pct={(output_words - words) / words * 100:.2f}")
print(f"sequence_similarity={SequenceMatcher(None, source.lower(), output.lower()).ratio():.3f}")
print(f"source_quote_count={len(source_quotes)}")
print(f"output_quote_count={len(out_quotes)}")
print(f"missing_quotes={len(missing_quotes)}")
print(f"source_citation_count={len(source_citations)}")
print(f"output_citation_count={len(out_citations)}")
print(f"missing_citations={len(missing_citations)}")
print(f"references_exact={output_refs == source_refs}")
print(f"em_dash_count={output.count('—')}")
print(f"paragraphs_source={len(source.split(chr(10)+chr(10)))}")
print(f"paragraphs_output={len(output.split(chr(10)+chr(10)))}")
print("OUTPUT_HEAD:")
print(output[:1800])
print("OUTPUT_TAIL:")
print(output[-1800:])

assert not missing_quotes, missing_quotes[:3]
assert not missing_citations, missing_citations[:3]
assert output_refs == source_refs
assert output.count("—") == 0
