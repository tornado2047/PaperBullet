const dateFromInput = document.getElementById("date-from");
const dateToInput = document.getElementById("date-to");
const statusNode = document.getElementById("status");
const digestTitle = document.getElementById("digest-title");
const digestSubtitle = document.getElementById("digest-subtitle");
const digestMetaBrand = document.getElementById("digest-meta-brand");
const digestMetaDate = document.getElementById("digest-meta-date");
const sourceStatsNode = document.getElementById("source-stats");
const paperList = document.getElementById("paper-list");
const paperCountNode = document.getElementById("paper-count");
const paginationNode = document.getElementById("pagination");
const categoryStatsNode = document.getElementById("category-stats");
const recommendedGrid = document.getElementById("recommended-grid");
const prevWeekButton = document.getElementById("prev-week-btn");
const nextWeekButton = document.getElementById("next-week-btn");
const currentWeekButton = document.getElementById("current-week-btn");
const loadButton = document.getElementById("load-btn");
const refreshButton = document.getElementById("refresh-btn");
const navTitle = document.getElementById("nav-title");
const navDigestLink = document.getElementById("nav-digest-link");
const navArchiveLink = document.getElementById("nav-archive-link");
const sourceStatsLabel = document.getElementById("source-stats-label");
const archiveLink = document.getElementById("archive-link");
const rangeSeparator = document.getElementById("range-separator");
const paperSectionTitle = document.getElementById("paper-section-title");
const categorySectionTitle = document.getElementById("category-section-title");
const recommendationSectionTitle = document.getElementById("recommendation-section-title");
const langZhButton = document.getElementById("lang-zh-btn");
const langEnButton = document.getElementById("lang-en-btn");
const domainTabsNode = document.getElementById("domain-tabs");
const domainDescriptionNode = document.getElementById("domain-description");

const today = new Date().toISOString().slice(0, 10);
const PAGE_SIZE = 10;
const MAX_REFRESH_DAYS = 14;
const APP_NAMES = { zh: "论文速递", en: "Paper Bullet" };
const SOURCE_LABELS = {
  nature: "Nature",
  science: "Science",
  cell: "Cell",
  pubmed: "PubMed",
  biorxiv: "bioRxiv",
  medrxiv: "medRxiv",
  arxiv: "arXiv",
};
const CATEGORY_LABELS = {
  "综合生物医学": "General Biomedicine",
  "医学影像": "Medical Imaging",
  "临床与人群": "Clinical & Population",
  "基因组与多组学": "Genomics & Multi-omics",
  "蛋白质与分子": "Proteins & Molecules",
  "细胞与机制": "Cells & Mechanisms",
  "工具与方法": "Tools & Methods",
};
const DOMAIN_LABELS_EN = {
  biomed_all: "Biomedical Overview",
  drug_discovery: "Drug Discovery",
  medical_imaging: "Medical Imaging",
  clinical_ai: "Clinical AI & Medical LMs",
  genomics_omics: "Genomics & Multi-omics",
  protein_biomolecules: "Proteins & Biomolecules",
};
const DOMAIN_DESCRIPTIONS_EN = {
  biomed_all: "A broad biomedical view across methods, diseases, molecules, imaging, clinical studies, and multi-omics.",
  drug_discovery: "Drug discovery, molecular generation, target discovery, binding prediction, therapeutics, and pharmacology.",
  medical_imaging: "Radiology, pathology, microscopy, segmentation, diagnosis, multimodal imaging, and imaging AI.",
  clinical_ai: "Clinical AI, medical language models, EHRs, decision support, real-world evidence, and population health.",
  genomics_omics: "Genomics, transcriptomics, single-cell studies, multi-omics, spatial biology, variants, and systems biology.",
  protein_biomolecules: "Protein structure, enzyme engineering, antibodies, nucleic acids, biomolecular design, and structure prediction.",
};

