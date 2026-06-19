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


def custom_clause_panel(page_id: str) -> str:
    encoded = json.dumps(page_id, ensure_ascii=False)
    return f"""
<style>
  #re-custom-panel {{
    position: fixed;
    left: 50%;
    bottom: 16px;
    transform: translateX(-50%);
    z-index: 2147483647;
    width: min(520px, calc(100vw - 32px));
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: #111827;
  }}
  #re-custom-panel details {{
    border: 1px solid #cfd8e3;
    border-radius: 10px;
    background: #ffffff;
    box-shadow: 0 12px 30px rgba(15, 23, 42, .18);
    overflow: hidden;
  }}
  #re-custom-panel summary {{
    cursor: pointer;
    padding: 12px 14px;
    font-weight: 800;
    background: #1f6feb;
    color: white;
    user-select: none;
  }}
  #re-custom-panel .body {{
    padding: 12px;
    display: grid;
    gap: 8px;
  }}
  #re-custom-panel textarea {{
    width: 100%;
    min-height: 78px;
    resize: vertical;
    border: 1px solid #cfd8e3;
    border-radius: 8px;
    padding: 9px;
    font: inherit;
  }}
  #re-custom-panel button {{
    border: 1px solid #cfd8e3;
    background: #ffffff;
    border-radius: 8px;
    padding: 8px 10px;
    cursor: pointer;
    font-weight: 700;
  }}
  #re-custom-panel button.primary {{
    background: #1f6feb;
    border-color: #1f6feb;
    color: white;
  }}
  #re-custom-panel .actions {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  #re-action-dock {{
    position: fixed;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2147483647;
    width: 132px;
    display: grid;
    gap: 8px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }}
  #re-action-dock button {{
    border: 1px solid #cfd8e3;
    background: #ffffff;
    color: #111827;
    border-radius: 10px;
    padding: 10px 12px;
    cursor: pointer;
    font-weight: 800;
    box-shadow: 0 8px 22px rgba(15, 23, 42, .14);
  }}
  #re-action-dock button.primary {{
    background: #1f6feb;
    border-color: #1f6feb;
    color: white;
  }}
  #re-custom-panel .list {{
    max-height: 180px;
    overflow: auto;
    display: grid;
    gap: 6px;
  }}
  #re-custom-panel .item {{
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 8px;
    background: #f9fafb;
    line-height: 1.45;
  }}
  #re-custom-panel .item-row {{
    display: flex;
    justify-content: space-between;
    gap: 8px;
    align-items: flex-start;
  }}
  #re-custom-panel .delete {{
    color: #b42318;
    padding: 4px 7px;
    flex: 0 0 auto;
  }}
  @media print {{
    #re-custom-panel,
    #re-action-dock {{ display: none; }}
  }}
  @media (max-width: 760px) {{
    #re-custom-panel {{
      left: 12px;
      right: 12px;
      bottom: 12px;
      transform: none;
      width: auto;
    }}
    #re-action-dock {{
      right: 12px;
      top: 12px;
      transform: none;
      width: auto;
      grid-template-columns: repeat(3, auto);
    }}
  }}
</style>
<div id="re-custom-panel">
  <details>
    <summary>내 문구 추가</summary>
    <div class="body">
      <textarea id="re-custom-input" placeholder="이 HTML에만 저장할 문구를 입력하세요."></textarea>
      <div class="actions">
        <button class="primary" id="re-custom-add" type="button">추가</button>
        <button id="re-custom-clear" type="button">전체 삭제</button>
      </div>
      <div class="list" id="re-custom-list"></div>
    </div>
  </details>
</div>
<div id="re-action-dock" aria-label="문서 작업">
  <button class="primary" id="re-copy-doc" type="button">복사</button>
  <button id="re-print-doc" type="button">인쇄</button>
  <button id="re-save-doc" type="button">파일 저장</button>
</div>
<script>
(function () {{
  const pageId = {encoded};
  const key = "realEstateCustomClauses:" + pageId;
  const input = document.getElementById("re-custom-input");
  const list = document.getElementById("re-custom-list");
  const add = document.getElementById("re-custom-add");
  const clear = document.getElementById("re-custom-clear");
  const copyDoc = document.getElementById("re-copy-doc");
  const printDoc = document.getElementById("re-print-doc");
  const saveDoc = document.getElementById("re-save-doc");

  function read() {{
    try {{
      const value = JSON.parse(localStorage.getItem(key) || "[]");
      return Array.isArray(value) ? value : [];
    }} catch (error) {{
      return [];
    }}
  }}

  function write(values) {{
    localStorage.setItem(key, JSON.stringify(values));
  }}

  function render() {{
    const values = read();
    list.innerHTML = "";
    if (!values.length) {{
      list.innerHTML = '<div style="color:#6b7280;font-size:13px;">아직 추가한 문구가 없습니다.</div>';
      return;
    }}
    values.forEach((value, index) => {{
      const row = document.createElement("div");
      row.className = "item";
      row.innerHTML = '<div class="item-row"><div>' + (index + 1) + '. ' + escapeHtml(value) + '</div><button class="delete" type="button">삭제</button></div>';
      row.querySelector("button").addEventListener("click", () => {{
        const next = read().filter((_, itemIndex) => itemIndex !== index);
        write(next);
        render();
      }});
      list.appendChild(row);
    }});
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

  add.addEventListener("click", () => {{
    const value = input.value.trim();
    if (!value) {{
      alert("추가할 문구를 입력하세요.");
      return;
    }}
    const values = read();
    values.push(value);
    write(values);
    input.value = "";
    render();
  }});

  function selectedOptionText() {{
    const values = [];
    document.querySelectorAll("input[type=checkbox]:checked").forEach((input) => {{
      const label = input.closest("label");
      values.push(input.value || (label ? label.innerText : ""));
    }});
    document.querySelectorAll(".selected, .active").forEach((node) => {{
      if (node.closest("#re-custom-panel") || node.closest("#re-action-dock")) return;
      values.push(node.innerText || node.textContent || "");
    }});
    return values.map(value => value.trim()).filter(Boolean);
  }}

  function primaryResultText() {{
    const selectors = ["textarea#result", "#result", "#out", ".result", ".right"];
    for (const selector of selectors) {{
      const node = document.querySelector(selector);
      if (!node || node.closest("#re-custom-panel") || node.closest("#re-action-dock")) continue;
      const text = "value" in node ? node.value : node.innerText;
      if (text && text.trim()) return text.trim();
    }}
    return "";
  }}

  function exportText() {{
    const sections = [];
    const resultText = primaryResultText();
    if (resultText) sections.push(resultText);
    const selected = selectedOptionText();
    if (!resultText && selected.length) {{
      sections.push(selected.map((value, index) => `${{index + 1}}. ${{value}}`).join("\\n"));
    }}
    const custom = read();
    if (custom.length) {{
      sections.push("[내 문구]\\n" + custom.map((value, index) => `${{index + 1}}. ${{value}}`).join("\\n"));
    }}
    return sections.join("\\n\\n").trim();
  }}

  copyDoc.addEventListener("click", async () => {{
    const text = exportText();
    if (!text) {{
      alert("복사할 문구가 없습니다.");
      return;
    }}
    try {{
      await navigator.clipboard.writeText(text);
    }} catch (error) {{
      const temp = document.createElement("textarea");
      temp.value = text;
      document.body.appendChild(temp);
      temp.select();
      document.execCommand("copy");
      temp.remove();
    }}
    alert("복사 완료");
  }});

  printDoc.addEventListener("click", () => {{
    window.print();
  }});

  saveDoc.addEventListener("click", () => {{
    const text = exportText();
    if (!text) {{
      alert("저장할 문구가 없습니다.");
      return;
    }}
    const blob = new Blob([text], {{ type: "text/plain;charset=utf-8" }});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = pageId + "-문구.txt";
    document.body.appendChild(link);
    link.click();
    URL.revokeObjectURL(link.href);
    link.remove();
  }});

  clear.addEventListener("click", () => {{
    if (!confirm("이 HTML에 추가한 문구를 모두 삭제할까요?")) return;
    write([]);
    render();
  }});

  render();
}}());
</script>
"""


def inject_panel(source: str, page_id: str) -> str:
    panel = custom_clause_panel(page_id)
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
        (PAGES_DIR / page_file).write_text(inject_panel(source, page_id), encoding="utf-8")
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
    .source {{
      margin-top: 3px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 400;
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
          <div class="source" id="activeSource"></div>
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
    const activeSource = document.getElementById("activeSource");
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
          button.innerHTML = `<div>${{escapeHtml(page.title)}}</div><div class="source">${{escapeHtml(page.source)}}</div>`;
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
      activeSource.textContent = `원본: ${{page.source}}`;
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
- 각 HTML 오른쪽 아래의 `내 문구 추가` 패널에서 해당 HTML에만 저장되는 문구를 추가할 수 있습니다.
- 추가 문구는 브라우저 localStorage에 페이지별로 분리 저장됩니다.

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
