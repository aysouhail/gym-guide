#!/usr/bin/env python3
"""Génère programme.html : page unique à onglets, construite depuis les fichiers Markdown.

Les fichiers .md restent la source de vérité. Après toute modification du programme,
relancer :  python3 outils/build-html.py
"""

import html
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "programme.html"

# --------------------------------------------------------------------------
# Onglets
# --------------------------------------------------------------------------

SEANCES = [
    ("s1", "Séance 1", "Pecs · Triceps · Épaules",
     "programme/seance-1-pecs-triceps-epaules.md", "guide-machines/pecs-triceps-epaules.md"),
    ("s2", "Séance 2", "Dos · Biceps",
     "programme/seance-2-dos-biceps.md", "guide-machines/dos-biceps.md"),
    ("s3", "Séance 3", "Jambes",
     "programme/seance-3-jambes.md", "guide-machines/jambes.md"),
    ("s4", "Séance 4", "Complémentaire",
     "programme/seance-4-complementaire.md", "guide-machines/complementaire.md"),
]

SIMPLES = [
    ("echauffement", "Échauffement", "Avant chaque séance", "programme/echauffement.md"),
    ("abdos", "Abdos", "4 blocs, un par séance", "programme/abdos.md"),
    ("prises", "Prises & réglages", "À lire en premier", "guide-machines/00-prises-et-vocabulaire.md"),
    ("progression", "Progression", "Quand augmenter les charges", ".cursor/skills/coach-musculation/progression.md"),
    ("nutrition", "Nutrition & cardio", "Recomposition", "programme/nutrition-et-cardio.md"),
]

TAB_FOR_MD = {src: tab for tab, _, _, src, _ in SEANCES}
TAB_FOR_MD.update({src: tab for tab, _, _, src in SIMPLES})

TAB_LABELS = {tab: f"{label} — {sub}" for tab, label, sub, _, _ in SEANCES}
TAB_LABELS.update({tab: label for tab, label, _, _ in SIMPLES})

# Renseigné pendant la construction : (fichier md, ancre GitHub) -> id de la fiche HTML
FICHE_IDS: dict[tuple[str, str], str] = {}

# --------------------------------------------------------------------------
# Slugs
# --------------------------------------------------------------------------


def gh_slug(text: str) -> str:
    """Reproduit l'ancre générée par GitHub pour un titre Markdown."""
    text = re.sub(r"[`*_]", "", text).strip().lower()
    keep = [c for c in text if c.isalnum() or c in " -_" or unicodedata.category(c)[0] == "L"]
    return "".join(keep).replace(" ", "-")


def ascii_slug(text: str) -> str:
    """Slug ASCII, pour les id HTML."""
    text = re.sub(r"[`*_]", "", text).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# --------------------------------------------------------------------------
# Réécriture des liens Markdown -> liens internes à la page
# --------------------------------------------------------------------------


def rewrite_link(url: str, source: str) -> str | None:
    """Renvoie l'URL à utiliser dans la page, ou None si le lien doit disparaître."""
    if url.startswith(("http://", "https://", "mailto:")):
        return url

    path_part, _, anchor = url.partition("#")
    if not path_part:
        return "#" + ascii_slug(anchor) if anchor else None

    target = str((Path(source).parent / path_part).as_posix())
    target = str(Path(target).resolve().relative_to(ROOT).as_posix()) \
        if (ROOT / target).exists() else target

    fiche = FICHE_IDS.get((target, anchor))
    if fiche:
        return "#" + fiche

    tab = TAB_FOR_MD.get(target)
    if tab:
        return "#" + tab

    # journal/, profil.md, README… : pas de place dans la page, on retire le lien
    return None


# --------------------------------------------------------------------------
# Mini convertisseur Markdown
# --------------------------------------------------------------------------

CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def inline(text: str, source: str) -> str:
    out = html.escape(text, quote=False)
    placeholders: list[str] = []

    def stash(markup: str) -> str:
        placeholders.append(markup)
        return f"\x00{len(placeholders) - 1}\x00"

    out = CODE_RE.sub(lambda m: stash(f"<code>{m.group(1)}</code>"), out)

    def do_link(m: re.Match) -> str:
        label, url = m.group(1), html.unescape(m.group(2))
        new = rewrite_link(url, source)
        if new is None:
            return stash(f'<span class="ref">{label}</span>')
        ext = ' target="_blank" rel="noopener"' if new.startswith("http") else ""
        cls = "lien-ext" if ext else "lien-int"
        if label.strip() == "→":
            label = "Fiche"
        elif label.strip().endswith(".md") and new.startswith("#"):
            # « nutrition-et-cardio.md » n'a pas de sens dans une page web
            onglet = TAB_LABELS.get(new[1:])
            label = "l'onglet " + html.escape(onglet, quote=False) if onglet else label
        return stash(f'<a class="{cls}" href="{html.escape(new, quote=True)}"{ext}>{label}</a>')

    out = LINK_RE.sub(do_link, out)
    out = BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = ITALIC_RE.sub(r"<em>\1</em>", out)
    out = re.sub(r"\\\|", "|", out)
    for i, markup in enumerate(placeholders):
        out = out.replace(f"\x00{i}\x00", markup)
    return out


def split_row(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip())
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return [c.strip() for c in cells]


def convert(md: str, source: str, base_level: int = 2) -> str:
    """Markdown -> HTML. base_level décale les niveaux de titres."""
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    para: list[str] = []

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para), source)}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        # Titre
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = min(len(m.group(1)) + base_level - 1, 6)
            title = m.group(2)
            out.append(f'<h{level} id="{ascii_slug(title)}">{inline(title, source)}</h{level}>')
            i += 1
            continue

        # Filet horizontal
        if re.fullmatch(r"-{3,}", stripped):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        # Citation
        if stripped.startswith(">"):
            flush_para()
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            out.append(f'<blockquote>{inline(" ".join(buf), source)}</blockquote>')
            continue

        # Tableau
        if stripped.startswith("|") and i + 1 < len(lines) \
                and re.fullmatch(r"\|[\s:\-|]+\|", lines[i + 1].strip()):
            flush_para()
            header = split_row(lines[i])
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(split_row(lines[i]))
                i += 1
            klass = "tbl"
            if header and header[0].lower().startswith("erreur"):
                klass += " tbl-erreurs"
            thead = "".join(f"<th>{inline(c, source)}</th>" for c in header)
            rows = []
            for cells in body:
                cells += [""] * (len(header) - len(cells))
                tds = "".join(f"<td>{inline(c, source)}</td>" for c in cells[:len(header)])
                rows.append(f"<tr>{tds}</tr>")
            out.append(
                f'<div class="tbl-wrap"><table class="{klass}">'
                f"<thead><tr>{thead}</tr></thead><tbody>{''.join(rows)}</tbody>"
                "</table></div>"
            )
            continue

        # Liste
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m or stripped.startswith("- "):
            flush_para()
            ordered = bool(m)
            items = []
            while i < len(lines):
                s = lines[i].strip()
                mm = re.match(r"^\d+\.\s+(.*)$", s)
                if ordered and mm:
                    items.append(mm.group(1))
                elif not ordered and s.startswith("- "):
                    items.append(s[2:])
                elif s and not s.startswith(("|", "#", ">")) and items \
                        and lines[i].startswith(("  ", "\t")):
                    items[-1] += " " + s
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            lis = "".join(f"<li>{inline(it, source)}</li>" for it in items)
            out.append(f"<{tag}>{lis}</{tag}>")
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return "\n".join(out)


# --------------------------------------------------------------------------
# Découpage des fiches techniques
# --------------------------------------------------------------------------


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def parse_fiches(rel: str) -> list[dict]:
    """Découpe un fichier guide-machines en fiches (une par titre de niveau 2)."""
    md = read(rel)
    parts = re.split(r"^## (.+)$", md, flags=re.M)
    fiches = []
    for title, body in zip(parts[1::2], parts[2::2]):
        fid = "f-" + ascii_slug(title)
        FICHE_IDS[(rel, gh_slug(title))] = fid
        fiches.append({"id": fid, "title": title, "body": body, "source": rel})
    return fiches


