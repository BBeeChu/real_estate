from __future__ import annotations

import html
import json
import re
import shutil
import unicodedata
from html.parser import HTMLParser
from pathlib import Path


BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
APP_DIR = BASE / "app"
PAGES_DIR = APP_DIR / "pages"
ROOT_PAGES_DIR = BASE / "pages"


class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.in_heading = False
        self.title = ""
        self.headings: list[str] = []
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self.in_title = True
            self._buffer = []
        elif tag in {"h1", "h2"} and not self.headings:
            self.in_heading = True
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        text = normalize_space("".join(self._buffer))
        if tag == "title" and self.in_title:
            self.title = text
            self.in_title = False
        elif tag in {"h1", "h2"} and self.in_heading:
            if text:
                self.headings.append(text)
            self.in_heading = False

    def handle_data(self, data: str) -> None:
        if self.in_title or self.in_heading:
            self._buffer.append(data)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def normalized_name(path: Path) -> str:
    return unicodedata.normalize("NFC", path.name)


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    value = re.sub(r"[^0-9a-zA-Z가-힣]+", "-", value).strip("-")
    return value or "page"


def display_title(path: Path, source: str) -> str:
    parser = TitleParser()
    parser.feed(source)
    raw = parser.title or (parser.headings[0] if parser.headings else path.stem)
    title = unicodedata.normalize("NFC", raw.replace("📋", "")).strip()
    replacements = {
        "특약 선택 PRO 최종 완성": "원룸 특약",
        "보성부동산 특약 선택기": "아파트 주택 특약",
    }
    for old, new in replacements.items():
        title = title.replace(old, new)
    if "가계약" in normalized_name(path):
        return "가계약서"
    if "동의" in normalized_name(path):
        return "동의서명"
    return title or normalized_name(path).removesuffix(".html")


def category_for(title: str, source_name: str) -> str:
    text = unicodedata.normalize("NFC", f"{title} {source_name}")
    if "가계약" in text:
        return "가계약"
    if "동의" in text:
        return "동의"
    if "토지" in text:
        return "토지"
    if "상가" in text:
        return "상가"
    if "월세" in text or "원룸" in text:
        return "임대차"
    if "아파트" in text or "주택" in text or "기본" in text:
        return "주택/매매"
    return "기타"


