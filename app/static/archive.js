const archiveList = document.getElementById("archive-list");
const archiveMoreButton = document.getElementById("archive-more-btn");
const navTitle = document.getElementById("nav-title");
const navDigestLink = document.getElementById("nav-digest-link");
const navArchiveLink = document.getElementById("nav-archive-link");
const archiveMetaLabel = document.getElementById("archive-meta-label");
const archiveMetaSub = document.getElementById("archive-meta-sub");
const archiveTitle = document.getElementById("archive-title");
const archiveSubtitle = document.getElementById("archive-subtitle");
const langZhButton = document.getElementById("lang-zh-btn");
const langEnButton = document.getElementById("lang-en-btn");

const archiveDomain = "biomed_all";
let nextCursor = null;

const urlParams = new URLSearchParams(window.location.search);
let currentLanguage = (urlParams.get("lang") || localStorage.getItem("paper_bullet_lang") || "zh") === "en" ? "en" : "zh";

const TEXT = {
  zh: {
    documentTitle: "归档 | 论文速递 | Paper Bullet",
    brand: "论文速递",
    navDigest: "日报",
    navArchive: "归档",
    metaLabel: "Archive",
    metaSub: "历史日报",
    title: "论文速递归档",
    subtitle: "按日期回看往期导览，快速定位最近一段时间的重要生物医学研究文章。",
    loadMore: "加载更多",
    empty: "目前还没有历史归档。",
    initFail: "归档初始化失败。",
    papers: (count) => `${count} 篇`,
  },
  en: {
    documentTitle: "Archive | Paper Bullet",
    brand: "Paper Bullet",
    navDigest: "Digest",
    navArchive: "Archive",
    metaLabel: "Archive",
    metaSub: "Past issues",
    title: "Paper Bullet Archive",
    subtitle: "Browse previous issues by date and quickly revisit important biomedical papers from recent periods.",
    loadMore: "Load more",
    empty: "No archive entries are available yet.",
    initFail: "Archive initialization failed.",
    papers: (count) => `${count} papers`,
    cardTitle: "Paper Bullet",
    cardSubtitle: (date, count) => `${count} papers collected for ${date}.`,
  },
};

function t(key, ...args) {
  const entry = TEXT[currentLanguage][key];
  return typeof entry === "function" ? entry(...args) : entry;
}

function containsChinese(value = "") {
  return /[\u3400-\u9fff]/.test(String(value));
}

function localizedArchiveCardTitle(item) {
  if (currentLanguage === "zh") {
    return item.title || t("brand");
  }
  if (!item.title || containsChinese(item.title)) {
    return t("cardTitle");
  }
  return item.title;
}

function localizedArchiveCardSubtitle(item) {
  if (currentLanguage === "zh") {
    return item.subtitle || "";
  }
  if (!item.subtitle || containsChinese(item.subtitle)) {
    return t("cardSubtitle", item.date, item.total_papers || 0);
  }
  return item.subtitle;
}

function archiveEscape(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function updateLocation() {
  const url = new URL(window.location.href);
  url.searchParams.set("lang", currentLanguage);
  window.history.replaceState({}, "", url);
}

function applyLanguageChrome() {
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  document.title = t("documentTitle");
  navTitle.textContent = t("brand");
  navDigestLink.textContent = t("navDigest");
  navArchiveLink.textContent = t("navArchive");
  navDigestLink.href = `/?lang=${encodeURIComponent(currentLanguage)}`;
  navArchiveLink.href = `/archive?lang=${encodeURIComponent(currentLanguage)}`;
  archiveMetaLabel.textContent = t("metaLabel");
  archiveMetaSub.textContent = t("metaSub");
  archiveTitle.textContent = t("title");
  archiveSubtitle.textContent = t("subtitle");
  archiveMoreButton.textContent = t("loadMore");
  langZhButton.classList.toggle("active", currentLanguage === "zh");
  langEnButton.classList.toggle("active", currentLanguage === "en");
}

function renderArchiveItems(items, append) {
  const html = items
    .map(
      (item) => `
      <a class="archive-card reveal visible" href="/?domain=${encodeURIComponent(item.domain)}&date=${encodeURIComponent(item.date)}&lang=${encodeURIComponent(currentLanguage)}">
        <div class="archive-card-header">
          <span class="archive-card-date">${archiveEscape(item.date)}</span>
          <span class="archive-card-count">${archiveEscape(t("papers", item.total_papers || 0))}</span>
        </div>
        <h2>${archiveEscape(localizedArchiveCardTitle(item))}</h2>
        <p class="archive-card-subtitle">${archiveEscape(localizedArchiveCardSubtitle(item))}</p>
        <ul class="archive-card-overview">
          ${(item.overview || [])
            .filter((bullet) => currentLanguage === "zh" || !containsChinese(bullet))
            .map((bullet) => `<li>${archiveEscape(bullet)}</li>`)
            .join("")}
        </ul>
      </a>
    `
    )
    .join("");

  if (append) {
    archiveList.insertAdjacentHTML("beforeend", html);
  } else {
    archiveList.innerHTML = html || `<div class="article-section empty-state visible"><p>${archiveEscape(t("empty"))}</p></div>`;
  }
}

async function loadArchive(append) {
  const cursorPart = nextCursor ? `&cursor=${encodeURIComponent(nextCursor)}` : "";
  const response = await fetch(`/api/archive?domain=${encodeURIComponent(archiveDomain)}&limit=12${cursorPart}`);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Archive load failed");
  }
  renderArchiveItems(payload.items || [], append);
  nextCursor = payload.next_cursor || null;
  archiveMoreButton.disabled = !nextCursor;
}

function switchLanguage(language) {
  currentLanguage = language === "en" ? "en" : "zh";
  localStorage.setItem("paper_bullet_lang", currentLanguage);
  applyLanguageChrome();
  updateLocation();
  nextCursor = null;
  loadArchive(false).catch(() => {
    archiveList.innerHTML = `<div class="article-section empty-state visible"><p>${archiveEscape(t("initFail"))}</p></div>`;
  });
}

archiveMoreButton.addEventListener("click", () => {
  if (nextCursor) {
    loadArchive(true).catch(() => {});
  }
});

langZhButton.addEventListener("click", () => switchLanguage("zh"));
langEnButton.addEventListener("click", () => switchLanguage("en"));

applyLanguageChrome();
updateLocation();
nextCursor = null;
loadArchive(false).catch(() => {
  archiveList.innerHTML = `<div class="article-section empty-state visible"><p>${archiveEscape(t("initFail"))}</p></div>`;
});
