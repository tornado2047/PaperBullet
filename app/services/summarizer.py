from __future__ import annotations

import re
from typing import Any


class PaperSummarizer:
    CATEGORY_RULES = {
        "医学影像": [
            "imaging", "radiology", "mri", "ct", "ultrasound", "pathology", "histology",
            "microscopy", "x-ray", "retinal", "optical coherence tomography", "oct",
            "segmentation", "diagnostic imaging", "fundus",
        ],
        "临床与人群": [
            "clinical", "patient", "cohort", "trial", "ehr", "diagnosis", "treatment",
            "therapy", "outcome", "epidemiology", "screening", "hospital", "mortality",
            "prognosis", "survival", "randomized", "prospective", "retrospective",
        ],
        "基因组与多组学": [
            "genome", "genomic", "single-cell", "single cell", "transcriptomic",
            "transcriptome", "epigenomic", "epigenome", "omics", "sequencing",
            "proteomic", "multi-omics", "multiomics", "rna-seq", "chromatin",
        ],
        "蛋白质与分子": [
            "protein", "enzyme", "antibody", "peptide", "biomolecule", "structure",
            "folding", "ligand", "compound", "molecule", "molecular", "drug",
            "binder", "pharmacology", "medicinal chemistry",
        ],
        "细胞与机制": [
            "cell", "cellular", "signaling", "mechanism", "immune", "tumor", "cancer",
            "microglia", "metabolism", "inflammation", "pathogenesis", "stem cell",
            "microenvironment", "neuron", "synapse", "mitochondria",
        ],
        "工具与方法": [
            "method", "methods", "tool", "pipeline", "framework", "platform", "benchmark",
            "dataset", "atlas", "algorithm", "workflow", "protocol", "reconstruction",
            "quantification", "sensor", "sequencer",
        ],
    }

    JOURNAL_BOOSTS = {
        "nature methods": {"工具与方法": 4},
        "nature biomedical engineering": {"医学影像": 1, "工具与方法": 1},
        "cell reports medicine": {"临床与人群": 2},
        "med": {"临床与人群": 2},
        "medrxiv": {"临床与人群": 2},
        "pubmed": {"临床与人群": 1},
    }

    STOPWORDS = {
        "a", "an", "and", "the", "of", "for", "to", "in", "on", "with", "by", "from", "using", "based",
        "study", "paper", "result", "results", "analysis", "approach", "method", "methods", "data", "new",
        "novel", "model", "models", "modeling", "ai", "artificial", "intelligence", "machine", "learning",
        "deep", "foundation", "framework", "system", "systems", "patient", "patients", "disease", "research",
        "state-of-the-art", "performance", "generalizability", "clinical", "medical", "biomedical",
    }

    def analyze_paper(self, paper: dict[str, Any], domain_label: str) -> dict[str, Any]:
        del domain_label
        title = (paper.get("title") or "").strip()
        abstract = (paper.get("abstract") or "").strip()
        cleaned_abstract = self._normalize_abstract(title, abstract, paper.get("authors", []))
        publication_year = self._extract_publication_year(paper.get("published_at"))
        research_category = self._infer_category(paper, title, cleaned_abstract)
        keywords = self._extract_keywords(paper, title, cleaned_abstract, paper.get("keywords", []), research_category)

        return {
            "short_title_cn": title,
            "summary_cn": cleaned_abstract,
            "summary": cleaned_abstract,
            "one_line_takeaway": cleaned_abstract[:220] if cleaned_abstract else "",
            "topic_label": research_category,
            "publication_year": publication_year,
            "citation_count": paper.get("citation_count"),
            "research_category": research_category,
            "research_type": "research_article",
            "brief_basis": "abstract" if cleaned_abstract else "title_only",
            "abstract_brief": cleaned_abstract,
            "introduction_brief": None,
            "methods_brief": None,
            "results_brief": None,
            "discussion_brief": None,
            "novelty_score": None,
            "strengths": [],
            "weaknesses": [],
            "innovations": [],
            "ranking_score": self._score_paper(paper, cleaned_abstract),
            "keywords": keywords,
        }

    def compose_digest(self, domain_label: str, papers: list[dict[str, Any]]) -> dict[str, Any]:
        journals = []
        for paper in papers:
            journal = paper.get("journal_or_server")
            if journal and journal not in journals:
                journals.append(journal)

        subtitle = f"本期共整理 {len(papers)} 篇生物医学研究文章，来源覆盖预印本、PubMed 与 Nature / Science / Cell 系列官方期刊。"
        if journals:
            subtitle += f" 当前样本包含 {'、'.join(journals[:5])}。"

        return {
            "title": "论文速递",
            "subtitle": subtitle,
            "overview": [],
            "observation": "",
        }

    def _extract_publication_year(self, published_at: str | None) -> int | None:
        if not published_at:
            return None
        match = re.search(r"(\d{4})", str(published_at))
        return int(match.group(1)) if match else None

    def _infer_category(self, paper: dict[str, Any], title: str, abstract: str) -> str:
        title_lower = title.lower()
        abstract_lower = abstract.lower()
        journal = (paper.get("journal_or_server") or paper.get("source") or "").lower()
        scores = {category: 0 for category in self.CATEGORY_RULES}

        for category, tokens in self.CATEGORY_RULES.items():
            for token in tokens:
                if token in title_lower:
                    scores[category] += 3
                if token in abstract_lower:
                    scores[category] += 1
                for existing in paper.get("keywords", []) or []:
                    if token == str(existing).lower():
                        scores[category] += 2

        for journal_key, boosts in self.JOURNAL_BOOSTS.items():
            if journal_key in journal:
                for category, boost in boosts.items():
                    scores[category] += boost

        ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        best_category, best_score = ordered[0]
        second_score = ordered[1][1] if len(ordered) > 1 else 0

        if best_score <= 1:
            return "综合生物医学"
        if best_score == second_score and best_score < 4:
            return "综合生物医学"
        return best_category

    def _extract_keywords(self, paper: dict[str, Any], title: str, abstract: str, existing: list[str], research_category: str) -> list[str]:
        keyword_candidates = []
        combined = f"{title}. {abstract}".lower()
        for phrase in [
            "single-cell", "single cell", "multi-omics", "optical coherence tomography",
            "electronic health record", "triple-negative breast cancer", "phase 2 trial",
            "diffuse intrinsic pontine glioma", "protein structure", "drug discovery",
            "medical imaging", "radiotherapy", "transcriptome", "epigenomics", "brain connectivity",
            "lung cancer", "retinal diseases", "gene expression", "immune complexes",
        ]:
            if phrase in combined:
                keyword_candidates.append(phrase)

        journal = paper.get("journal_or_server")
        if journal:
            keyword_candidates.append(journal)

        for item in existing or []:
            if item:
                keyword_candidates.append(item)

        for token in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", combined):
            lowered = token.lower()
            if lowered in self.STOPWORDS:
                continue
            keyword_candidates.append(token)

        normalized = []
        for item in keyword_candidates:
            cleaned = " ".join(str(item).replace("_", " ").split())
            lowered = cleaned.lower()
            if not cleaned or lowered in self.STOPWORDS:
                continue
            if lowered in {"machine learning", "deep learning", "artificial intelligence", "foundation model", "ai"}:
                continue
            if cleaned not in normalized:
                normalized.append(cleaned)

        if research_category not in normalized:
            normalized.insert(0, research_category)
        return normalized[:10]

    def _normalize_abstract(self, title: str, abstract: str, authors: list[str] | None = None) -> str:
        del title
        if abstract:
            normalized = self._strip_metadata_prefixes(" ".join(abstract.split()))
            if normalized and not self._looks_like_author_list(normalized, authors or []):
                return normalized
        return ""

    def _strip_metadata_prefixes(self, value: str) -> str:
        cleaned = value
        patterns = [
            r"^author\(s\)\s*:\s*.+$",
            r"^authors?\s*:\s*.+$",
            r"^source\s*:\s*.+$",
            r"^published online\s*:\s*.+$",
        ]
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"\bAuthor\(s\)\s*:\s*.+$", "", cleaned, flags=re.IGNORECASE).strip()
        return cleaned

    def _looks_like_author_list(self, abstract: str, authors: list[str]) -> bool:
        text = abstract.strip()
        if not text:
            return False

        lower_text = text.lower()
        scientific_markers = [
            "background", "methods", "results", "conclusion", "conclusions", "objective", "objectives",
            "importance", "we ", "our ", "this study", "here we", "findings", "significance",
        ]
        if any(marker in lower_text for marker in scientific_markers):
            return False

        if re.search(r"[.;:!?]\s", text):
            return False

        name_like_chunks = [chunk.strip() for chunk in re.split(r",| and ", text) if chunk.strip()]
        if len(name_like_chunks) >= 4 and all(self._looks_like_person_name(chunk) for chunk in name_like_chunks[: min(len(name_like_chunks), 10)]):
            return True

        author_tokens = self._author_tokens(authors)
        if author_tokens:
            text_tokens = re.findall(r"[A-Za-z][A-Za-z'\-]+", lower_text)
            if text_tokens:
                overlap = sum(1 for token in text_tokens if token in author_tokens)
                overlap_ratio = overlap / max(len(text_tokens), 1)
                if overlap_ratio >= 0.6 and len(text_tokens) <= 40:
                    return True
        return False

    def _looks_like_person_name(self, chunk: str) -> bool:
        if not chunk or len(chunk) > 60:
            return False
        words = [word for word in re.split(r"\s+", chunk) if word]
        if not 2 <= len(words) <= 5:
            return False
        valid_words = 0
        for word in words:
            stripped = word.strip(".,")
            if re.fullmatch(r"[A-Z][a-zA-Z'\-]+", stripped) or re.fullmatch(r"[A-Z]\.?", stripped):
                valid_words += 1
        return valid_words == len(words)

    def _author_tokens(self, authors: list[str]) -> set[str]:
        tokens: set[str] = set()
        for author in authors:
            for token in re.findall(r"[A-Za-z][A-Za-z'\-]+", str(author).lower()):
                if len(token) > 1:
                    tokens.add(token)
        return tokens

    def _score_paper(self, paper: dict[str, Any], abstract: str) -> float:
        source_weights = {
            "nature_journal": 5.2,
            "science_journal": 5.0,
            "cell_press": 4.8,
            "pubmed": 3.2,
            "medrxiv": 2.2,
            "biorxiv": 2.0,
            "arxiv": 1.7,
        }
        score = source_weights.get(paper.get("source", ""), 1.0)
        score += min(len(abstract) / 900, 1.2)
        if paper.get("doi"):
            score += 0.2
        if paper.get("citation_count"):
            score += min((paper.get("citation_count") or 0) / 50, 0.8)
        return round(score, 3)
