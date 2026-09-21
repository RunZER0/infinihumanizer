import re, time, requests
from difflib import SequenceMatcher

BASE="https://www.byinfini.online/humanizer/"
ENDPOINT="https://www.byinfini.online/humanizer/humanize/"

pairs=[
("Urban green space is often discussed as if it were an optional amenity added after the serious work of housing, transport, and public services has been completed.",
 "Urban green space is treated as if it were an afterthought to the 'real' development of a city, namely its housing and transport, and public services."),
("Parks, tree-lined streets, river corridors, playgrounds, and small planted areas shape how people move, rest, meet, and experience heat, noise, and crowding.",
 "Parks, tree-lined streets, river corridors, playgrounds and small planted areas influence the movement, rest, meeting and feeling of heat, noise and crowding."),
("The public-health importance of green space becomes clearer when attention shifts from spectacular parks to ordinary routines.",
 "It is only when people look at green space from a different perspective and start thinking about their daily lives that the public-health significance of green space becomes more evident."),
("There is also an environmental dimension.",
 "An environmental dimension as well."),
("The social value of green space is more difficult to measure, yet it is equally important.",
 "Social value of green space is more challenging to measure, but it is also significant."),
("Judicial independence is commonly defended as a condition of the rule of law because courts must be able to decide cases without improper pressure from government, private interests, or popular anger.",
 "Judicial independence is a generally accepted principle of the rule of law, as it is essential for the courts to be able to adjudicate cases without undue influence from the government, private entities or public sentiment."),
("Accountability begins with reasons.",
 "The first step to accountability is to give reasons."),
("Remote work changes more than the location from which employees complete tasks.",
 "Working remotely is more than a shift in location of where workers perform their duties."),
("The clearest advantage of remote work is flexibility.",
 "Flexibility is the greatest benefit of telecommuting."),
("In-person supervision sometimes allows managers to confuse visibility with productivity.",
 'Sometimes managers equate "visibility" with "productivity" in the case of in-person supervision.'),
]

def words(s):
    return re.findall(r"[A-Za-z0-9']+", s.lower())

def ngrams(s,n):
    w=words(s)
    return [tuple(w[i:i+n]) for i in range(len(w)-n+1)]

def retention(src,out,n):
    a=ngrams(src,n); b=set(ngrams(out,n))
    return (sum(x in b for x in a)/len(a)) if a else 1.0

def sim(a,b):
    return SequenceMatcher(None," ".join(words(a))," ".join(words(b))).ratio()

def first_match(src,out,k):
    return words(src)[:k] == words(out)[:k]

source="\n\n".join(x[0] for x in pairs)
assert len(source.split()) <= 300, len(source.split())

s=requests.Session()
s.headers["User-Agent"]="InfiniAI-Reference-Benchmark/1.0"
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
if r.status_code!=200:
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
      "i":i,
      "ref_sim":sim(src,ref),
      "our_sim":sim(src,ours),
      "ref_len":len(words(ref))/max(1,len(words(src))),
      "our_len":len(words(ours))/max(1,len(words(src))),
      "ref_bi":retention(src,ref,2),
      "our_bi":retention(src,ours,2),
      "ref_tri":retention(src,ref,3),
      "our_tri":retention(src,ours,3),
      "ref_open1":first_match(src,ref,1),
      "our_open1":first_match(src,ours,1),
      "ref_open2":first_match(src,ref,2),
      "our_open2":first_match(src,ours,2),
    }
    rows.append(row)
    print(f"\n[{i}] SOURCE: {src}")
    print(f"[{i}] REF:    {ref}")
    print(f"[{i}] OURS:   {ours}")
    print(f"[{i}] depth ref={row['ref_sim']:.3f} ours={row['our_sim']:.3f} | len ref={row['ref_len']:.2f} ours={row['our_len']:.2f} | bi ref={row['ref_bi']:.2f} ours={row['our_bi']:.2f} | tri ref={row['ref_tri']:.2f} ours={row['our_tri']:.2f}")

avg=lambda key: sum(r[key] for r in rows)/len(rows)
print("\n=== PAIRED SUMMARY ===")
for key in ["ref_sim","our_sim","ref_len","our_len","ref_bi","our_bi","ref_tri","our_tri"]:
    print(key,round(avg(key),3))
print("opening1_change_ref",round(sum(not r["ref_open1"] for r in rows)/len(rows),3))
print("opening1_change_ours",round(sum(not r["our_open1"] for r in rows)/len(rows),3))
print("opening2_change_ref",round(sum(not r["ref_open2"] for r in rows)/len(rows),3))
print("opening2_change_ours",round(sum(not r["our_open2"] for r in rows)/len(rows),3))
print("mean_abs_depth_gap",round(sum(abs(r["ref_sim"]-r["our_sim"]) for r in rows)/len(rows),3))
print("mean_abs_len_ratio_gap",round(sum(abs(r["ref_len"]-r["our_len"]) for r in rows)/len(rows),3))
print("opening_direction_agreement",round(sum((r["ref_open1"]==r["our_open1"]) for r in rows)/len(rows),3))