def register_all_anchors() -> None:
    """Pré-enregistre les ancres pour que les liens des séances soient résolus."""
    for _, _, _, _, guide in SEANCES:
        parse_fiches(guide)


def render_fiche(f: dict) -> str:
    title_html = inline(f["title"], f["source"])
    md = f["body"]
    # La ligne « Muscles » est remontée dans l'en-tête replié : on l'ôte du corps
    muscles = ""
    m = re.search(r"^\*\*Muscles\*\*\s*:\s*(.+)$", md, re.M)
    if m:
        muscles = f'<span class="fiche-muscles">{inline(m.group(1), f["source"])}</span>'
        md = md[:m.start()] + md[m.end():]
    body = convert(md, f["source"], base_level=4)
    return (
        f'<details class="fiche" id="{f["id"]}">'
        f'<summary><span class="fiche-titre">{title_html}</span>{muscles}</summary>'
        f'<div class="fiche-corps">{body}</div>'
        "</details>"
    )


# --------------------------------------------------------------------------
# Construction des onglets
# --------------------------------------------------------------------------


def strip_h1(md: str) -> tuple[str, str]:
    m = re.match(r"^#\s+(.*?)\n", md)
    return (m.group(1), md[m.end():]) if m else ("", md)


def build_seance(tab: str, label: str, sub: str, src: str, guide: str) -> str:
    title, body = strip_h1(read(src))
    fiches = parse_fiches(guide)
    fiches_html = "".join(render_fiche(f) for f in fiches)
    return f"""
<section class="panel" id="{tab}" role="tabpanel" aria-labelledby="tab-{tab}">
  <h1 class="panel-titre">{inline(title, src)}</h1>
  {convert(body, src)}
  <div class="fiches-entete">
    <h2>Fiches techniques détaillées</h2>
    <button class="btn-mini" data-toggle-fiches="{tab}">Tout ouvrir</button>
  </div>
  <p class="hint">Chaque fiche donne les réglages de la machine, la prise exacte des mains,
  l'exécution phase par phase, la respiration, le tempo, les erreurs fréquentes et deux vidéos.</p>
  {fiches_html}
</section>"""


def build_simple(tab: str, label: str, sub: str, src: str) -> str:
    title, body = strip_h1(read(src))
    return f"""
<section class="panel" id="{tab}" role="tabpanel" aria-labelledby="tab-{tab}">
  <h1 class="panel-titre">{inline(title, src)}</h1>
  {convert(body, src)}
</section>"""