def page_enhancement(page_id: str, title: str, is_precontract: bool) -> str:
    encoded = json.dumps(page_id, ensure_ascii=False)
    title_encoded = json.dumps(title, ensure_ascii=False)
    if is_precontract:
        return f"""
<script>
(function () {{
  const sharedKey = "realEstateSelectedClauses";
  const pageId = {encoded};

  function sharedClauses() {{
    try {{
      const stored = JSON.parse(localStorage.getItem(sharedKey) || "{{}}");
      return Object.entries(stored)
        .filter(([id]) => id !== pageId)
        .flatMap(([, entry]) => Array.isArray(entry.clauses) ? entry.clauses : [])
        .map(value => String(value).trim())
        .filter(Boolean)
        .filter((value, index, values) => values.indexOf(value) === index);
    }} catch (error) {{
      return [];
    }}
  }}

  function appendSharedClauses() {{
    const result = document.getElementById("result");
    if (!result) return;
    const clauses = sharedClauses();
    let text = result.value || "";
    text = text.replace(/\\n\\[다른 섹션 선택 특약\\][\\s\\S]*?(?=\\n\\n보성공인중개사사무소:|\\n보성공인중개사사무소:|$)/, "");
    if (clauses.length) {{
      text = text.replace("- 특약 선택 없음\\n", "");
      const block = "\\n[다른 섹션 선택 특약]\\n" + clauses.map((clause, index) => `${{index + 1}}. ${{clause}}`).join("\\n");
      text = text.replace(/\\n\\n보성공인중개사사무소:/, block + "\\n\\n보성공인중개사사무소:");
      if (text.indexOf(block) === -1) text += "\\n" + block;
    }}
    result.value = text;
  }}

  function installGenerateHook() {{
    if (typeof generateText === "function" && !generateText.__realEstateSharedHook) {{
      const original = generateText;
      generateText = function () {{
        original.apply(this, arguments);
        appendSharedClauses();
      }};
      generateText.__realEstateSharedHook = true;
      generateText();
      return true;
    }}
    appendSharedClauses();
    return false;
  }}

  function downloadContract() {{
    const result = document.getElementById("result");
    const text = result && result.value ? result.value.trim() : "";
    if (!text) {{
      alert("다운로드할 가계약서 문구가 없습니다.");
      return;
    }}
    const blob = new Blob([text], {{ type: "text/plain;charset=utf-8" }});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "가계약서.txt";
    document.body.appendChild(link);
    link.click();
    URL.revokeObjectURL(link.href);
    link.remove();
  }}

  function addDownloadButton() {{
    if (document.getElementById("re-download-precontract")) return;
    const group = document.querySelector(".btn-group");
    if (!group) return;
    const button = document.createElement("button");
    button.id = "re-download-precontract";
    button.className = "copy-btn";
    button.type = "button";
    button.textContent = "💾 다운로드";
    button.addEventListener("click", downloadContract);
    group.insertBefore(button, group.children[2] || null);
  }}

  window.addEventListener("storage", event => {{
    if (event.key === sharedKey) appendSharedClauses();
  }});
  window.addEventListener("message", event => {{
    if (event.data && event.data.type === "realEstateClausesUpdated") appendSharedClauses();
  }});

  addDownloadButton();
  installGenerateHook();
}}());
</script>
"""

    return f"""
<script>
(function () {{
  const pageId = {encoded};
  const pageTitle = {title_encoded};
  const sharedKey = "realEstateSelectedClauses";

  function selectedOptionText() {{
    const values = [];
    document.querySelectorAll("input[type=checkbox]:checked").forEach((input) => {{
      const label = input.closest("label");
      values.push(input.value || (label ? label.innerText : ""));
    }});
    document.querySelectorAll(".selected, .active").forEach((node) => {{
      values.push(node.innerText || node.textContent || "");
    }});
    return values
      .map(value => value.trim())
      .filter(Boolean)
      .filter((value, index, all) => all.indexOf(value) === index);
  }}

  function publishSelection() {{
    const selected = selectedOptionText();
    let stored = {{}};
    try {{
      stored = JSON.parse(localStorage.getItem(sharedKey) || "{{}}");
    }} catch (error) {{
      stored = {{}};
    }}
    if (selected.length) {{
      stored[pageId] = {{ title: pageTitle, clauses: selected }};
    }} else {{
      delete stored[pageId];
    }}
    localStorage.setItem(sharedKey, JSON.stringify(stored));
    try {{
      window.parent.postMessage({{ type: "realEstateClausesUpdated", pageId, clauses: selected }}, "*");
    }} catch (error) {{}}
  }}

  document.addEventListener("click", () => setTimeout(publishSelection, 0), true);
  document.addEventListener("change", () => setTimeout(publishSelection, 0), true);
  publishSelection();
}}());
</script>
"""


def inject_enhancement(source: str, page_id: str, title: str, is_precontract: bool) -> str:
    panel = page_enhancement(page_id, title, is_precontract)
    index = source.lower().rfind("</body>")
    if index != -1:
        return source[:index] + panel + "\n" + source[index:]
    return source + "\n" + panel


def build_pages() -> list[dict[str, str]]:
    if PAGES_DIR.exists():
        shutil.rmtree(PAGES_DIR)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    tools: list[dict[str, str]] = []
    for index, path in enumerate(sorted(DATA_DIR.glob("*.html")), start=1):
        source = path.read_text(encoding="utf-8")
        source_name = normalized_name(path)
        title = display_title(path, source)
        page_id = f"{index:02d}-{slugify(source_name.removesuffix('.html'))}"
        page_file = f"{page_id}.html"
        is_precontract = "가계약" in source_name
        (PAGES_DIR / page_file).write_text(
            inject_enhancement(source, page_id, title, is_precontract),
            encoding="utf-8",
        )
        tools.append(
            {
                "id": page_id,
                "title": title,
                "category": category_for(title, source_name),
                "source": source_name,
                "file": f"pages/{page_file}",
            }
        )
    return tools