const TEXT = {
  zh: {
    documentTitle: "论文速递 | Paper Bullet",
    navDigest: "日报",
    navArchive: "归档",
    brand: "论文速递",
    metaBrand: "Paper Bullet",
    mastheadFallback: "聚合预印本、PubMed 与 Nature / Cell / Science 官方期刊来源，整理最新生物医学论文摘要与关键词。",
    sourceStats: "本期来源",
    allSources: "全部来源",
    viewArchive: "查看归档",
    prevWeek: "上一周",
    nextWeek: "下一周",
    recentWeek: "最近一周",
    loadRange: "读取本时段",
    refreshRange: "更新本时段",
    ready: "准备就绪",
    paperList: "论文列表",
    categoryStats: "领域分布",
    recommendations: "Paper 推荐",
    defaultCategory: "综合生物医学",
    rangeTo: "至",
    loadingDigest: "正在读取本时段简报...",
    loadingLegacy: "正在聚合旧版接口的整段论文列表并生成分页...",
    readingDone: (page, totalPages) => `时段简报读取完成，第 ${page} / ${totalPages} 页`,
    legacyDone: (page, totalPages) => `已兼容旧版接口分页显示，第 ${page} / ${totalPages} 页`,
    loadingRefresh: "正在抓取时段内多源论文并生成简报，这一步可能需要几十秒...",
    loadingRefreshLegacy: "抓取完成，正在聚合旧版接口论文并生成分页...",
    loadingRefreshChunk: (index, total, from, to) => `正在更新第 ${index} / ${total} 段：${from} 至 ${to}`,
    refreshDone: (count) => `更新完成，共整理 ${count} 篇论文`,
    rangeChanged: "已选择新时段，点击“读取本时段”查看已有数据，或点击“更新本时段”抓取新数据。",
    currentPageEmpty: "当前页暂无论文。",
    noCategoryStats: "暂无可展示的领域统计。",
    noSourceStats: "暂无来源统计",
    sourceEmptyAfterFilter: "当前来源筛选下没有论文。",
    emptyHint: "可以换一个来源、缩短时间范围，或点击“更新本时段”重新抓取。",
    clearSourceFilter: "清除来源筛选",
    useRecentWeek: "改看最近一周",
    invalidRange: "开始日期不能晚于结束日期。",
    futureRange: "结束日期不能晚于今天。",
    refreshRangeTooLarge: (days) => `当前选择了 ${days} 天，将自动拆分为每段不超过 ${MAX_REFRESH_DAYS} 天进行更新。`,
    loadingShort: "处理中",
    noRecommendations: "当前时段内还没有可推荐的高引论文。",
    currentCountModern: (total, pageCount) => `共 ${total} 篇，本页 ${pageCount} 篇`,
    currentCountLegacy: (total, pageCount, pages) => `共 ${total} 篇，当前第 ${pages ? `${currentPage} / ${pages}` : "1 / 1"} 页，本页 ${pageCount} 篇`,
    authors: "作者",
    institutions: "机构",
    journal: "期刊",
    year: "年份",
    doi: "DOI",
    abstract: "Abstract",
    keywords: "Keywords",
    noAbstract: "当前未抓到该文摘要，请点击原文查看。",
    original: "原文",
    details: "详情",
    pdf: "PDF",
    prevPage: "上一页",
    nextPage: "下一页",
    noRecommendationsCitations: "引用数未披露",
    citations: (count) => `引用 ${count}`,
    recommendationSource: "期刊",
    recommendationCategory: "领域",
    recommendationLink: "查看论文",
    initFail: "初始化失败",
  },
  en: {
    documentTitle: "Paper Bullet",
    navDigest: "Digest",
    navArchive: "Archive",
    brand: "Paper Bullet",
    metaBrand: "Paper Bullet",
    mastheadFallback: "Aggregates preprints, PubMed, and official Nature / Cell / Science sources with original biomedical abstracts and keywords.",
    sourceStats: "Sources",
    allSources: "All sources",
    viewArchive: "Open archive",
    prevWeek: "Previous week",
    nextWeek: "Next week",
    recentWeek: "Last 7 days",
    loadRange: "Load range",
    refreshRange: "Refresh range",
    ready: "Ready",
    paperList: "Papers",
    categoryStats: "Field distribution",
    recommendations: "Recommended Papers",
    defaultCategory: "General Biomedicine",
    rangeTo: "to",
    loadingDigest: "Loading digest for the selected range...",
    loadingLegacy: "Collecting full papers from the legacy API and building pagination...",
    readingDone: (page, totalPages) => `Digest loaded, page ${page} / ${totalPages}`,
    legacyDone: (page, totalPages) => `Legacy API pagination is active, page ${page} / ${totalPages}`,
    loadingRefresh: "Refreshing multi-source papers for this range. This may take a while...",
    loadingRefreshLegacy: "Refresh finished. Building pagination from the legacy API...",
    loadingRefreshChunk: (index, total, from, to) => `Refreshing chunk ${index} / ${total}: ${from} to ${to}`,
    refreshDone: (count) => `Refresh complete, ${count} papers organized`,
    rangeChanged: "New range selected. Click Load range to read stored data, or Refresh range to collect fresh papers.",
    currentPageEmpty: "No papers are available on this page.",
    noCategoryStats: "No field distribution is available yet.",
    noSourceStats: "No source stats available",
    sourceEmptyAfterFilter: "No papers match the selected sources.",
    emptyHint: "Try another source, narrow the range, or refresh this range to collect fresh papers.",
    clearSourceFilter: "Clear source filters",
    useRecentWeek: "Use last 7 days",
    invalidRange: "The start date cannot be later than the end date.",
    futureRange: "The end date cannot be later than today.",
    refreshRangeTooLarge: (days) => `The selected range has ${days} days and will be refreshed in chunks of ${MAX_REFRESH_DAYS} days or fewer.`,
    loadingShort: "Working",
    noRecommendations: "No citation-based recommendations are available for this range yet.",
    currentCountModern: (total, pageCount) => `${total} papers in total, ${pageCount} on this page`,
    currentCountLegacy: (total, pageCount, pages) => `${total} papers in total, page ${currentPage} / ${pages || 1}, ${pageCount} on this page`,
    authors: "Authors",
    institutions: "Affiliations",
    journal: "Journal",
    year: "Year",
    doi: "DOI",
    abstract: "Abstract",
    keywords: "Keywords",
    noAbstract: "No abstract was captured. Please open the original paper.",
    original: "Original",
    details: "Details",
    pdf: "PDF",
    prevPage: "Previous",
    nextPage: "Next",
    noRecommendationsCitations: "Citation count unavailable",
    citations: (count) => `${count} citations`,
    recommendationSource: "Journal",
    recommendationCategory: "Field",
    recommendationLink: "Open paper",
    initFail: "Initialization failed",
  },
};

