from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv_file(BASE_DIR / ".env")


DOMAIN_PRESETS = {
    "biomed_all": {
        "label": "生物医学全景导览",
        "description": "面向生物医学相关最新研究文章的全量导览，覆盖方法、实验、分子、疾病、影像与多组学等方向",
        "theme_color": "#49606a",
        "journal_keywords": [
            "biomedical",
            "medicine",
            "medical",
            "clinical",
            "patient",
            "disease",
            "therapy",
            "drug",
            "protein",
            "genome",
            "genomic",
            "cell",
            "single-cell",
            "imaging",
            "pathology",
            "biomarker",
            "tumor",
            "cancer",
            "immune",
            "neuron",
            "gene",
            "rna",
            "dna",
            "transcript",
            "retina",
            "brain",
            "neural",
            "cardio",
            "metabolism",
            "microbi",
            "lung",
            "liver",
            "kidney",
            "stem cell",
            "cellular",
            "molecular",
            "therapy",
            "therapeutic",
            "diagnostic",
            "pathogenesis",
            "mechanism",
        ],
        "source_queries": {
            "arxiv": '((cat:q-bio.BM OR cat:q-bio.CB OR cat:q-bio.GN OR cat:q-bio.MN OR cat:q-bio.NC OR cat:q-bio.OT OR cat:q-bio.PE OR cat:q-bio.QM OR cat:q-bio.SC OR cat:q-bio.TO OR cat:physics.bio-ph) OR ((cat:cs.CV OR cat:eess.IV) AND (all:medical OR all:biomedical OR all:clinical OR all:imaging OR all:pathology)))',
            "biorxiv_categories": ["bioinformatics", "genomics", "systems biology", "synthetic biology", "biophysics", "biochemistry", "cell biology", "molecular biology", "neuroscience", "immunology"],
            "biorxiv_keywords": ["protein", "genome", "genomic", "drug", "clinical", "biomedical", "single-cell", "transcriptomic", "antibody", "pathology", "imaging", "biomarker", "omics", "therapy", "tumor", "molecular", "cell", "disease", "mechanism"],
            "medrxiv_keywords": ["clinical", "medical", "diagnosis", "imaging", "patient", "disease", "biomarker", "screening", "radiology", "therapy", "trial", "cohort", "treatment", "epidemiology", "outcome"],
            "pubmed": '("biomedical"[Title/Abstract] OR "medical"[Title/Abstract] OR "clinical"[Title/Abstract] OR "patient"[Title/Abstract] OR "disease"[Title/Abstract] OR "therapy"[Title/Abstract] OR "treatment"[Title/Abstract] OR "protein"[Title/Abstract] OR "genome"[Title/Abstract] OR "genomic"[Title/Abstract] OR "cell"[Title/Abstract] OR "molecular"[Title/Abstract] OR "imaging"[Title/Abstract] OR "pathology"[Title/Abstract] OR "biomarker"[Title/Abstract] OR "single-cell"[Title/Abstract])',
        },
    },
}

_BASE_BIOMED_QUERIES = DOMAIN_PRESETS["biomed_all"]["source_queries"]

