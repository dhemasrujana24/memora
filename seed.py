"""Seeds 30 customers, ~120 tickets, ~360 messages, 60+ memories, 20 KB articles. Run: python seed.py"""
import random, json, datetime as dt
from app.main import db, ex, q, emb, add_memory, hp, init, understand
random.seed(7); init()
with db() as c:
    for t in ("users", "customers", "tickets", "messages", "memories", "kb", "audit"): c.execute(f"delete from {t}")
TOPICS = [("Sync fails on large file uploads", "Increase the sync timeout to 300s", "Clear the local cache"), ("Authentication timeout at login", "Re-authenticate and refresh the token", None), ("Invoice shows duplicate charge", "Refund issued for duplicate charge", None), ("App is slow when opening workspace", "Disable background indexing", "Reinstall the client"), ("Cannot connect Slack integration", "Reconnect the OAuth app", None), ("Sync stalls at 99%", "Increase the sync timeout to 300s", "Clear the local cache"), ("Password reset email not arriving", "Allow-list the sender domain", None), ("Export to CSV crashes the app", "Upgrade to the latest patch", "Restart the client")]
for title, kind in [(t[0], k) for t in TOPICS for k in ("Troubleshooting guide", "FAQ")]:
    ex("insert into kb(title,kind,body,emb) values(?,?,?,?)", (f"{kind}: {title}", kind, f"Steps to diagnose and resolve: {title}. Recommended fix: see resolution history.", json.dumps(emb(title))))
for t in ("Release notes v6.4.2", "Known issue: large-file timeouts in v6.4.2", "Internal: escalation policy", "Product documentation: sync engine"):
    ex("insert into kb(title,kind,body,emb) values(?,?,?,?)", (t, "Known issue" if "Known" in t else "Docs", f"{t}. Large files over 2GB can time out; increasing sync timeout is the workaround.", json.dumps(emb(t))))
ex("insert into users values(?,?,?,?)", ("agent@memora.io", hp("agent123"), "agent", None))
F = "Aarav Priya Rohan Meera Kabir Isha Vikram Neha Arjun Sana Dev Tara Kiran Riya Nikhil Zoya Aditya Lena Omar Diya Sameer Anika Yash Mira Ravi Pooja Ishaan Kavya Tanvi".split(); L = "Sharma Iyer Menon Kapoor Nair Das Bose Patel Reddy Singh".split()
def day(n): return (dt.date(2026, 9, 28) - dt.timedelta(days=n)).isoformat()
def ticket(cid, issue, status, ago, ver, sol=None, fail=None):
    tag, cat, sent, pri = understand(issue)
    tid = ex("insert into tickets(cid,issue,category,tag,priority,status,sentiment,version,created,updated,emb,resolution) values(?,?,?,?,?,?,?,?,?,?,?,?)", (cid, issue, cat, tag, pri, status, sent, ver, day(ago), day(ago), json.dumps(emb(issue)), sol))
    for r, t in (("customer", issue), ("ai", f"Thanks, investigating. Suggested fix: {sol or 'gathering details'}."), ("customer", "That worked, thanks." if status == "Resolved" else "Still checking.")):
        ex("insert into messages(tid,role,text,ts) values(?,?,?,?)", (tid, r, t, day(ago)))
    if status == "Resolved" and sol: add_memory(cid, "resolution_success", f"{sol} resolved: {issue[:50]}", .92, .8, f"TCK-{tid}", day(ago))
    if fail: add_memory(cid, "resolution_fail", f"{fail} did not resolve: {issue[:50]}", .9, .7, f"TCK-{tid}", day(ago))
    return tid
# Ananya Rao: the demo customer
A = "CUS-10482"
ex("insert into customers values(?,?,?,?,?,?,?)", (A, "Ananya Rao", "Enterprise", "CloudSync Pro", "6.4.2", "Windows 11", "2024-03-01"))
ex("insert into users values(?,?,?,?)", ("ananya@example.com", hp("demo123"), "customer", A))
ticket(A, "Authentication timeout at login", "Resolved", 200, "6.3.0", "Re-authentication fixed the login issue")
ticket(A, "Sync fails after upload", "Resolved", 160, "6.4.0", "Increasing the sync timeout", "Clearing the cache")
ticket(A, "Sync fails on large file uploads", "Resolved", 106, "6.4.1", "Increasing the sync timeout solved the large-file issue", "Clearing the cache")
for t in ["Uses CloudSync Pro daily", "Uses Windows 11", "Works in an Enterprise workspace", "Frequently uploads large files", "Uses version 6.4.2"]: add_memory(A, "semantic", t, .95, .6, "TCK-1", day(100))
for t in ["Prefers concise technical explanations", "Prefers step-by-step instructions", "Avoid repeating completed troubleshooting"]: add_memory(A, "preference", t, .9, .7, "TCK-1", day(100))
add_memory(A, "episodic", "Intermittent sync failures remain unresolved", .85, .9, "TCK-3", day(30))
# other customers
for i in range(29):
    cid = f"CUS-{10500+i}"; ver = random.choice(["6.4.2", "6.4.2", "6.4.1", "6.3.0"]); os_ = random.choice(["Windows 11", "macOS 14", "Ubuntu 22.04"])
    ex("insert into customers values(?,?,?,?,?,?,?)", (cid, f"{F[i]} {random.choice(L)}", random.choice(["Enterprise", "Team", "Pro"]), "CloudSync Pro", ver, os_, day(random.randint(200, 900))))
    add_memory(cid, "semantic", f"Uses {os_}", .95, .5, "TCK-0", day(90)); add_memory(cid, "semantic", f"Uses version {ver}", .95, .6, "TCK-0", day(90))
    for _ in range(4):
        t = random.choice(TOPICS[:2] if ver == "6.4.2" and random.random() < .5 else TOPICS)
        ticket(cid, t[0], random.choices(["Resolved", "AI Investigating", "Waiting for Customer", "Escalated"], [70, 12, 8, 10])[0], random.randint(3, 150) if ver != "6.4.2" else random.randint(3, 60), ver, t[1], t[2])
n = lambda t: q(f"select count(*) n from {t}")[0]["n"]
print({t: n(t) for t in ("customers", "tickets", "messages", "memories", "kb")})
