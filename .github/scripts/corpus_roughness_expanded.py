import re, time, requests
from difflib import SequenceMatcher

BASE="https://www.byinfini.online/humanizer/"
ENDPOINT="https://www.byinfini.online/humanizer/humanize/"

pairs=[
("That view understates its role in the daily functioning of a city.","It's a minimalistic perspective on its role in the life of a city."),
("Well-planned green space can support physical activity, offer relief from environmental stress, and create informal places of contact among residents who might otherwise remain socially separated.","Designed green space can promote physical activity, provide respite from environmental stressors, and provide informal contact opportunities among members of the community who may otherwise be socially separated."),
("A person who lives near a safe walking route may be more likely to walk to a shop, take a child outside, or spend time outdoors after work.","A person who resides adjacent to a safe walking route is more likely to walk to a store, take a child outside to play and spend time outside after work."),
("Public health is shaped by repeated habits, and the physical environment can either make those habits easier or place small obstacles in their way.","Repeated habits help to create public health, and the physical environment either facilitates or presents minor barriers to such habits."),
("Dense urban districts often retain heat because roads, roofs, and concrete absorb solar energy and release it slowly.","Rough surfaces like roads, roofing, and concrete can be solar absorbers and lose heat slowly, causing dense urban districts to hold onto heat."),
("The effect is not uniform, and planting a few trees cannot solve an urban heat problem created by poor housing and limited infrastructure.","The impact is not consistent and the isolated planting of a few trees is not a solution to an urban heat issue caused by inadequate housing and infrastructure."),
("Neighbours may recognize one another without becoming close friends; parents may speak while children play; street vendors and regular walkers may become familiar figures.","People may not be friends, but they can recognize each other; parents may talk while children are playing; street vendors and frequent strollers may be familiar faces."),
("The point is not constant surveillance, but the social presence created by ordinary activity.","The point is not one that is constantly monitored, but rather a social point that is generated through common action."),
("Judicial independence is commonly defended as a condition of the rule of law because courts must be able to decide cases without improper pressure from government, private interests, or popular anger.","Judicial independence is a generally accepted principle of the rule of law, as it is essential for the courts to be able to adjudicate cases without undue influence from the government, private entities or public sentiment."),
("Courts exercise public power, interpret legal rules, and sometimes determine disputes with major social and economic consequences.","Courts have public powers of interpretation of the law and in some cases resolve social and economic issues of great importance."),
("These arrangements do not guarantee good judging, but they help create an institutional environment in which legal reasoning can take priority over personal survival.","These do not ensure good judging, but do help to establish an atmosphere that can become institutionalized so that legal reasoning can be paramount over survival."),
("Independence is particularly important in disputes involving the state, where one party may possess resources and authority far beyond those of an individual claimant.","Independence is especially significant when the claim is against the state, as the party against whom the claim is made may have resources and power that are much greater than those that the claimant has."),
("Courts usually justify decisions through written or oral judgments that identify the issues, explain the relevant law, and show how conclusions were reached.","Courts typically provide explained (printed or spoken) decisions that state the issues, discuss the law involved, and demonstrate the process of reaching a decision."),
]

def words(s): return re.findall(r"[A-Za-z0-9']+", s.lower())
def sim(a,b): return SequenceMatcher(None," ".join(words(a))," ".join(words(b))).ratio()
def grams(s,n):
    w=words(s); return [tuple(w[i:i+n]) for i in range(len(w)-n+1)]
def retain(src,out,n):
    a=grams(src,n); b=set(grams(out,n))
    return sum(x in b for x in a)/len(a) if a else 1.0
def first(src,out,k): return words(src)[:k]==words(out)[:k]

source="\n\n".join(s for s,_ in pairs)
print("source_words",len(source.split()))
assert len(source.split()) <= 300

s=requests.Session(); s.headers["User-Agent"]="InfiniAI-Corpus-Roughness-Benchmark/1.0"
page=s.get(BASE,timeout=30); page.raise_for_status()
csrf=s.cookies.get("csrftoken")
if not csrf:
    m=re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"',page.text)
    csrf=m.group(1) if m else None
if not csrf: raise RuntimeError("No CSRF token")

t=time.perf_counter()
r=s.post(ENDPOINT,data={"text":source,"strength":"8"},headers={"X-CSRFToken":csrf,"Referer":BASE},timeout=180)
print("HTTP",r.status_code,"elapsed",round(time.perf_counter()-t,3))
payload=r.json()
if r.status_code!=200:
    print(payload); raise RuntimeError("benchmark failed")
out=payload["output_text"]
outs=[x.strip() for x in out.split("\n\n") if x.strip()]
print("sentences",len(outs),"expected",len(pairs),"em_dashes",out.count("—"))
if len(outs)!=len(pairs):
    print(out); raise RuntimeError("alignment failed")

rows=[]
for i,((src,ref),ours) in enumerate(zip(pairs,outs),1):
    row=dict(ref_sim=sim(src,ref),our_sim=sim(src,ours),
             ref_len=len(words(ref))/max(1,len(words(src))),our_len=len(words(ours))/max(1,len(words(src))),
             ref_bi=retain(src,ref,2),our_bi=retain(src,ours,2),
             ref_tri=retain(src,ref,3),our_tri=retain(src,ours,3),
             ref_open=first(src,ref,1),our_open=first(src,ours,1))
    rows.append(row)
    print(f"\n[{i}] SOURCE: {src}\n[{i}] REF: {ref}\n[{i}] OURS: {ours}")
    print(f"[{i}] sim ref={row['ref_sim']:.3f} ours={row['our_sim']:.3f} len ref={row['ref_len']:.2f} ours={row['our_len']:.2f} bi ref={row['ref_bi']:.2f} ours={row['our_bi']:.2f} tri ref={row['ref_tri']:.2f} ours={row['our_tri']:.2f}")

avg=lambda k: sum(x[k] for x in rows)/len(rows)
print("\n=== EXPANDED CORPUS SUMMARY ===")
for k in ["ref_sim","our_sim","ref_len","our_len","ref_bi","our_bi","ref_tri","our_tri"]:
    print(k,round(avg(k),3))
print("open_change_ref",round(sum(not x["ref_open"] for x in rows)/len(rows),3))
print("open_change_ours",round(sum(not x["our_open"] for x in rows)/len(rows),3))
print("mean_abs_depth_gap",round(sum(abs(x["ref_sim"]-x["our_sim"]) for x in rows)/len(rows),3))
print("mean_abs_len_gap",round(sum(abs(x["ref_len"]-x["our_len"]) for x in rows)/len(rows),3))