DOMAIN_PRESETS.update(
    {
        "drug_discovery": {
            "label": "药物发现与分子设计",
            "description": "聚焦药物发现、分子生成、靶点发现、结合预测、治疗策略与药理研究",
            "theme_color": "#6a5049",
            "journal_keywords": [
                "drug",
                "molecule",
                "molecular",
                "ligand",
                "compound",
                "binding",
                "therapeutic",
                "therapy",
                "target",
                "screening",
                "pharmacology",
                "inhibitor",
                "antibody",
                "protein",
                "enzyme",
            ],
            "source_queries": {
                **_BASE_BIOMED_QUERIES,
                "arxiv": '((cat:q-bio.BM OR cat:q-bio.QM OR cat:q-bio.MN OR cat:physics.chem-ph OR cat:cs.LG) AND (all:drug OR all:molecule OR all:ligand OR all:binding OR all:therapeutic OR all:protein OR all:screening))',
                "biorxiv_categories": ["biochemistry", "biophysics", "bioinformatics", "systems biology", "synthetic biology"],
                "biorxiv_keywords": ["drug", "molecule", "ligand", "compound", "binding", "therapeutic", "target", "screening", "protein", "enzyme", "antibody", "inhibitor"],
                "medrxiv_keywords": ["drug", "therapy", "therapeutic", "treatment", "trial", "dose", "pharmacology", "clinical"],
                "pubmed": '("drug discovery"[Title/Abstract] OR "molecular design"[Title/Abstract] OR ligand[Title/Abstract] OR compound[Title/Abstract] OR inhibitor[Title/Abstract] OR therapeutic[Title/Abstract] OR pharmacology[Title/Abstract] OR "target discovery"[Title/Abstract])',
            },
        },
        "medical_imaging": {
            "label": "医学影像",
            "description": "聚焦放射影像、病理图像、显微成像、分割诊断、多模态影像与影像 AI",
            "theme_color": "#475f74",
            "journal_keywords": [
                "imaging",
                "image",
                "radiology",
                "mri",
                "ct",
                "x-ray",
                "ultrasound",
                "pathology",
                "microscopy",
                "segmentation",
                "diagnosis",
                "retina",
            ],
            "source_queries": {
                **_BASE_BIOMED_QUERIES,
                "arxiv": '((cat:cs.CV OR cat:eess.IV OR cat:q-bio.QM) AND (all:medical OR all:clinical OR all:radiology OR all:pathology OR all:imaging OR all:MRI OR all:CT OR all:segmentation))',
                "biorxiv_categories": ["bioinformatics", "biophysics", "neuroscience", "cell biology"],
                "biorxiv_keywords": ["imaging", "image", "microscopy", "pathology", "segmentation", "retina", "spatial", "histology"],
                "medrxiv_keywords": ["imaging", "radiology", "mri", "ct", "x-ray", "ultrasound", "pathology", "segmentation", "diagnosis"],
                "pubmed": '("medical imaging"[Title/Abstract] OR radiology[Title/Abstract] OR MRI[Title/Abstract] OR CT[Title/Abstract] OR ultrasound[Title/Abstract] OR pathology[Title/Abstract] OR segmentation[Title/Abstract] OR "image analysis"[Title/Abstract])',
            },
        },
        "clinical_ai": {
            "label": "临床与医疗语言模型",
            "description": "聚焦临床 AI、医疗语言模型、电子病历、决策支持、真实世界研究与人群健康",
            "theme_color": "#536b5b",
            "journal_keywords": [
                "clinical",
                "patient",
                "hospital",
                "diagnosis",
                "prognosis",
                "ehr",
                "electronic health record",
                "language model",
                "llm",
                "cohort",
                "trial",
                "outcome",
            ],
            "source_queries": {
                **_BASE_BIOMED_QUERIES,
                "arxiv": '((cat:cs.CL OR cat:cs.AI OR cat:cs.LG OR cat:stat.ML) AND (all:clinical OR all:medical OR all:patient OR all:healthcare OR all:EHR OR all:"language model" OR all:LLM OR all:diagnosis))',
                "biorxiv_categories": ["bioinformatics", "systems biology", "neuroscience"],
                "biorxiv_keywords": ["clinical", "patient", "diagnosis", "prognosis", "language model", "llm", "healthcare", "cohort"],
                "medrxiv_keywords": ["clinical", "patient", "diagnosis", "prognosis", "ehr", "language model", "llm", "cohort", "trial", "outcome"],
                "pubmed": '("clinical AI"[Title/Abstract] OR "medical AI"[Title/Abstract] OR "language model"[Title/Abstract] OR LLM[Title/Abstract] OR "electronic health record"[Title/Abstract] OR diagnosis[Title/Abstract] OR prognosis[Title/Abstract] OR "clinical decision support"[Title/Abstract])',
            },
        },
        "genomics_omics": {
            "label": "基因组学与多组学",
            "description": "聚焦基因组、转录组、单细胞、多组学、空间组学、遗传变异与系统生物学",
            "theme_color": "#5d6375",
            "journal_keywords": [
                "genome",
                "genomic",
                "gene",
                "rna",
                "dna",
                "transcript",
                "single-cell",
                "omics",
                "proteomic",
                "metabolomic",
                "spatial",
                "variant",
                "genetics",
            ],
            "source_queries": {
                **_BASE_BIOMED_QUERIES,
                "arxiv": '((cat:q-bio.GN OR cat:q-bio.QM OR cat:q-bio.MN OR cat:q-bio.CB OR cat:stat.ML) AND (all:genome OR all:genomic OR all:single-cell OR all:transcriptomic OR all:omics OR all:variant OR all:spatial))',
                "biorxiv_categories": ["genomics", "bioinformatics", "systems biology", "molecular biology", "cell biology"],
                "biorxiv_keywords": ["genome", "genomic", "gene", "rna", "transcriptomic", "single-cell", "omics", "spatial", "variant", "genetics", "proteomic"],
                "medrxiv_keywords": ["genome", "genomic", "variant", "genetics", "biomarker", "omics", "cohort"],
                "pubmed": '("genomics"[Title/Abstract] OR genome[Title/Abstract] OR transcriptome[Title/Abstract] OR "single-cell"[Title/Abstract] OR multi-omics[Title/Abstract] OR proteomics[Title/Abstract] OR metabolomics[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR variant[Title/Abstract])',
            },
        },
        "protein_biomolecules": {
            "label": "蛋白质、酶与生物分子设计",
            "description": "聚焦蛋白质结构、酶工程、抗体、核酸、生物分子设计与结构预测",
            "theme_color": "#665c46",
            "journal_keywords": [
                "protein",
                "enzyme",
                "antibody",
                "peptide",
                "biomolecule",
                "structure",
                "folding",
                "binder",
                "rna",
                "nucleic acid",
                "design",
            ],
            "source_queries": {
                **_BASE_BIOMED_QUERIES,
                "arxiv": '((cat:q-bio.BM OR cat:q-bio.MN OR cat:q-bio.QM OR cat:physics.bio-ph OR cat:cs.LG) AND (all:protein OR all:enzyme OR all:antibody OR all:peptide OR all:structure OR all:folding OR all:binder OR all:biomolecule))',
                "biorxiv_categories": ["biochemistry", "biophysics", "synthetic biology", "molecular biology", "bioinformatics"],
                "biorxiv_keywords": ["protein", "enzyme", "antibody", "peptide", "structure", "folding", "binder", "biomolecule", "rna", "nucleic acid", "design"],
                "medrxiv_keywords": ["protein", "antibody", "biomarker", "therapy", "immune"],
                "pubmed": '("protein design"[Title/Abstract] OR protein[Title/Abstract] OR enzyme[Title/Abstract] OR antibody[Title/Abstract] OR peptide[Title/Abstract] OR "structure prediction"[Title/Abstract] OR biomolecule[Title/Abstract] OR binder[Title/Abstract])',
            },
        },
    }
)