def sync_root_pages() -> None:
    if ROOT_PAGES_DIR.exists():
        shutil.rmtree(ROOT_PAGES_DIR)
    shutil.copytree(PAGES_DIR, ROOT_PAGES_DIR)
    shutil.copy2(APP_DIR / "index.html", BASE / "index.html")
    shutil.copy2(APP_DIR / ".nojekyll", BASE / ".nojekyll")


def app_html(tools: list[dict[str, str]]) -> str:
    data = json.dumps(tools, ensure_ascii=False, indent=2)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>부동산 HTML 독립 실행 앱</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --panel: #ffffff;
      --text: #111827;
      --muted: #6b7280;
      --line: #d7dee8;
      --accent: #1f6feb;
      --accent-soft: #e8f1ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--bg);
    }}
    header {{
      height: 68px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px 20px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{ margin: 0; font-size: 21px; }}
    .subtle {{ color: var(--muted); font-size: 13px; }}
    .layout {{
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      height: calc(100vh - 68px);
    }}
    nav {{
      background: #fbfcfe;
      border-right: 1px solid var(--line);
      padding: 14px;
      overflow: auto;
    }}
    .search {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 11px 12px;
      font: inherit;
      margin-bottom: 12px;
      background: white;
    }}
    .category {{
      margin: 17px 0 8px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }}
    .page-btn {{
      width: 100%;
      border: 1px solid transparent;
      border-radius: 8px;
      padding: 10px 11px;
      margin-bottom: 5px;
      background: transparent;
      text-align: left;
      cursor: pointer;
      color: var(--text);
    }}
    .page-btn:hover {{ background: #edf2f7; }}
    .page-btn.active {{
      background: var(--accent-soft);
      border-color: #b8d4ff;
      color: #0b4fb3;
      font-weight: 800;
    }}
    main {{
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      min-width: 0;
    }}
    .toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 12px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }}
    .toolbar-title {{
      min-width: 0;
      font-weight: 800;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .actions {{ display: flex; gap: 8px; flex: 0 0 auto; }}
    .btn {{
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      border-radius: 8px;
      padding: 8px 10px;
      cursor: pointer;
      font-weight: 700;
      text-decoration: none;
      font-size: 14px;
    }}
    iframe {{
      width: 100%;
      height: 100%;
      border: 0;
      background: white;
    }}
    .empty {{
      padding: 18px;
      color: var(--muted);
    }}
    @media (max-width: 820px) {{
      header {{ height: auto; align-items: flex-start; flex-direction: column; }}
      .layout {{ display: block; height: auto; }}
      nav {{ border-right: 0; border-bottom: 1px solid var(--line); max-height: 280px; }}
      main {{ height: calc(100vh - 280px); min-height: 620px; }}
      .toolbar {{ align-items: flex-start; flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>부동산 HTML 독립 실행 앱</h1>
      <div class="subtle">원본 HTML을 각각 독립 iframe으로 실행합니다. 가운데에서 문구를 추가하고 오른쪽에서 복사, 인쇄, 파일 저장을 할 수 있습니다.</div>
    </div>
    <div class="subtle">GitHub Pages 배포용 정적 앱</div>
  </header>
  <div class="layout">
    <nav>
      <input id="search" class="search" placeholder="HTML 이름 검색">
      <div id="menu"></div>
    </nav>
    <main>
      <div class="toolbar">
        <div>
          <div class="toolbar-title" id="activeTitle">-</div>
        </div>
        <div class="actions">
          <a class="btn" id="openNew" target="_blank" rel="noopener">새 창</a>
          <button class="btn" id="reloadFrame" type="button">새로고침</button>
        </div>
      </div>
      <iframe id="pageFrame" title="선택한 HTML"></iframe>
    </main>
  </div>
  <script>
    const PAGES = {data};
    const state = {{
      activeId: location.hash ? decodeURIComponent(location.hash.slice(1)) : PAGES[0]?.id,
      query: ""
    }};

    const menu = document.getElementById("menu");
    const frame = document.getElementById("pageFrame");
    const activeTitle = document.getElementById("activeTitle");
    const openNew = document.getElementById("openNew");

    function activePage() {{
      return PAGES.find(page => page.id === state.activeId) || PAGES[0];
    }}

    function renderMenu() {{
      const query = state.query.trim().toLowerCase();
      const filtered = PAGES.filter(page => {{
        const text = `${{page.title}} ${{page.source}} ${{page.category}}`.toLowerCase();
        return !query || text.includes(query);
      }});
      const groups = new Map();
      filtered.forEach(page => {{
        if (!groups.has(page.category)) groups.set(page.category, []);
        groups.get(page.category).push(page);
      }});
      menu.innerHTML = "";
      groups.forEach((pages, category) => {{
        const heading = document.createElement("div");
        heading.className = "category";
        heading.textContent = category;
        menu.appendChild(heading);
        pages.forEach(page => {{
          const button = document.createElement("button");
          button.type = "button";
          button.className = "page-btn" + (page.id === state.activeId ? " active" : "");
          button.innerHTML = `<div>${{escapeHtml(page.title)}}</div>`;
          button.addEventListener("click", () => openPage(page.id));
          menu.appendChild(button);
        }});
      }});
      if (!filtered.length) {{
        menu.innerHTML = '<div class="empty">검색 결과가 없습니다.</div>';
      }}
    }}

    function openPage(id) {{
      state.activeId = id;
      const page = activePage();
      location.hash = encodeURIComponent(page.id);
      frame.src = page.file;
      activeTitle.textContent = page.title;
      openNew.href = page.file;
      renderMenu();
    }}

    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, char => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }}[char]));
    }}

    document.getElementById("search").addEventListener("input", event => {{
      state.query = event.target.value;
      renderMenu();
    }});
    document.getElementById("reloadFrame").addEventListener("click", () => {{
      frame.contentWindow?.location.reload();
    }});
    window.addEventListener("hashchange", () => {{
      const id = decodeURIComponent(location.hash.slice(1));
      if (id && id !== state.activeId) openPage(id);
    }});

    renderMenu();
    if (activePage()) openPage(activePage().id);
  </script>