let selectedDomain = "biomed_all";
let currentPage = 1;
let totalPages = 0;
let currentLanguage = "zh";
let selectedSources = new Set();
let availableDomains = [];
let activeRequestId = 0;

const urlParams = new URLSearchParams(window.location.search);
selectedDomain = urlParams.get("domain") || selectedDomain;
currentPage = Math.max(1, Number.parseInt(urlParams.get("page") || "1", 10) || 1);
currentLanguage = resolveLanguage(urlParams.get("lang") || localStorage.getItem("paper_bullet_lang") || "zh");
selectedSources = new Set(parseSourcesParam(urlParams.get("sources")));

const legacyDate = urlParams.get("date");
if (urlParams.get("date_from") || urlParams.get("date_to")) {
  dateFromInput.value = urlParams.get("date_from") || today;
  dateToInput.value = urlParams.get("date_to") || today;
} else if (legacyDate) {
  dateFromInput.value = legacyDate;
  dateToInput.value = legacyDate;
} else {
  setDefaultRange();
}

function resolveLanguage(value) {
  return value === "en" ? "en" : "zh";
}

function t(key, ...args) {
  const entry = TEXT[currentLanguage][key];
  return typeof entry === "function" ? entry(...args) : entry;
}

function containsChinese(value = "") {
  return /[\u3400-\u9fff]/.test(String(value));
}

function translateCategoryLabel(label) {
  if (!label) {
    return t("defaultCategory");
  }
  if (currentLanguage === "zh") {
    return label;
  }
  return CATEGORY_LABELS[label] || label;
}

function englishSubtitleFromPayload(payload) {
  const total = payload.total_papers || 0;
  const sourceLabels = (payload.source_stats || []).map((item) => item.label).slice(0, 5);
  let subtitle = `This issue curates ${total} biomedical research papers from preprints, PubMed, and official Nature / Science / Cell journals.`;
  if (sourceLabels.length) {
    subtitle += ` Current sources include ${sourceLabels.join(", ")}.`;
  }
  return subtitle;
}

function localizedDigestSubtitle(payload) {
  if (currentLanguage === "zh") {
    return payload.subtitle || t("mastheadFallback");
  }
  if (!payload.subtitle || containsChinese(payload.subtitle)) {
    return englishSubtitleFromPayload(payload);
  }
  return payload.subtitle;
}

function localizedPeriodLabel(value) {
  const raw = String(value || "");
  if (currentLanguage === "zh") {
    return raw;
  }
  return raw.replace(/\s*至\s*/g, " to ");
}

function parseSourcesParam(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter((item) => item && SOURCE_LABELS[item]);
}

function setStatus(message, isError = false) {
  statusNode.textContent = message;
  statusNode.classList.toggle("error", isError);
}

