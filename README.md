# Bio-House

Educational sandbox for debating biomedical mechanisms. An unofficial homage to a television diagnostic-room dynamic — not an official tie-in, and not a medical device.

House proposes sharp hypotheses. Cameron checks them against a small library of curated teaching notes. Cuddy keeps a support set and a refute set, then throws out claims that do not hold. The UI is a live whiteboard fed by server-sent events.

The GitHub repository may keep the name SpecInsert. The product name in the docs and the UI is Bio-House.

[中文说明在英文之后。](#中文)

## What this is

- A local hackathon MVP: FastAPI + Uvicorn + SSE, and React 19 + TypeScript + Vite.
- Four preset pharma / biochem cases, plus a free-text case.
- One OpenAI-compatible chat model (DeepSeek, OpenAI, Qwen, or a local server).

## What this is not

- Not a diagnostic device. Do not use it for diagnosis, treatment, or dosing.
- Not a live retrieval system. There is no vector database, no PubMed client, and no GraphRAG. Preset cases load hand-written notes from `backend/knowledge_base.py`. A custom case gets at most three of those notes when keywords overlap, and none when they do not.
- Those notes are labeled illustrative / to-be-verified. A few point at well-known research directions (for example cereblon / IKZF work). They are not formatted or checked as real citations.
- `BIO_HOUSE_AGENTIC_RAG_PRD.md` is an aspirational sketch. The behavior that actually runs is this README plus `.kiro/specs/bio-house-mvp/`.

## License

[MIT](LICENSE). The `/.kiro` tree (specs, steering, hooks) is part of the project and is meant to stay visible.

## Run it locally

Requirements: Python 3.11+ (with the stdlib `venv` module; on Debian/Ubuntu that is the `python3-venv` package), Node.js 20+, and npm.

```bash
./start.sh
```

On a fresh clone the script will:

1. Copy `backend/.env.example` to `backend/.env` if needed (gitignored).
2. Copy `frontend/.env.example` to `frontend/.env` if needed (gitignored).
3. Stop, with a non-zero exit, if `LLM_API_KEY` is missing or still a placeholder. It does not print the key and it does not start the servers.
4. After you put a real key in `backend/.env` and run `./start.sh` again: create `backend/venv` if needed, `pip install -r backend/requirements.txt`, `npm install` in `frontend` if `node_modules` is missing, then start both processes.

Edit `backend/.env`:

```bash
LLM_API_KEY=your-real-key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

Other compatible endpoints:

| Provider | `LLM_BASE_URL` | `LLM_MODEL` example |
| --- | --- | --- |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Qwen compatible mode | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| Local server | your local `/v1` URL | that server's model id |

Do not point `LLM_BASE_URL` at this app's own port 8000. This app is the Bio-House API, not a model server.

Then open:

- UI: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

Manual start, after the venv and installs exist and the key is set:

```bash
cd backend && ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
cd frontend && npm run dev
```

## Point a public demo at a deployed API

This repository does not ship a live demo URL. No hosting account was configured here.

When you have one:

1. Deploy the backend with `LLM_API_KEY` set in the host's secret store, not in git.
2. Set `CORS_ORIGINS` to the frontend origin, for example `https://your-frontend.example`. A comma-separated list is allowed. `*` turns credentials off.
3. Build the frontend with `VITE_API_BASE_URL=https://your-api.example` (no trailing slash). See `frontend/.env.example`.

Until those two values are set, the UI keeps calling `http://localhost:8000`, and the API keeps allowing the local Vite origins.

## Preset cases

| Case | Mechanism the notes sketch |
| --- | --- |
| Stacked rapamycin, metformin, semaglutide | mTOR / AMPK / gastric-emptying overlap and lactate |
| Grapefruit juice and atorvastatin | Intestinal CYP3A4 inhibition and muscle toxicity |
| Ethanol for methanol | ADH competition so methanol is not metabolized to formate |
| Thalidomide | CRBN molecular-glue story: teratogenicity and myeloma substrates |

Numbers in the notes and in `.kiro/steering/hackathon-scenarios.md` are teaching sketches. They are not verified results.

## Kiro

`.kiro/` stays at the repository root.

- `specs/bio-house-mvp/` — requirements, design, and tasks. Update these when behavior changes.
- `steering/` — product boundaries, backend and frontend conventions, agent prompt rules, and the scenario notes.
- `hooks/` — session env check, Python syntax check, frontend `tsc`, agent-prompt consistency, and a spec-task summary. Commands are repo-relative and expect the workspace root as the working directory. They used to contain an absolute path with a trailing space; that is gone.

## Layout

```
SpecInsert/
├── LICENSE
├── README.md
├── start.sh
├── .kiro/
├── backend/
│   ├── main.py              # FastAPI, CORS, SSE
│   ├── agents.py            # House, Cameron, Cuddy
│   ├── knowledge_base.py    # preset cases + curated notes
│   ├── settings.py          # key check and CORS parsing
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── .env.example         # VITE_API_BASE_URL
    └── src/
```

`backend/venv/`, `backend/.env`, `frontend/.env`, and `frontend/node_modules/` are gitignored.

## Checks

```bash
cd backend && ./venv/bin/python -m unittest test_submission_readiness.py test_api.py
cd frontend && npx tsc --noEmit -p tsconfig.app.json && npm run build
```

`test_api.py` never calls a model. A placeholder key must produce HTTP 503 on `POST /api/diagnose/stream`.

## Disclaimer

Bio-House is an educational sandbox. It is not a medical device and must not be used for diagnosis, treatment, or dosing. House, Cameron, and Cuddy are an unofficial homage. No television logos or other trademarked show assets belong in this repo.

---

## 中文

Bio-House（赛博豪斯）是一个生物医药机理辩论沙盒，用来看三个角色如何提出假说、对照笔记、再把站不住的假说划掉。角色名是对电视剧诊断室的非官方致敬，不是官方授权，也不是医疗器械。

仓库名可以继续叫 SpecInsert。文档和界面里的产品名是 Bio-House。

### 实际做了什么

- 后端：Python、FastAPI、Uvicorn、SSE。
- 前端：React 19、TypeScript、Vite。
- 四个预置剧本，加上自由输入。
- 知识来自 `backend/knowledge_base.py` 里写好的教学笔记。自定义病例只做关键词重叠，最多三条；对不上就一条都不给。
- 笔记标成 illustrative / to-be-verified（示意、待核验）。不要把它们当成已核对的论文。

没有向量数据库，没有实时文献检索。`BIO_HOUSE_AGENTIC_RAG_PRD.md` 是设想稿，不能当成已实现的 RAG 平台。

### 启动

需要 Python 3.11+（Debian/Ubuntu 上还要安装 `python3-venv`）和 Node.js 20+。

```bash
./start.sh
```

第一次运行会复制 `.env.example`。如果 `LLM_API_KEY` 还是占位符，脚本会直接失败退出，不会启动服务，也不会把 key 打出来。把真实 key 写进 `backend/.env`（已被 gitignore）后再运行一次，脚本会创建虚拟环境并安装依赖。

界面：http://localhost:5173  
接口：http://localhost:8000  
接口文档：http://localhost:8000/docs

### 以后如果要放到公网

这次没有部署地址，因为没有可用的托管账号。后端设置 `CORS_ORIGINS` 为前端来源，前端构建时设置 `VITE_API_BASE_URL` 为 API 地址。不要把 key 提交进仓库，也不要编造一个能打开的演示链接。

### Kiro

`/.kiro` 保留在根目录：`specs/` 写需求和设计，`steering/` 写约定，`hooks/` 用仓库相对路径做语法检查和环境提醒。行为有变时，同步改 spec。

### 免责声明

本项目只用于教学演示，不能用于诊断、治疗或给药。界面里的同一句话会一直显示。
