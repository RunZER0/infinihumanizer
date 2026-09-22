import re, time, requests
from difflib import SequenceMatcher

BASE="https://www.byinfini.online/humanizer/"
ENDPOINT="https://www.byinfini.online/humanizer/humanize/"

pairs=[
("Urban green space is often discussed as if it were an optional amenity added after the serious work of housing, transport, and public services has been completed.",
 "Urban green space is viewed as an add-on after the serious business of housing, transportation and public services."),
("Parks, tree-lined streets, river corridors, playgrounds, and small planted areas shape how people move, rest, meet, and experience heat, noise, and crowding.",
 "Parks, tree-lined streets, river corridors, playgrounds and small planted areas dictate movement, rest, gathering, and exposure to heat, noise and crowding."),
("Well-planned green space can support physical activity, offer relief from environmental stress, and create informal places of contact among residents who might otherwise remain socially separated.",
 "Good-designed green areas can help to facilitate physical exercise, provide respite from environmental hazards and facilitate informal contact between local people, who would otherwise be socially segregated."),
("The public-health importance of green space becomes clearer when attention shifts from spectacular parks to ordinary routines.",
 "When one examines the impact of green space from the perspective of the public health, it is more apparent when looking at our everyday lives, rather than just spectacular parks."),
("A person who lives near a safe walking route may be more likely to walk to a shop, take a child outside, or spend time outdoors after work.",
 "An individual who resides close to a safe walking path may be more inclined to walk to a shop, take a child outside, or spend time outside after work."),
("An older resident may use a shaded bench as part of a regular route, while adolescents may depend on a local playing field because organized recreation is too expensive.",
 "For older residents, a shaded bench may be part of a regular route, and for adolescents, organized recreation may be too costly, and they may rely upon a local playing field."),
("There is also an environmental dimension.",
 "The environmental aspect is also included."),
("Dense urban districts often retain heat because roads, roofs, and concrete absorb solar energy and release it slowly.",
 "In a dense urban district, roads, roofs and concrete store energy from the sun, and give off heat slowly."),
("Trees and vegetation can reduce exposure to heat by providing shade and supporting evaporative cooling.",
 "Vegetation can protect from the heat by providing shade and/or evaporative cooling."),
("The social value of green space is more difficult to measure, yet it is equally important.",
 "The social benefit of green space is more challenging to quantify but no less significant."),
("Public places allow weak social ties to develop through repeated, low-pressure contact.",
 "Through frequent and low intensity interactions, weak social ties are generated in public places."),
("However, the benefits of green space depend on quality, accessibility, and maintenance.",
 "The advantages of green space will however, only be realized if the green space is of good quality, accessible, and maintained."),
]

def words(s):
    return re.findall(r"[A-Za-z0-9']+", s.lower())
def ngrams(s,n):
    w=words(s); return [tuple(w[i:i+n]) for i in range(len(w)-n+1)]
def retention(src,out,n):
    a=ngrams(src,n); b=set(ngrams(out,n))
    return sum(x in b for x in a)/len(a) if a else 1.0
def sim(a,b):
    return SequenceMatcher(None," ".join(words(a))," ".join(words(b))).ratio()
def first_match(src,out,k):
    return words(src)[:k]==words(out)[:k]

source="\n\n".join(x[0] for x in pairs)
assert len(source.split()) <= 300, len(source.split())

s=requests.Session()
s.headers["User-Agent"]="InfiniAI-GreenSpace-Heldout/1.0"
page=s.get(BASE,timeout=30); page.raise_for_status()
csrf=s.cookies.get("csrftoken")
if not csrf:
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"',page.text)
    csrf=m.group(1) if m else None
if not csrf: raise RuntimeError("No CSRF token")

t=time.perf_counter()
r=s.post(ENDPOINT,data={"text":source,"strength":"8"},headers={"X-CSRFToken":csrf,"Referer":BASE},timeout=120)
elapsed=time.perf_counter()-t
print("HTTP",r.status_code)
payload=r.json()
if r.status_code != 200:
    print(payload); raise RuntimeError("benchmark request failed")
out=payload["output_text"]
outs=[x.strip() for x in out.split("\n\n") if x.strip()]
print("source_words",len(source.split()))
print("elapsed_seconds",round(elapsed,3))
print("sentences_expected",len(pairs),"sentences_output",len(outs))
print("em_dashes",out.count("—"))
if len(outs)!=len(pairs):
    print(out); raise RuntimeError("paragraph/sentence alignment failed")

rows=[]
for i,((src,ref),ours) in enumerate(zip(pairs,outs),1):
    row={
      "ref_src_sim":sim(src,ref),
      "our_src_sim":sim(src,ours),
      "our_ref_sim":sim(ref,ours),
      "ref_len":len(words(ref))/max(1,len(words(src))),
      "our_len":len(words(ours))/max(1,len(words(src))),
      "ref_bi":retention(src,ref,2),
      "our_bi":retention(src,ours,2),
      "ref_tri":retention(src,ref,3),
      "our_tri":retention(src,ours,3),
      "ref_open1":first_match(src,ref,1),
      "our_open1":first_match(src,ours,1),
    }
    rows.append(row)
    print(f"\n[{i}] SOURCE: {src}")
    print(f"[{i}] REF:    {ref}")
    print(f"[{i}] OURS:   {ours}")
    print(f"[{i}] src-sim ref={row['ref_src_sim']:.3f} ours={row['our_src_sim']:.3f} | ours-ref={row['our_ref_sim']:.3f} | len ref={row['ref_len']:.2f} ours={row['our_len']:.2f}")

avg=lambda k: sum(x[k] for x in rows)/len(rows)
print("\n=== GREEN SPACE HELD-OUT SUMMARY ===")
for key in ["ref_src_sim","our_src_sim","our_ref_sim","ref_len","our_len","ref_bi","our_bi","ref_tri","our_tri"]:
    print(key,round(avg(key),3))
print("opening1_change_ref",round(sum(not x["ref_open1"] for x in rows)/len(rows),3))
print("opening1_change_ours",round(sum(not x["our_open1"] for x in rows)/len(rows),3))
print("mean_abs_source_depth_gap",round(sum(abs(x["ref_src_sim"]-x["our_src_sim"]) for x in rows)/len(rows),3))
print("mean_abs_len_gap",round(sum(abs(x["ref_len"]-x["our_len"]) for x in rows)/len(rows),3))
print("over_160pct",sum(x["our_len"]>1.60 for x in rows))