function setBusy(isBusy) {
  [loadButton, refreshButton, prevWeekButton, nextWeekButton, currentWeekButton, dateFromInput, dateToInput].forEach((node) => {
    node.disabled = isBusy;
  });
  document.body.classList.toggle("is-busy", isBusy);
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function formatPeople(items = [], max = 4) {
  if (!items.length) {
    return currentLanguage === "zh" ? "未披露" : "Unavailable";
  }
  const visible = items.slice(0, max).map((item) => escapeHtml(item));
  if (items.length > max) {
    visible.push(currentLanguage === "zh" ? `等 ${items.length} 位` : `${items.length} total`);
  }
  return visible.join(currentLanguage === "zh" ? "、" : ", ");
}

function renderFact(label, value) {
  const unavailable = currentLanguage === "zh" ? "未披露" : "Unavailable";
  if (!value || value === unavailable) {
    return "";
  }
  return `
    <div class="paper-fact">
      <span class="fact-label">${escapeHtml(label)}</span>
      <span class="fact-value">${value}</span>
    </div>
  `;
}

function renderCategoryStats(items = []) {
  if (!items.length) {
    return `<div class="empty-state visible"><p>${escapeHtml(t("noCategoryStats"))}</p></div>`;
  }
  const maxCount = Math.max(...items.map((item) => item.count), 1);
  return items
    .map((item) => {
      const width = Math.max(18, Math.round((item.count / maxCount) * 100));
      const countLabel = currentLanguage === "zh" ? `${item.count} 篇` : `${item.count}`;
      return `
        <div class="category-row">
          <div class="category-row-head">
            <span class="category-label">${escapeHtml(translateCategoryLabel(item.label))}</span>
            <span class="category-count">${escapeHtml(String(countLabel))}</span>
          </div>
          <div class="category-bar-track">
            <div class="category-bar-fill" style="width:${width}%"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function updateLocation() {
  const url = new URL(window.location.href);
  url.searchParams.set("domain", selectedDomain);
  url.searchParams.set("date_from", dateFromInput.value);
  url.searchParams.set("date_to", dateToInput.value);
  url.searchParams.set("page", String(currentPage));
  url.searchParams.set("lang", currentLanguage);
  if (selectedSources.size) {
    url.searchParams.set("sources", [...selectedSources].join(","));
  } else {
    url.searchParams.delete("sources");
  }
  url.searchParams.delete("date");
  window.history.replaceState({}, "", url);
}

function toIsoDate(date) {
  return date.toISOString().slice(0, 10);
}

function setWeekRange(anchorDate) {
  const end = new Date(anchorDate);
  const start = new Date(anchorDate);
  start.setDate(start.getDate() - 6);
  dateFromInput.value = toIsoDate(start);
  dateToInput.value = toIsoDate(end);
}

function setDefaultRange() {
  const currentYear = new Date(`${today}T00:00:00`).getFullYear();
  dateFromInput.value = `${currentYear}-01-01`;
  dateToInput.value = today;
}

function getSelectedDomain() {
  return availableDomains.find((domain) => domain.key === selectedDomain) || null;
}

function localizedDomainDescription(domain) {
  if (!domain) {
    return "";
  }
  if (currentLanguage === "en") {
    return DOMAIN_DESCRIPTIONS_EN[domain.key] || domain.description || "";
  }
  return domain.description || "";
}

function validateDateRange() {
  if (!dateFromInput.value || !dateToInput.value) {
    return true;
  }
  if (dateFromInput.value > dateToInput.value) {
    setStatus(t("invalidRange"), true);
    return false;
  }
  if (dateToInput.value > today) {
    setStatus(t("futureRange"), true);
    return false;
  }
  return true;
}

function selectedRangeDays() {
  if (!dateFromInput.value || !dateToInput.value) {
    return 0;
  }
  const start = parseIsoDate(dateFromInput.value);
  const end = parseIsoDate(dateToInput.value);
  return Math.floor((end - start) / 86400000) + 1;
}

function validateRefreshRange() {
  if (!validateDateRange()) {
    return false;
  }
  const days = selectedRangeDays();
  if (days > MAX_REFRESH_DAYS) {
    setStatus(t("refreshRangeTooLarge", days));
  }
  return true;
}

function buildRefreshChunks() {
  const chunks = [];
  const current = parseIsoDate(dateFromInput.value);
  const end = parseIsoDate(dateToInput.value);
  while (current <= end) {
    const chunkStart = new Date(current);
    const chunkEnd = new Date(current);
    chunkEnd.setDate(chunkEnd.getDate() + MAX_REFRESH_DAYS - 1);
    if (chunkEnd > end) {
      chunkEnd.setTime(end.getTime());
    }
    chunks.push({ from: toIsoDate(chunkStart), to: toIsoDate(chunkEnd) });
    current.setDate(current.getDate() + MAX_REFRESH_DAYS);
  }
  return chunks;
}

function markRangeChanged() {
  currentPage = 1;
  updateLocation();
  if (validateDateRange()) {
    setStatus(t("rangeChanged"));
  }
}

function renderDomains(domains) {
  availableDomains = domains || [];
  if (!domains.some((domain) => domain.key === selectedDomain) && domains.length) {
    selectedDomain = domains[0].key;
  }
  if (!domainTabsNode) {
    return;
  }
  domainTabsNode.innerHTML = domains
    .map((domain) => {
      const active = domain.key === selectedDomain;
      const label = currentLanguage === "en" ? DOMAIN_LABELS_EN[domain.key] || domain.key : domain.label || domain.key;
      return `<button class="tab-pill domain-tab ${active ? "active" : ""}" type="button" data-domain="${escapeHtml(domain.key)}">${escapeHtml(label)}</button>`;
    })
    .join("");
  if (domainDescriptionNode) {
    domainDescriptionNode.textContent = localizedDomainDescription(getSelectedDomain());
  }
}

function renderEmptyState(message) {
  const clearFilterButton = selectedSources.size
    ? `<button class="inline-action" type="button" data-empty-action="clear-sources">${escapeHtml(t("clearSourceFilter"))}</button>`
    : "";
  return `
    <div class="empty-state visible rich-empty">
      <p>${escapeHtml(message)}</p>
      <p class="empty-hint">${escapeHtml(t("emptyHint"))}</p>
      <div class="empty-actions">
        ${clearFilterButton}
        <button class="inline-action" type="button" data-empty-action="recent-week">${escapeHtml(t("useRecentWeek"))}</button>
      </div>
    </div>
  `;
}

function renderSourceStats(items = []) {
  const stats = items
    .map((item) => ({
      key: normalizeSourceKey(item.key || item.label || ""),
      label: item.label || sourceLabelForKey(normalizeSourceKey(item.key || item.label || "")),
      count: item.count || 0,
    }))
    .filter((item) => item.key);

  if (!stats.length) {
    return `<span class="source-stat empty">${escapeHtml(t("noSourceStats"))}</span>`;
  }
  const allActive = selectedSources.size === 0;
  const allChip = `
    <button class="source-stat source-filter ${allActive ? "active" : ""}" type="button" data-source-key="all">
      ${escapeHtml(t("allSources"))}
    </button>
  `;
  const suffix = currentLanguage === "zh" ? " 篇" : "";
  const statChips = stats
    .map((item) => {
      const active = selectedSources.size === 0 ? false : selectedSources.has(item.key);
      return `
        <button class="source-stat source-filter ${active ? "active" : ""}" type="button" data-source-key="${escapeHtml(item.key)}">
          ${escapeHtml(item.label)} ${escapeHtml(String(item.count))}${suffix}
        </button>
      `;
    })
    .join("");
  return `${allChip}${statChips}`;
}

function normalizeSourceKey(value) {
  const normalized = String(value || "").trim().toLowerCase();
  if (SOURCE_LABELS[normalized]) {
    return normalized;
  }
  const byLabel = {
    nature: "nature",
    science: "science",
    cell: "cell",
    pubmed: "pubmed",
    biorxiv: "biorxiv",
    medrxiv: "medrxiv",
    arxiv: "arxiv",
  };
  return byLabel[normalized.replace(/[^a-z]/g, "")] || "";
}

function sourceLabelForKey(key) {
  return SOURCE_LABELS[key] || key;
}

function sourceKeyFromPaper(paper = {}) {
  const family = normalizeSourceKey(paper.source_family || "");
  if (family) {
    return family;
  }
  const source = String(paper.source || "").toLowerCase();
  const journal = String(paper.journal_or_server || "").toLowerCase();
  if (source === "pubmed") {
    return "pubmed";
  }
  if (source === "biorxiv") {
    return "biorxiv";
  }
  if (source === "medrxiv") {
    return "medrxiv";
  }
  if (source === "arxiv") {
    return "arxiv";
  }
  if (source === "cell_press") {
    return "cell";
  }
  if (source === "science_journal" || journal === "science") {
    return "science";
  }
  if (source === "nature_journal" || journal.startsWith("nature")) {
    return "nature";
  }
  return "";
}

function parseIsoDate(value) {
  return new Date(`${value}T00:00:00`);
}

function enumerateDateRange(startValue, endValue) {
  const dates = [];
  const current = parseIsoDate(startValue);
  const end = parseIsoDate(endValue);
  while (current <= end) {
    dates.push(toIsoDate(current));
    current.setDate(current.getDate() + 1);
  }
  return dates;
}

function paperIdentityKey(paper = {}) {
  const doi = String(paper.doi || "").trim().toLowerCase();
  if (doi) {
    return `doi:${doi}`;
  }
  const title = String(paper.title || "").toLowerCase().replace(/[^a-z0-9]+/g, "");
  return `title:${title}`;
}

function sortPapersDescending(papers = []) {
  return [...papers].sort((left, right) => {
    const leftCitation = left.citation_count ?? -1;
    const rightCitation = right.citation_count ?? -1;
    if (rightCitation !== leftCitation) {
      return rightCitation - leftCitation;
    }
    const scoreDiff = Number(right.ranking_score || 0) - Number(left.ranking_score || 0);
    if (scoreDiff !== 0) {
      return scoreDiff;
    }
    const rightDate = String(right.published_at || "");
    const leftDate = String(left.published_at || "");
    return rightDate.localeCompare(leftDate);
  });
}

function buildRecommendations(papers = []) {
  return sortPapersDescending(papers)
    .filter((paper) => paper.title)
    .slice(0, 3);
}

function filterPapersBySources(papers = []) {
  if (!selectedSources.size) {
    return papers;
  }
  return papers.filter((paper) => selectedSources.has(sourceKeyFromPaper(paper)));
}

async function fetchLegacyRangePapers() {
  const dates = enumerateDateRange(dateFromInput.value, dateToInput.value);
  const responses = await Promise.all(
    dates.map(async (day) => {
      const response = await fetch(
        `/api/papers?domain=${encodeURIComponent(selectedDomain)}&date=${encodeURIComponent(day)}&limit=500`
      );
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || `${day} load failed`);
      }
      return payload.items || [];
    })
  );

  const chosen = new Map();
  responses.flat().forEach((paper) => {
    const key = paperIdentityKey(paper);
    const existing = chosen.get(key);
    if (!existing || Number(paper.ranking_score || 0) >= Number(existing.ranking_score || 0)) {
      chosen.set(key, paper);
    }
  });
  return filterPapersBySources(sortPapersDescending([...chosen.values()]));
}

async function hydrateLegacyPaginationPayload(payload) {
  const papers = await fetchLegacyRangePapers();
  const totalPaperCount = papers.length;
  const computedTotalPages = totalPaperCount ? Math.ceil(totalPaperCount / PAGE_SIZE) : 0;
  const safePage = computedTotalPages ? Math.min(currentPage, computedTotalPages) : 1;
  const startIndex = (safePage - 1) * PAGE_SIZE;
  const pageItems = papers.slice(startIndex, startIndex + PAGE_SIZE);
  return {
    ...payload,
    items: pageItems,
    page: safePage,
    page_size: PAGE_SIZE,
    total_pages: computedTotalPages,
    total_papers: totalPaperCount,
    recommended: buildRecommendations(papers),
  };
}

function renderPaperCard(paper, index) {
  const displayNumber = (currentPage - 1) * PAGE_SIZE + index + 1;
  const abstract = (paper.abstract_brief || "").trim();
  const categoryLabel = translateCategoryLabel(paper.research_category || paper.topic_label || "综合生物医学");
  const abstractMarkup = abstract
    ? `<p class="abstract-text full">${escapeHtml(abstract)}</p>`
    : `<p class="abstract-text empty">${escapeHtml(t("noAbstract"))}</p>`;

  return `
    <article class="paper-card visible">
      <h3>
        <span class="paper-num">${String(displayNumber).padStart(2, "0")}</span>
        <span class="feature-title-wrap">
          <span class="paper-tag">${escapeHtml(categoryLabel)}</span>
          ${escapeHtml(paper.title || "Untitled paper")}
        </span>
      </h3>
      <p class="feature-journal-line">${escapeHtml(paper.journal_or_server || paper.source || "Source unavailable")} · ${escapeHtml(paper.published_at || paper.publication_year || "Date unavailable")}</p>
      <div class="paper-basic-grid">
        ${renderFact(t("authors"), formatPeople(paper.authors || [], 5))}
        ${renderFact(t("institutions"), formatPeople(paper.institutions || [], 2))}
        ${renderFact(t("journal"), escapeHtml(paper.journal_or_server || paper.source || (currentLanguage === "zh" ? "未披露" : "Unavailable")))}
        ${renderFact(t("year"), escapeHtml(paper.publication_year || (currentLanguage === "zh" ? "未披露" : "Unavailable")))}
        ${renderFact(t("doi"), escapeHtml(paper.doi || (currentLanguage === "zh" ? "未披露" : "Unavailable")))}
      </div>
      <section class="brief-section abstract-only">
        <h4>${escapeHtml(t("abstract"))}</h4>
        ${abstractMarkup}
      </section>
      <section class="brief-section compact">
        <h4>${escapeHtml(t("keywords"))}</h4>
        <div class="key-tags">
          ${(paper.keywords || [])
            .slice(0, 10)
            .map((item) => `<span class="key-tag">${escapeHtml(item)}</span>`)
            .join("")}
        </div>
      </section>
      <p class="paper-link">
        ${escapeHtml(t("original"))}：
        ${paper.primary_link ? `<a href="${paper.primary_link}" target="_blank" rel="noreferrer">${escapeHtml(t("details"))}</a>` : ""}
        ${paper.pdf_link ? ` | <a href="${paper.pdf_link}" target="_blank" rel="noreferrer">${escapeHtml(t("pdf"))}</a>` : ""}
      </p>
    </article>
  `;
}

function renderRecommendations(items = []) {
  if (!items.length) {
    return `<div class="empty-state visible"><p>${escapeHtml(t("noRecommendations"))}</p></div>`;
  }
  return items
    .map((paper) => {
      const citationLabel = paper.citation_count != null ? t("citations", paper.citation_count) : t("noRecommendationsCitations");
      const link = paper.primary_link || paper.pdf_link || "";
      const categoryLabel = translateCategoryLabel(paper.research_category || paper.topic_label || "综合生物医学");
      return `
        <article class="recommendation-card visible">
          <div class="recommendation-head">
            <span class="recommendation-count">${escapeHtml(citationLabel)}</span>
            <span class="paper-tag">${escapeHtml(categoryLabel)}</span>
          </div>
          <h3>${escapeHtml(paper.title || "Untitled paper")}</h3>
          <p class="recommendation-meta">${escapeHtml(t("recommendationSource"))}: ${escapeHtml(paper.journal_or_server || paper.source || "-")}</p>
          <p class="recommendation-meta">${escapeHtml(t("recommendationCategory"))}: ${escapeHtml(categoryLabel || "-")}</p>
          ${link ? `<a class="recommendation-link" href="${link}" target="_blank" rel="noreferrer">${escapeHtml(t("recommendationLink"))}</a>` : ""}
        </article>
      `;
    })
    .join("");
}

function renderPagination(page, pageCount) {
  if (!pageCount || pageCount <= 1) {
    return "";
  }

  const pages = [];
  for (let value = 1; value <= pageCount; value += 1) {
    pages.push(value);
  }

  return `
    <div class="pagination-bar">
      <button class="page-btn" type="button" data-page="${page - 1}" ${page <= 1 ? "disabled" : ""}>${escapeHtml(t("prevPage"))}</button>
      <div class="page-numbers">
        ${pages
          .map(
            (value) => `
            <button class="page-btn ${value === page ? "active" : ""}" type="button" data-page="${value}">
              ${value}
            </button>
          `
          )
          .join("")}
      </div>
      <button class="page-btn" type="button" data-page="${page + 1}" ${page >= pageCount ? "disabled" : ""}>${escapeHtml(t("nextPage"))}</button>
    </div>
  `;
}

function renderSkeleton() {
  paperList.innerHTML = Array.from({ length: 3 }, () => `<div class="paper-card skeleton-card"></div>`).join("");
  paperCountNode.textContent = currentLanguage === "zh" ? "加载中" : "Loading";
  paginationNode.innerHTML = "";
  categoryStatsNode.innerHTML = Array.from({ length: 4 }, () => `<div class="skeleton-card"></div>`).join("");
  recommendedGrid.innerHTML = Array.from({ length: 3 }, () => `<div class="related-card skeleton-card"></div>`).join("");
  sourceStatsNode.innerHTML = Array.from({ length: 4 }, () => `<span class="source-stat skeleton-line"></span>`).join("");
}

function triggerReveal() {
  document.querySelectorAll(".reveal").forEach((node) => node.classList.add("visible"));
}

function applyLanguageChrome() {
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  document.title = t("documentTitle");
  navTitle.textContent = t("brand");
  navDigestLink.textContent = t("navDigest");
  navArchiveLink.textContent = t("navArchive");
  digestMetaBrand.textContent = t("metaBrand");
  if (!digestTitle.dataset.dynamic) {
    digestTitle.textContent = t("brand");
  }
  if (!digestSubtitle.dataset.dynamic) {
    digestSubtitle.textContent = t("mastheadFallback");
  }
  sourceStatsLabel.textContent = t("sourceStats");
  archiveLink.textContent = t("viewArchive");
  rangeSeparator.textContent = t("rangeTo");
  prevWeekButton.textContent = t("prevWeek");
  nextWeekButton.textContent = t("nextWeek");
  currentWeekButton.textContent = t("recentWeek");
  loadButton.textContent = t("loadRange");
  refreshButton.textContent = t("refreshRange");
  paperSectionTitle.textContent = t("paperList");
  categorySectionTitle.textContent = t("categoryStats");
  recommendationSectionTitle.textContent = t("recommendations");
  langZhButton.classList.toggle("active", currentLanguage === "zh");
  langEnButton.classList.toggle("active", currentLanguage === "en");
  navArchiveLink.href = `/archive?lang=${encodeURIComponent(currentLanguage)}`;
  archiveLink.href = `/archive?lang=${encodeURIComponent(currentLanguage)}`;
  renderDomains(availableDomains);
}

function renderDigest(payload) {
  const legacyItems = [...(payload.featured || []), ...(payload.notable || [])];
  const papers = payload.items && payload.items.length ? payload.items : legacyItems;
  const recommendations = payload.recommended && payload.recommended.length ? payload.recommended : buildRecommendations(papers);
  const hasModernPagination = typeof payload.page === "number" && typeof payload.total_pages === "number";
  if (Array.isArray(payload.selected_sources)) {
    selectedSources = new Set(payload.selected_sources.map((item) => normalizeSourceKey(item)).filter(Boolean));
  }

  currentPage = payload.page || 1;
  totalPages = hasModernPagination ? payload.total_pages || 0 : 0;

  digestTitle.textContent = currentLanguage === "zh" ? "论文速递" : "Paper Bullet";
  digestTitle.dataset.dynamic = "true";
  digestSubtitle.textContent = localizedDigestSubtitle(payload);
  digestSubtitle.dataset.dynamic = "true";
  digestMetaDate.textContent = localizedPeriodLabel(payload.period_label || payload.date || "-");
  sourceStatsNode.innerHTML = renderSourceStats(payload.source_stats || []);
  paperCountNode.textContent = hasModernPagination
    ? t("currentCountModern", payload.total_papers || papers.length || 0, papers.length)
    : t("currentCountLegacy", payload.total_papers || papers.length || 0, papers.length, payload.total_pages || 0);

  if (!papers.length) {
    const emptyLabel = selectedSources.size ? t("sourceEmptyAfterFilter") : t("currentPageEmpty");
    paperList.innerHTML = renderEmptyState(emptyLabel);
    paginationNode.innerHTML = "";
    categoryStatsNode.innerHTML = `<div class="empty-state visible"><p>${escapeHtml(t("noCategoryStats"))}</p></div>`;
    recommendedGrid.innerHTML = renderRecommendations([]);
    if (!(payload.source_stats || []).length) {
      sourceStatsNode.innerHTML = `<span class="source-stat empty">${escapeHtml(t("noSourceStats"))}</span>`;
    }
    updateLocation();
    return;
  }

  paperList.innerHTML = papers.map((paper, index) => renderPaperCard(paper, index)).join("");
  paginationNode.innerHTML = renderPagination(currentPage, totalPages);
  categoryStatsNode.innerHTML = renderCategoryStats(payload.category_stats || []);
  recommendedGrid.innerHTML = renderRecommendations(recommendations);
  updateLocation();
  triggerReveal();
}

async function loadDomains() {
  const response = await fetch("/api/domains");
  const payload = await response.json();
  renderDomains(payload.domains || []);
}

async function loadDigest(page = currentPage) {
  if (!validateDateRange()) {
    return;
  }
  const requestId = ++activeRequestId;
  currentPage = Math.max(1, page);
  updateLocation();
  renderSkeleton();
  setStatus(t("loadingDigest"));
  setBusy(true);
  try {
    const response = await fetch(
      `/api/digest?domain=${encodeURIComponent(selectedDomain)}&date_from=${encodeURIComponent(dateFromInput.value)}&date_to=${encodeURIComponent(dateToInput.value)}&page=${encodeURIComponent(currentPage)}&page_size=${encodeURIComponent(PAGE_SIZE)}${selectedSources.size ? `&sources=${encodeURIComponent([...selectedSources].join(","))}` : ""}`
    );
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Load failed");
    }
    if (requestId !== activeRequestId) {
      return;
    }
    let displayPayload = payload;
    if (!("items" in payload) && payload.total_papers) {
      setStatus(t("loadingLegacy"));
      displayPayload = await hydrateLegacyPaginationPayload(payload);
    }
    renderDigest(displayPayload);
    if (!("items" in payload) && displayPayload.total_pages) {
      setStatus(t("legacyDone", displayPayload.page, displayPayload.total_pages));
      return;
    }
    setStatus(t("readingDone", displayPayload.page || 1, displayPayload.total_pages || 1));
  } catch (error) {
    setStatus(error.message || "Load failed", true);
  } finally {
    if (requestId === activeRequestId) {
      setBusy(false);
    }
  }
}

async function refreshDigest() {
  if (!validateRefreshRange()) {
    return;
  }
  const requestId = ++activeRequestId;
  currentPage = 1;
  updateLocation();
  renderSkeleton();
  const chunks = buildRefreshChunks();
  if (chunks.length > 1) {
    setStatus(t("refreshRangeTooLarge", selectedRangeDays()));
  } else {
    setStatus(t("loadingRefresh"));
  }
  setBusy(true);
  try {
    for (let index = 0; index < chunks.length; index += 1) {
      const chunk = chunks[index];
      if (requestId !== activeRequestId) {
        return;
      }
      setStatus(
        chunks.length > 1
          ? t("loadingRefreshChunk", index + 1, chunks.length, chunk.from, chunk.to)
          : t("loadingRefresh")
      );
      const response = await fetch("/api/digest/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: selectedDomain,
          date_from: chunk.from,
          date_to: chunk.to,
          limit: 18,
          page: 1,
          page_size: PAGE_SIZE,
          sources: [...selectedSources],
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Refresh failed");
      }
    }
    if (requestId !== activeRequestId) {
      return;
    }
    const response = await fetch(
      `/api/digest?domain=${encodeURIComponent(selectedDomain)}&date_from=${encodeURIComponent(dateFromInput.value)}&date_to=${encodeURIComponent(dateToInput.value)}&page=1&page_size=${encodeURIComponent(PAGE_SIZE)}${selectedSources.size ? `&sources=${encodeURIComponent([...selectedSources].join(","))}` : ""}`
    );
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Load failed");
    }
    let displayPayload = payload;
    if (!("items" in payload) && payload.total_papers) {
      setStatus(t("loadingRefreshLegacy"));
      displayPayload = await hydrateLegacyPaginationPayload(payload);
    }
    renderDigest(displayPayload);
    setStatus(t("refreshDone", displayPayload.total_papers || 0));
  } catch (error) {
    setStatus(error.message || "Refresh failed", true);
  } finally {
    if (requestId === activeRequestId) {
      setBusy(false);
    }
  }
}

function shiftWeek(deltaWeeks) {
  const currentStart = new Date(`${dateFromInput.value}T00:00:00`);
  const currentEnd = new Date(`${dateToInput.value}T00:00:00`);
  currentStart.setDate(currentStart.getDate() + deltaWeeks * 7);
  currentEnd.setDate(currentEnd.getDate() + deltaWeeks * 7);
  dateFromInput.value = toIsoDate(currentStart);
  dateToInput.value = toIsoDate(currentEnd);
  currentPage = 1;
  loadDigest(1);
}

function switchLanguage(language) {
  currentLanguage = resolveLanguage(language);
  localStorage.setItem("paper_bullet_lang", currentLanguage);
  applyLanguageChrome();
  updateLocation();
  loadDigest(currentPage);
}

loadButton.addEventListener("click", () => {
  currentPage = 1;
  loadDigest(1);
});

refreshButton.addEventListener("click", refreshDigest);
prevWeekButton.addEventListener("click", () => shiftWeek(-1));
nextWeekButton.addEventListener("click", () => shiftWeek(1));
currentWeekButton.addEventListener("click", () => {
  setWeekRange(new Date(`${today}T00:00:00`));
  currentPage = 1;
  loadDigest(1);
});

paperList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-empty-action]");
  if (!button) {
    return;
  }
  if (button.dataset.emptyAction === "clear-sources") {
    selectedSources = new Set();
  }
  if (button.dataset.emptyAction === "recent-week") {
    setWeekRange(new Date(`${today}T00:00:00`));
  }
  currentPage = 1;
  loadDigest(1);
});

dateFromInput.addEventListener("change", () => {
  markRangeChanged();
});

dateToInput.addEventListener("change", () => {
  markRangeChanged();
});

paginationNode.addEventListener("click", (event) => {
  const button = event.target.closest(".page-btn");
  if (!button || button.disabled) {
    return;
  }
  const targetPage = Number.parseInt(button.dataset.page || "1", 10);
  if (!Number.isNaN(targetPage) && targetPage >= 1 && targetPage <= totalPages && targetPage !== currentPage) {
    loadDigest(targetPage);
  }
});

sourceStatsNode.addEventListener("click", (event) => {
  const button = event.target.closest(".source-filter");
  if (!button) {
    return;
  }
  const key = button.dataset.sourceKey || "";
  if (key === "all") {
    selectedSources = new Set();
  } else if (SOURCE_LABELS[key]) {
    const next = new Set(selectedSources);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    selectedSources = next;
  }
  currentPage = 1;
  loadDigest(1);
});

domainTabsNode.addEventListener("click", (event) => {
  const button = event.target.closest(".domain-tab");
  if (!button || button.dataset.domain === selectedDomain) {
    return;
  }
  selectedDomain = button.dataset.domain || "biomed_all";
  selectedSources = new Set();
  currentPage = 1;
  renderDomains(availableDomains);
  loadDigest(1);
});

langZhButton.addEventListener("click", () => switchLanguage("zh"));
langEnButton.addEventListener("click", () => switchLanguage("en"));

applyLanguageChrome();
dateFromInput.max = today;
dateToInput.max = today;
setStatus(t("ready"));
loadDomains().then(() => loadDigest(currentPage)).catch(() => setStatus(t("initFail"), true));