CSS = """
:root{
  --bg:#0e1116; --bg2:#151921; --panel:#1a1f29; --line:#2a313d;
  --txt:#e8ebf0; --mut:#98a2b3; --acc:#3ddc97; --acc2:#0b3d2c;
  --warn:#f0a84a; --danger:#f2706f; --radius:12px;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--txt);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  padding-bottom:5rem}
a{color:var(--acc)}
a.lien-int{color:var(--acc);text-decoration:none;border-bottom:1px dotted var(--acc)}
a.lien-ext::after{content:" ↗";font-size:.8em;opacity:.6}
.ref{color:var(--mut)}
code{background:var(--bg2);border:1px solid var(--line);border-radius:5px;
  padding:.1em .35em;font-size:.88em}

/* En-tête */
header{position:sticky;top:0;z-index:50;background:rgba(14,17,22,.96);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.head-top{display:flex;align-items:baseline;gap:.7rem;
  padding:.7rem 1rem .1rem;max-width:960px;margin:0 auto}
.head-top h1{font-size:1rem;margin:0;letter-spacing:.01em}
.head-top span{font-size:.78rem;color:var(--mut)}
nav{display:flex;gap:.4rem;overflow-x:auto;scrollbar-width:none;
  padding:.6rem 1rem;max-width:960px;margin:0 auto;scroll-snap-type:x proximity}
nav::-webkit-scrollbar{display:none}
nav button{flex:0 0 auto;scroll-snap-align:start;cursor:pointer;
  background:var(--bg2);color:var(--mut);border:1px solid var(--line);
  border-radius:999px;padding:.5rem .95rem;font-size:.86rem;font-weight:500;
  font-family:inherit;white-space:nowrap;transition:.15s}
nav button:hover{color:var(--txt);border-color:#3b4553}
nav button[aria-selected="true"]{background:var(--acc2);color:var(--acc);
  border-color:var(--acc)}
nav button b{display:block;font-weight:600;font-size:.86rem}
nav button i{display:block;font-style:normal;font-size:.68rem;opacity:.75;margin-top:1px}

/* Contenu */
main{max-width:960px;margin:0 auto;padding:1.2rem 1rem 3rem}
.panel{display:none;animation:in .18s ease-out}
.panel.actif{display:block}
.panel,.fiche,h2,h3,h4{scroll-margin-top:7rem}
@keyframes in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.panel-titre{font-size:1.5rem;line-height:1.25;margin:.2rem 0 1rem;letter-spacing:-.01em}
h2{font-size:1.15rem;margin:2rem 0 .7rem;padding-top:.3rem}
h3{font-size:1rem;margin:1.5rem 0 .5rem;color:var(--acc)}
h4{font-size:.95rem;margin:1.3rem 0 .4rem;color:var(--acc)}
h5,h6{font-size:.9rem;margin:1.1rem 0 .35rem;color:var(--acc)}
p{margin:.7rem 0}
ul,ol{margin:.7rem 0;padding-left:1.35rem}
li{margin:.3rem 0}
hr{border:0;border-top:1px solid var(--line);margin:2rem 0}
blockquote{margin:1rem 0;padding:.7rem 1rem;background:var(--bg2);
  border-left:3px solid var(--acc);border-radius:0 var(--radius) var(--radius) 0;
  color:var(--mut);font-size:.92rem}
.hint{color:var(--mut);font-size:.87rem}
strong{color:#fff;font-weight:600}

/* Tableaux */
.tbl-wrap{overflow-x:auto;margin:1rem 0;border:1px solid var(--line);
  border-radius:var(--radius);background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{padding:.6rem .7rem;text-align:left;vertical-align:top;
  border-bottom:1px solid var(--line)}
th{background:var(--bg2);color:var(--mut);font-weight:600;font-size:.78rem;
  text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(61,220,151,.035)}
td:first-child{color:#fff;font-weight:500}
.tbl-erreurs td:first-child{color:var(--danger);font-weight:500}

/* Fiches */
.fiches-entete{display:flex;align-items:center;justify-content:space-between;
  gap:1rem;margin:2.2rem 0 .3rem}
.fiches-entete h2{margin:0}
.btn-mini{cursor:pointer;background:var(--bg2);color:var(--mut);font-family:inherit;
  border:1px solid var(--line);border-radius:999px;padding:.35rem .8rem;font-size:.78rem}
.btn-mini:hover{color:var(--txt)}
.fiche{background:var(--panel);border:1px solid var(--line);
  border-radius:var(--radius);margin:.55rem 0;overflow:hidden}
.fiche[open]{border-color:#3b4553}
.fiche summary{cursor:pointer;display:block;list-style:none;position:relative;
  padding:.85rem 2.6rem .85rem 1rem}
.fiche summary::-webkit-details-marker{display:none}
.fiche summary::after{content:"＋";position:absolute;right:.95rem;top:.78rem;
  color:var(--acc);font-size:1rem;line-height:1.4}
.fiche[open] summary::after{content:"－"}
.fiche summary:hover{background:var(--bg2)}
.fiche-titre{display:block;font-weight:600;font-size:.98rem}
.fiche-muscles{display:block;font-size:.79rem;color:var(--mut);margin-top:.15rem}
.fiche-corps{padding:0 1rem 1.1rem;border-top:1px solid var(--line)}
.fiche-corps h4:first-of-type{margin-top:1rem}
.fiche:target{border-color:var(--acc);box-shadow:0 0 0 2px rgba(61,220,151,.18)}

/* Minuteur de repos */
#chrono{position:fixed;right:1rem;bottom:1rem;z-index:60;text-align:right}
#chrono-panneau{display:none;background:var(--panel);border:1px solid var(--line);
  border-radius:var(--radius);padding:.8rem;margin-bottom:.55rem;
  box-shadow:0 10px 30px rgba(0,0,0,.45)}
#chrono.ouvert #chrono-panneau{display:block}
#chrono-ecran{font-size:1.9rem;font-weight:600;font-variant-numeric:tabular-nums;
  text-align:center;margin:.1rem 0 .55rem;letter-spacing:.02em}
#chrono-ecran.fini{color:var(--acc)}
.chrono-presets{display:grid;grid-template-columns:repeat(3,1fr);gap:.35rem}
.chrono-presets button,#chrono-stop{cursor:pointer;font-family:inherit;
  background:var(--bg2);color:var(--txt);border:1px solid var(--line);
  border-radius:8px;padding:.45rem 0;font-size:.82rem}
.chrono-presets button:hover{border-color:var(--acc);color:var(--acc)}
#chrono-stop{width:100%;margin-top:.35rem;color:var(--mut);font-size:.76rem}
#chrono-bouton{cursor:pointer;font-family:inherit;background:var(--acc2);
  color:var(--acc);border:1px solid var(--acc);border-radius:999px;
  padding:.65rem 1.1rem;font-size:.85rem;font-weight:600;
  box-shadow:0 6px 20px rgba(0,0,0,.4)}

@media (max-width:600px){
  body{font-size:15px}
  main{padding:1rem .8rem 3rem}
  .panel-titre{font-size:1.3rem}
  nav{padding:.55rem .8rem}
  th,td{padding:.5rem .55rem;font-size:.84rem}
}
@media print{
  header,#chrono,.btn-mini{display:none}
  body{background:#fff;color:#000;padding:0}
  .panel{display:block!important}
  .fiche-corps{display:block!important}
  .tbl-wrap,.fiche{break-inside:avoid}
}
"""

