# Biomed Research Brief

一个面向生物医学 AI 的日报式论文简报站，支持：

- 生医领域切换与日期切换
- 多源抓取：arXiv / bioRxiv / medRxiv / PubMed
- 提取作者、机构、基金、期刊或预印本来源等基础信息
- 自动生成中文短标题、重点摘要、创新点和今日观察
- 日报首页与历史归档页

## 启动

```bash
copy .env.example .env
python run.py
```

浏览器打开：

`http://127.0.0.1:8000`

## 环境变量

- `OPENAI_API_KEY`: 可选，不填则使用规则摘要
- `OPENAI_MODEL`: 默认 `gpt-4o-mini`
- `OPENAI_ENABLED`: 是否启用 LLM 摘要
- `CROSSREF_MAILTO`: 建议填写邮箱，使用 polite pool
- `DEFAULT_DOMAINS`: 定时任务默认抓取领域，逗号分隔
- `SCHEDULER_ENABLED`: 是否启用定时任务
- `SCHEDULER_HOUR`: 每日触发小时
- `SCHEDULER_MINUTE`: 每日触发分钟
- `COLLECT_MAX_RESULTS`: 单次抓取上限

## 当前领域预设

- `biomed_all`
- `drug_discovery`
- `medical_imaging`
- `clinical_ai`
- `genomics_omics`
- `protein_biomolecules`

## API

- `GET /api/domains` 获取领域配置
- `GET /api/digest?domain=biomed_all&date=2026-04-25` 获取日报
- `POST /api/digest/refresh` 手动抓取并重建日报
- `GET /api/archive?domain=biomed_all&limit=12` 获取归档卡片
- `GET /api/papers?...` 保留为调试接口

## 说明

- 多源抓取后会统一归一到同一份 paper schema，再生成日报结构。
- arXiv / bioRxiv / medRxiv 天然字段不完全一致，因此系统会尝试通过 DOI 或标题在 Crossref 中做补全。
- 基金、机构依赖元数据完整度，部分论文可能为空。
- 调度任务是进程内调度，适合原型与内网部署；正式生产建议使用系统级定时器或工作流平台。
- 如果想启用更强摘要能力，可手动安装 `openai`。
