<div align="center">

# 🧠 LangGraph Agent Architectures

### The Definitive Interactive Platform for Mastering AI Agent Design Patterns

[![GitHub stars](https://img.shields.io/github/stars/chandrakethan27/langgraph-agent-architectures?style=for-the-badge&logo=github&color=050ef2&labelColor=0f172a)](https://github.com/chandrakethan27/langgraph-agent-architectures/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/chandrakethan27/langgraph-agent-architectures?style=for-the-badge&logo=git&color=4f46e5&labelColor=0f172a)](https://github.com/chandrakethan27/langgraph-agent-architectures/network/members)
[![GitHub issues](https://img.shields.io/github/issues/chandrakethan27/langgraph-agent-architectures?style=for-the-badge&logo=github&color=ef4444&labelColor=0f172a)](https://github.com/chandrakethan27/langgraph-agent-architectures/issues)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge&logo=opensourceinitiative&labelColor=0f172a)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/chandrakethan27/langgraph-agent-architectures?style=for-the-badge&logo=git&color=22c55e&labelColor=0f172a)](https://github.com/chandrakethan27/langgraph-agent-architectures/commits)

<br />

**A comprehensive, production-grade interactive platform showcasing 14 core AI Agent Architectures**<br />
implemented using **LangGraph** · **LangChain** · **Claude** — paired with a modern **Next.js** glassmorphism UI.

<br />

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-🦜-1C3C3C?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![Anthropic Claude](https://img.shields.io/badge/Claude-Anthropic-D4A574?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)

<br />

[**🚀 Quick Start**](#-quick-start) · [**📖 Architecture Guide**](#-supported-agent-architectures) · [**🌐 Deploy**](#-deployment-guide) · [**🤝 Contributing**](#-contributing)

</div>

---

## ✨ Highlights

<table>
<tr>
<td width="50%">

### 🏗️ 14 Agent Architectures
From basic sequential chaining to hierarchical multi-agent orchestration — every major LangGraph pattern is implemented, visualized, and explained.

</td>
<td width="50%">

### 🎨 Apple Glassmorphism UI
A stunning frosted-glass interface with `backdrop-filter` blur, smooth hover animations, and the Electric Cobalt (`#050ef2`) accent system.

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Live Execution Engine
Run any architecture in real-time against Claude models. See step traces, token metrics, and raw state JSON — all from the browser.

</td>
<td width="50%">

### 📊 Built-in Observability
LangSmith integration, token-level cost tracking, execution step timelines, and compiled graph visualizations via Mermaid.js.

</td>
</tr>
</table>

---

## 🧠 Supported Agent Architectures

| # | Architecture | Description | Core Mechanics |
|:---:|---|---|---|
| **01** | **Sequential Chaining** | Linear prompt-to-prompt state graph | `StateGraph` · `START → Node 1 → Node 2 → END` |
| **02** | **Dynamic Intent Routing** | Automatic intent classification & expert branching | `conditional_edges` · specialized expert nodes |
| **03** | **ReAct Agent with Tools** | Autonomous reasoning and action loop | Tool binding · calculator · search · current time |
| **03b** | **Plan-and-Execute** | Multi-step cyclic planner with dynamic replanning | `Planner → Executor → Replanner` loop |
| **04** | **Memory Systems** | Short-term thread + long-term user facts | `MemorySaver` · thread checkpointers · user store |
| **05** | **Human-in-the-Loop** | Critical action breakpoints requiring human approval | `interrupt_before` · approval/rejection signals |
| **06** | **Time-Travel & History** | State snapshot traversal and checkpoint rewinding | `get_state_history` · state branching |
| **07** | **Hierarchical Multi-Agent** | Supervisor coordinating specialized workers | Supervisor → Researcher → Coder → Review |
| **08** | **Deep Agents (Sub-Graphs)** | Standalone compiled sub-graph within parent node | Modular sub-graphs · encapsulated state schemas |
| **09** | **Reflection & Correction** | Generator-Critic loop with iterative self-critique | Evaluation rubrics · self-correction loops |
| **09b** | **Parallel Map-Reduce** | Fan-out concurrent workers and synthesis | Parallel edges · `Annotated[..., operator.add]` |
| **10** | **Observability & Eval** | Automated LLM-as-a-judge dataset evaluation | Benchmark evaluation · LangSmith tracing |
| **11** | **Streaming Architecture** | Real-time token and state event streaming | `.stream()` mode · low-latency UI updates |
| **12** | **Context & Injection** | Runtime dependency and tenant configuration | `RunnableConfig` · configurable parameters |

---

## 🛠️ Tech Stack

<table>
<tr>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" height="40" alt="Python" />
<br><strong>Python</strong>
</td>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="40" height="40" alt="FastAPI" />
<br><strong>FastAPI</strong>
</td>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg" width="40" height="40" alt="Next.js" />
<br><strong>Next.js 16</strong>
</td>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" width="40" height="40" alt="TypeScript" />
<br><strong>TypeScript</strong>
</td>
<td align="center" width="96">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" width="40" height="40" alt="Tailwind" />
<br><strong>Tailwind</strong>
</td>
</tr>
</table>

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11+ · FastAPI · Uvicorn · LangGraph · LangChain · Anthropic Claude SDK · LangSmith |
| **Frontend** | Next.js 16 (Turbopack, TypeScript) · Tailwind CSS · Apple Glassmorphism Design System · Lucide React · Mermaid.js |
| **Fonts** | Instrument Serif · Inter · IBM Plex Mono |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **Anthropic API Key** ([get one here](https://console.anthropic.com/))
- **LangSmith API Key** (optional, for observability — [get one here](https://smith.langchain.com/))

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/chandrakethan27/langgraph-agent-architectures.git
cd langgraph-agent-architectures
```

### 2️⃣ Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --port 8000 --reload
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install

# Start the Next.js dev server
npm run dev
```

### 4️⃣ Open & Explore

Open [**http://localhost:3000**](http://localhost:3000) in your browser. Enter your API keys in the navigation bar and start running agent architectures! 🎉

---

## 📁 Project Structure

```
langgraph-agent-architectures/
├── backend/
│   ├── main.py                  # FastAPI app with /api/modules, /api/run_module, /api/approve_hitl
│   ├── config.py                # Configuration and model registry
│   ├── requirements.txt         # Python dependencies
│   ├── utils/                   # Shared utilities
│   └── modules/
│       ├── module_01_basics.py          # Sequential Chaining
│       ├── module_02_routing.py         # Dynamic Intent Routing
│       ├── module_03_react.py           # ReAct Agent with Tools
│       ├── module_03b_plan_execute.py   # Plan-and-Execute
│       ├── module_04_memory.py          # Memory Systems
│       ├── module_05_hitl.py            # Human-in-the-Loop
│       ├── module_06_timetravel.py      # Time-Travel & History
│       ├── module_07_multi_agent.py     # Hierarchical Multi-Agent
│       ├── module_08_subgraphs.py       # Deep Agents (Sub-Graphs)
│       ├── module_09_reflection.py      # Reflection & Correction
│       ├── module_09b_map_reduce.py     # Parallel Map-Reduce
│       ├── module_10_eval_langsmith.py  # Observability & Eval
│       ├── module_11_streaming.py       # Streaming Architecture
│       └── module_12_context.py         # Context & Injection
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout with Apple font stack
│   │   │   ├── globals.css      # Apple Glassmorphism design system
│   │   │   └── page.tsx         # Main interactive platform UI
│   │   ├── components/
│   │   │   └── MermaidViewer.tsx # Interactive graph visualization
│   │   └── data/
│   │       └── agentExplanations.ts  # Architecture deep-dive content
│   ├── package.json
│   └── next.config.ts
│
├── README.md
└── .gitignore
```

---

## 🔑 Environment Variables

API keys are supplied directly in the UI navigation bar and persist in browser `localStorage`. No `.env` file is required for basic usage.

| Variable | Where | Description |
|----------|-------|-------------|
| `ANTHROPIC_API_KEY` | Browser UI | Your Anthropic API key (`sk-ant-...`) |
| `LANGSMITH_API_KEY` | Browser UI | Optional LangSmith key for tracing (`lsv2_...`) |
| `NEXT_PUBLIC_API_URL` | Frontend `.env.local` | Backend URL (defaults to `http://localhost:8000`) |

---

## 📈 Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=chandrakethan27/langgraph-agent-architectures&type=Date)](https://star-history.com/#chandrakethan27/langgraph-agent-architectures&Date)

</div>

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m "feat: add amazing feature"
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Contribution Ideas

- 🆕 Add new agent architecture modules (e.g., Tool-Use Agents, Debate Agents)
- 🧪 Add unit tests for backend modules
- 🎨 Improve UI/UX animations and micro-interactions
- 📝 Improve documentation and add usage examples
- 🐛 Fix bugs and improve error handling

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [**LangGraph**](https://github.com/langchain-ai/langgraph) — The graph-based framework that makes agent architectures composable
- [**LangChain**](https://github.com/langchain-ai/langchain) — The foundational LLM orchestration library
- [**Anthropic Claude**](https://anthropic.com) — The AI models powering every agent execution
- [**LangSmith**](https://smith.langchain.com) — Observability and evaluation platform
- [**Next.js**](https://nextjs.org) — The React framework for the interactive frontend
- [**Mermaid.js**](https://mermaid.js.org) — Graph diagram rendering engine

---

<div align="center">

**Built with ❤️ by [Chandra Kethan](https://www.chandrakethan.com)**

[![GitHub](https://img.shields.io/badge/GitHub-chandrakethan27-181717?style=for-the-badge&logo=github)](https://github.com/chandrakethan27)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/chandrakethan-sivarathri/)
[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-FF0000?style=for-the-badge&logo=youtube)](https://www.youtube.com/@iamchandrakethan27)
[![Portfolio](https://img.shields.io/badge/Portfolio-chandrakethan.com-050ef2?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.chandrakethan.com)

<br />

If you found this project helpful, please consider giving it a ⭐

</div>