OFFICIAL_JOURNAL_FEEDS = [
    {
        "source": "nature_journal",
        "journal": "Nature",
        "publisher": "Springer Nature",
        "feed_url": "https://www.nature.com/nature.rss",
        "strict_keyword_match": False,
    },
    {
        "source": "nature_journal",
        "journal": "Nature Medicine",
        "publisher": "Springer Nature",
        "feed_url": "https://www.nature.com/nm.rss",
        "strict_keyword_match": False,
    },
    {
        "source": "nature_journal",
        "journal": "Nature Biotechnology",
        "publisher": "Springer Nature",
        "feed_url": "https://www.nature.com/nbt.rss",
        "strict_keyword_match": False,
    },
    {
        "source": "nature_journal",
        "journal": "Nature Methods",
        "publisher": "Springer Nature",
        "feed_url": "https://www.nature.com/nmeth.rss",
        "strict_keyword_match": False,
    },
    {
        "source": "nature_journal",
        "journal": "Nature Biomedical Engineering",
        "publisher": "Springer Nature",
        "feed_url": "https://www.nature.com/natbiomedeng.rss",
        "strict_keyword_match": False,
    },
    {
        "source": "science_journal",
        "journal": "Science",
        "publisher": "AAAS",
        "feed_url": "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
        "strict_keyword_match": False,
        "per_feed_limit": 8,
    },
    {
        "source": "science_journal",
        "journal": "Science",
        "publisher": "AAAS",
        "feed_url": "https://www.science.org/action/showFeed?type=axatoc&feed=rss&jc=science",
        "strict_keyword_match": False,
        "per_feed_limit": 8,
    },
    {
        "source": "cell_press",
        "journal": "Cell",
        "publisher": "Cell Press / ScienceDirect",
        "feed_url": "https://rss.sciencedirect.com/publication/science/00928674",
        "strict_keyword_match": False,
    },
    {
        "source": "cell_press",
        "journal": "Cell Reports Medicine",
        "publisher": "Cell Press / ScienceDirect",
        "feed_url": "https://rss.sciencedirect.com/publication/science/26663791",
        "strict_keyword_match": False,
    },
    {
        "source": "cell_press",
        "journal": "Med",
        "publisher": "Cell Press / ScienceDirect",
        "feed_url": "https://rss.sciencedirect.com/publication/science/26666340",
        "strict_keyword_match": False,
    },
]


@dataclass
class Settings:
    app_name: str = "生物医学论文简报"
    database_path: str = str(BASE_DIR / "data" / "papers.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    openai_enabled: bool = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
    crossref_mailto: str = os.getenv("CROSSREF_MAILTO", "").strip()
    default_domains: list[str] = None
    scheduler_enabled: bool = os.getenv("SCHEDULER_ENABLED", "false").lower() == "true"
    scheduler_hour: int = int(os.getenv("SCHEDULER_HOUR", "8"))
    scheduler_minute: int = int(os.getenv("SCHEDULER_MINUTE", "0"))
    collect_max_results: int = int(os.getenv("COLLECT_MAX_RESULTS", "24"))
    refresh_max_days: int = int(os.getenv("REFRESH_MAX_DAYS", "14"))

    def __post_init__(self) -> None:
        raw_domains = os.getenv("DEFAULT_DOMAINS", "biomed_all")
        self.default_domains = [value.strip() for value in raw_domains.split(",") if value.strip()]


settings = Settings()