JS = """
const onglets = [...document.querySelectorAll('nav button')];
const panneaux = [...document.querySelectorAll('.panel')];

function activer(id, pousser = true) {
  if (!panneaux.some(p => p.id === id)) id = panneaux[0].id;
  onglets.forEach(b => b.setAttribute('aria-selected', b.dataset.tab === id));
  panneaux.forEach(p => p.classList.toggle('actif', p.id === id));
  const actif = onglets.find(b => b.dataset.tab === id);
  if (actif) actif.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  if (pousser && location.hash.slice(1) !== id) history.replaceState(null, '', '#' + id);
  window.scrollTo({ top: 0 });
}

onglets.forEach(b => b.addEventListener('click', () => activer(b.dataset.tab)));

// Liens internes : ouvrir le bon onglet, déplier la fiche visée
document.addEventListener('click', e => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const cible = a.getAttribute('href').slice(1);
  e.preventDefault();
  if (panneaux.some(p => p.id === cible)) { activer(cible); return; }
  const el = document.getElementById(cible);
  if (!el) return;
  const panneau = el.closest('.panel');
  if (panneau) activer(panneau.id, false);
  if (el.tagName === 'DETAILS') el.open = true;
  requestAnimationFrame(() => el.scrollIntoView({ behavior: 'smooth', block: 'start' }));
});

// « Tout ouvrir » / « Tout fermer »
document.querySelectorAll('[data-toggle-fiches]').forEach(btn => {
  btn.addEventListener('click', () => {
    const fiches = document.querySelectorAll('#' + btn.dataset.toggleFiches + ' .fiche');
    const ouvrir = btn.textContent.trim() === 'Tout ouvrir';
    fiches.forEach(f => { f.open = ouvrir; });
    btn.textContent = ouvrir ? 'Tout fermer' : 'Tout ouvrir';
  });
});

// Minuteur de repos
const chrono = document.getElementById('chrono');
const ecran = document.getElementById('chrono-ecran');
let reste = 0, tick = null;

function afficher() {
  const m = Math.floor(reste / 60), s = reste % 60;
  ecran.textContent = m + ':' + String(s).padStart(2, '0');
  ecran.classList.toggle('fini', reste === 0);
}
function bip() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [0, 0.22, 0.44].forEach(d => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.value = 880; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.0001, ctx.currentTime + d);
      g.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + d + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + d + 0.15);
      o.start(ctx.currentTime + d); o.stop(ctx.currentTime + d + 0.16);
    });
  } catch (_) { /* son indisponible, sans conséquence */ }
}
function lancer(secondes) {
  clearInterval(tick);
  reste = secondes; afficher();
  tick = setInterval(() => {
    reste--; afficher();
    if (reste <= 0) { clearInterval(tick); tick = null; bip(); }
  }, 1000);
}

document.getElementById('chrono-bouton').addEventListener('click',
  () => chrono.classList.toggle('ouvert'));
document.querySelectorAll('.chrono-presets button').forEach(b =>
  b.addEventListener('click', () => lancer(+b.dataset.s)));
document.getElementById('chrono-stop').addEventListener('click', () => {
  clearInterval(tick); tick = null; reste = 0; afficher();
});
afficher();

// Au chargement : l'ancre peut viser un onglet, ou un élément situé dans un onglet
function ouvrirDepuisHash(pousser) {
  const cible = location.hash.slice(1);
  if (!cible || panneaux.some(p => p.id === cible)) {
    activer(cible || 's1', pousser);
    requestAnimationFrame(() => window.scrollTo({ top: 0 }));
    return;
  }
  const el = document.getElementById(cible);
  if (!el) { activer('s1', false); return; }
  const panneau = el.closest('.panel');
  if (panneau) activer(panneau.id, false);
  if (el.tagName === 'DETAILS') el.open = true;
  requestAnimationFrame(() => el.scrollIntoView({ block: 'start' }));
}

ouvrirDepuisHash(false);
window.addEventListener('hashchange', () => ouvrirDepuisHash(false));
"""