</body>
</html>
"""


def readme() -> str:
    return """# 부동산 HTML 독립 실행 앱

`../data`의 기존 HTML 11개를 각각 독립 페이지로 유지해 실행하는 정적 앱입니다.

## 로컬 실행

```bash
cd /home/gentler/Develop2/real_estate/app
python3 -m http.server 8766
```

접속: `http://127.0.0.1:8766`

## 사용 방법

- 왼쪽 메뉴에서 원본 HTML 항목을 선택합니다.
- 선택한 HTML은 iframe 안에서 독립적으로 실행됩니다.
- 가계약 섹션을 제외한 다른 섹션에서 선택한 특약사항은 가계약서의 `가계약 문구 자동 생성` 특약사항에 자동으로 합산됩니다.
- 가계약서 작성 후 `다운로드` 버튼으로 텍스트 파일을 저장할 수 있습니다.

## GitHub Pages 배포

이 저장소 루트에 `.github/workflows/real-estate-pages.yml`가 생성되어 있습니다.

1. 변경 파일을 GitHub 저장소에 push합니다.
2. GitHub 저장소의 `Settings > Pages`에서 Source를 `GitHub Actions`로 설정합니다.
3. `Actions > Deploy real estate app to GitHub Pages`를 실행하거나, 관련 파일을 push하면 자동 배포됩니다.

배포 대상 폴더는 git 저장소 루트 기준 `app`입니다.
"""


def main() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    tools = build_pages()
    (APP_DIR / "index.html").write_text(app_html(tools), encoding="utf-8")
    (APP_DIR / "README.md").write_text(readme(), encoding="utf-8")
    (APP_DIR / ".nojekyll").write_text("", encoding="utf-8")
    sync_root_pages()
    print(json.dumps({"pages": len(tools), "output": str(APP_DIR)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
