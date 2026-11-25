import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
IDENTITY_PATH = ROOT / ".submission_identity.json"

GENERIC_PATTERNS = {
    "ABS_USER_PATH": re.compile(r"(?:[A-Za-z]:[/\\]{1,2}Users|/Users|/home)[/\\][A-Za-z0-9._-]+", re.I),
    "NIM_DMN_FILENAME": re.compile(r"AI102-HW02-\d+"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS_KEY": re.compile(r"AKIA[0-9A-Z]{16}"),
    "GH_TOKEN": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "GOOGLE_KEY": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    "CREDENTIAL_ASSIGN": re.compile(r"(api[_-]?key|secret|password|passwd|access[_-]?token)\s*[:=]\s*['\"][^'\"]{4,}['\"]", re.I),
    "EMAIL": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
}


def load_local_pii_terms():
    terms = []
    if IDENTITY_PATH.exists():
        data = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
        for a in data.get("authors", []):
            if a.get("name"):
                terms.append(("AUTHOR_NAME", re.compile(re.escape(a["name"]), re.I)))
            if a.get("nim"):
                terms.append(("AUTHOR_NIM", re.compile(re.escape(a["nim"]))))
    return terms


def get_trackable_files():
    res = subprocess.run(
        ["git", "ls-files", "--others", "--cached", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


def main():
    local_pii = load_local_pii_terms()
    trackable = get_trackable_files()
    print(f"Public trackable files (git non-ignored): {len(trackable)}")

    findings = []
    for rel in trackable:
        p = ROOT / rel
        if not p.is_file():
            continue
        if p.suffix.lower() in {".png", ".pdf", ".zip", ".xsd"}:
            if GENERIC_PATTERNS["NIM_DMN_FILENAME"].search(rel):
                findings.append((rel, ["NIM_DMN_FILENAME"]))
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        hits = [k for k, pat in GENERIC_PATTERNS.items() if pat.search(txt)]
        for k, pat in local_pii:
            if pat.search(txt):
                hits.append(k)
        if GENERIC_PATTERNS["NIM_DMN_FILENAME"].search(rel):
            hits.append("NIM_DMN_FILENAME")
        if hits:
            findings.append((rel, sorted(set(hits))))

    print(f"Security/PII findings in public trackable set: {len(findings)}")
    for rel, hits in findings:
        print(f"  {rel} => {hits}")
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