def build() -> None:
    register_all_anchors()

    def bouton(tab: str, label: str, sub: str) -> str:
        return (
            f'<button id="tab-{tab}" data-tab="{tab}" role="tab" aria-selected="false">'
            f"<b>{html.escape(label, quote=False)}</b>"
            f"<i>{html.escape(sub, quote=False)}</i></button>"
        )

    tabs_html = []
    panels = []
    for tab, label, sub, src, guide in SEANCES:
        tabs_html.append(bouton(tab, label, sub))
        panels.append(build_seance(tab, label, sub, src, guide))
    for tab, label, sub, src in SIMPLES:
        tabs_html.append(bouton(tab, label, sub))
        panels.append(build_simple(tab, label, sub, src))

    doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0e1116">
<meta name="robots" content="noindex">
<title>Mon programme de musculation — 4 séances</title>
<style>{CSS}</style>
</head>
<body>

<header>
  <div class="head-top">
    <h1>Mon programme de musculation</h1>
    <span>4 séances · débutant · 60 min</span>
  </div>
  <nav role="tablist" aria-label="Séances et guides">
    {''.join(tabs_html)}
  </nav>
</header>

<main>
{''.join(panels)}
</main>

<div id="chrono">
  <div id="chrono-panneau">
    <div id="chrono-ecran">0:00</div>
    <div class="chrono-presets">
      <button data-s="45">45 s</button>
      <button data-s="60">60 s</button>
      <button data-s="75">75 s</button>
      <button data-s="90">90 s</button>
      <button data-s="120">2 min</button>
      <button data-s="180">3 min</button>
    </div>
    <button id="chrono-stop">Remettre à zéro</button>
  </div>
  <button id="chrono-bouton" aria-label="Minuteur de repos">Repos</button>
</div>

<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    ko = doc.count('class="ref"')
    print(f"{OUT.relative_to(ROOT)} généré — {len(doc) / 1024:.0f} Ko, "
          f"{len(panels)} onglets, {len(FICHE_IDS)} fiches techniques"
          + (f", {ko} liens neutralisés (fichiers hors page)" if ko else ""))


if __name__ == "__main__":
    build()
