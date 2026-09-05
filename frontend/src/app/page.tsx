'use client';

import React, { useState, useEffect, useRef } from 'react';
import MermaidViewer from '@/components/MermaidViewer';
import Logo from '@/components/Logo';
import {
  Play,
  Key,
  Layers,
  ShieldAlert,
  Activity,
  Terminal,
  Zap,
  Bot,
  BookOpen,
  Lightbulb,
  GitBranch,
  CheckCircle2,
  Sparkles,
  Settings,
  ChevronUp,
  X,
  ArrowLeft,
  ArrowUpRight,
  Sliders,
  Check,
  Loader2,
} from 'lucide-react';
import { AGENT_EXPLANATIONS } from '@/data/agentExplanations';

interface ModuleInfo {
  id: string;
  title: string;
  description: string;
  mermaid: string;
}

interface Metrics {
  model?: string;
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_write_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
  call_count: number;
}

export default function Home() {
  const [apiKey, setApiKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('claude-4-5-haiku');
  const [modules, setModules] = useState<ModuleInfo[]>([]);
  const [selectedModuleId, setSelectedModuleId] = useState('module_01');
  const [inputText, setInputText] = useState('Build an AI-powered code analysis tool');
  const [langSmithKey, setLangSmithKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [wakingUp, setWakingUp] = useState(false);
  const [wakeError, setWakeError] = useState('');

  useEffect(() => {
    if (sessionStorage.getItem('labSessionStarted') === 'true') {
      setSessionStarted(true);
    }
  }, []);

  const handleStartSession = async () => {
    setWakingUp(true);
    setWakeError('');
    try {
      const maxRetries = 35; // 70 seconds max
      let retries = 0;
      while (retries < maxRetries) {
        try {
          const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' });
          if (res.ok) {
            setSessionStarted(true);
            sessionStorage.setItem('labSessionStarted', 'true');
            break;
          }
        } catch (e) {
          // keep polling
        }
        retries++;
        await new Promise(r => setTimeout(r, 2000));
      }
      if (retries >= maxRetries) {
        setWakeError('Failed to wake up the backend. Please check your internet or try again.');
      }
    } finally {
      setWakingUp(false);
    }
  };

  const [settingsOpen, setSettingsOpen] = useState(false);
  const settingsPanelRef = useRef<HTMLDivElement>(null);
  const [sessionId, setSessionId] = useState<string>('');

  // Load from localStorage on mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem('anthropicApiKey');
    if (savedApiKey) setApiKey(savedApiKey);

    let currentSessionId = '';
    try {
      currentSessionId = sessionStorage.getItem('sessionId') || '';
      if (!currentSessionId) {
        currentSessionId = typeof crypto !== 'undefined' && crypto.randomUUID 
          ? crypto.randomUUID() 
          : 'sess_' + Math.random().toString(36).substring(2, 15);
        sessionStorage.setItem('sessionId', currentSessionId);
      }
    } catch (e) {
      currentSessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
    }
    setSessionId(currentSessionId);

    const savedLangSmithKey = localStorage.getItem('langSmithKey');
    if (savedLangSmithKey) setLangSmithKey(savedLangSmithKey);

    const savedModel = localStorage.getItem('selectedModel');
    if (savedModel) setSelectedModel(savedModel);
  }, []);

  // Save to localStorage when values change
  useEffect(() => {
    localStorage.setItem('anthropicApiKey', apiKey);
  }, [apiKey]);

  useEffect(() => {
    localStorage.setItem('langSmithKey', langSmithKey);
  }, [langSmithKey]);

  useEffect(() => {
    localStorage.setItem('selectedModel', selectedModel);
  }, [selectedModel]);

  const [resultData, setResultData] = useState<any>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [requiresApproval, setRequiresApproval] = useState(false);

  const samplePrompts: Record<string, string> = {
    module_01: 'How do state graphs work in LangGraph?',
    module_02: 'Solve this equation: 3x + 15 = 45',
    module_03: 'What is the current weather in San Francisco and calculate 25 * 4',
    module_03b: 'Research quantum computing and write a summary Python script',
    module_04: 'Hi, my name is Alex and I love building agentic AI applications',
    module_05: 'DROP DATABASE production_users_v2;',
    module_06: 'Process multi-stage pipeline data',
    module_07: 'Design a web scraping tool and write the python script',
    module_08: 'LangGraph allows building stateful multi-agent systems with cyclic execution graph architectures.',
    module_09: 'Write a brief technical explanation of LLM guardrails',
    module_09b: 'Chunk 1: Intro to LLMs; Chunk 2: Graph Execution; Chunk 3: Multi-agent Teams',
    module_10: 'Run dataset evaluations across test benchmark samples',
    module_11: 'Explain streaming architecture in real-time LLM agents',
    module_12: 'Fetch user settings for current enterprise organization tenant',
  };

  const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

  useEffect(() => {
    fetch(`${API_BASE}/api/modules`)
      .then((res) => {
        if (!res.ok) throw new Error('API returned ' + res.status);
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setModules(data);
        } else {
          console.error('Invalid modules data format:', data);
          setModules([]);
        }
      })
      .catch((err) => console.error('Failed to fetch modules:', err));
  }, []);

  const handleModuleSelect = (id: string) => {
    setSelectedModuleId(id);
    setInputText(samplePrompts[id] || 'Test prompt');
    setResultData(null);
    setMetrics(null);
    setRequiresApproval(false);
  };

  const runModule = async (approvedOverride?: boolean) => {
    setLoading(true);
    setResultData(null);
    try {
      const res = await fetch(`${API_BASE}/api/run_module`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_id: selectedModuleId,
          input_text: inputText,
          api_key: apiKey,
          langsmith_key: langSmithKey,
          model_name: selectedModel,
          is_approved: approvedOverride ?? false,
          user_id: sessionId,
          thread_id: `${sessionId}_${selectedModuleId}`,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Backend execution failed');
      }

      setResultData(data.result);
      setMetrics(data.metrics);
      setRequiresApproval(data.requires_approval || false);
    } catch (err: any) {
      setResultData({ error: err.message || 'Execution failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleApproveHITL = async (approved: boolean) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/approve_hitl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_id: selectedModuleId,
          input_text: inputText,
          api_key: apiKey,
          langsmith_key: langSmithKey,
          model_name: selectedModel,
          is_approved: approved,
          user_id: sessionId,
          thread_id: `${sessionId}_${selectedModuleId}`,
        }),
      });
      const data = await res.json();
      setResultData(data.result);
      setMetrics(data.metrics);
      setRequiresApproval(false);
    } catch (err: any) {
      setResultData({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const selectedModule = modules?.find((m) => m.id === selectedModuleId);

  // Dynamic API key label based on selected model
  const isGroq = selectedModel.includes('llama') || selectedModel.includes('mixtral') || selectedModel.includes('qwen');
  const isGemini = selectedModel.includes('gemini');
  const providerName = isGroq ? 'Groq' : isGemini ? 'Gemini' : 'Anthropic';
  const apiPlaceholder = isGroq ? 'gsk_...' : isGemini ? 'AIzaSy...' : 'sk-ant-api03-...';

  if (!sessionStarted) {
    return (
      <div className="splash-layout">
        <div className="splash-container">
          <div className="splash-header">
            <div style={{ display: 'inline-flex', padding: 12, background: 'rgba(5, 14, 242, 0.08)', borderRadius: 20, marginBottom: 24, border: '1px solid rgba(5, 14, 242, 0.2)' }}>
              <Bot size={40} color="var(--accent)" />
            </div>
            <h1 style={{ fontSize: 36, fontFamily: 'var(--font-display)', marginBottom: 12 }}>LangGraph Interactive Lab</h1>
            <p style={{ fontSize: 16, color: 'var(--text-dim)', maxWidth: 500, margin: '0 auto', lineHeight: 1.6 }}>
              Explore, test, and trace 14 different autonomous agent architectures. This interactive playground lets you see exactly how state flows, tools are executed, and LLMs reason in real-time.
            </p>
          </div>
          
          <div className="splash-features" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, textAlign: 'left', marginTop: 32, marginBottom: 40 }}>
            <div className="card-static" style={{ padding: 20, background: 'var(--bg-panel)' }}>
              <Layers size={18} color="var(--accent)" style={{ marginBottom: 12 }} />
              <h3 style={{ fontSize: 16, marginBottom: 8 }}>14 Architectures</h3>
              <p style={{ fontSize: 13, color: 'var(--text-faint)' }}>From simple prompt chains to multi-agent swarms and ReAct execution loops.</p>
            </div>
            <div className="card-static" style={{ padding: 20, background: 'var(--bg-panel)' }}>
              <Activity size={18} color="var(--accent)" style={{ marginBottom: 12 }} />
              <h3 style={{ fontSize: 16, marginBottom: 8 }}>Live Execution</h3>
              <p style={{ fontSize: 13, color: 'var(--text-faint)' }}>Watch graph state mutations and tool invocations happen step-by-step.</p>
            </div>
          </div>

          {wakeError && (
            <div style={{ color: 'var(--danger)', fontSize: 14, marginBottom: 16, padding: '12px 16px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <ShieldAlert size={16} style={{ display: 'inline', marginRight: 8, verticalAlign: 'text-bottom' }} />
              {wakeError}
            </div>
          )}

          <button 
            onClick={handleStartSession} 
            disabled={wakingUp}
            className="btn btn-primary" 
            style={{ width: '100%', padding: '16px', fontSize: 16, borderRadius: 12, height: 'auto', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 10, boxShadow: '0 8px 24px rgba(5, 14, 242, 0.3)' }}
          >
            {wakingUp ? (
              <>
                <Loader2 size={20} className="spin" />
                Waking up agentic backend... (Render cold start ~50s)
              </>
            ) : (
              <>
                Initialize Lab Session <ArrowUpRight size={18} />
              </>
            )}
          </button>
          
          <div style={{ marginTop: 24, fontSize: 12, color: 'var(--text-faint)' }}>
            Note: The backend is hosted on a free Render instance and goes to sleep after inactivity. It takes about a minute to spin back up!
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-layout">
      {/* ═══════════════ FULL WIDTH GLASS HEADER ═══════════════ */}
      <header className="site-nav">
        <div className="site-nav-inner">
          <div className="nav-left">
            <a href="https://www.chandrakethan.com" className="brand-logo" aria-label="Portfolio Home">
              <Logo size={28} color="var(--accent)" />
            </a>
            <div className="brand-breadcrumbs">
              <span className="brand-product">LangGraph Agent Architectures</span>
              <span className="brand-badge">Interactive Labs</span>
            </div>
          </div>

          {/* nav-center removed per user request */}          <div className="nav-right">
            {/* Engine Status Chip replacing the green dots */}
            <div
              className={`engine-status-badge ${apiKey ? 'configured' : 'unconfigured'}`}
              onClick={() => setSettingsOpen(true)}
              role="button"
              tabIndex={0}
            >
              <span className={`status-pulse-dot ${apiKey ? 'active' : 'demo'}`} />
              <span className="engine-model-name">
                {selectedModel.includes('sonnet') ? 'Claude 3.5 Sonnet' : 
                 selectedModel.includes('haiku') ? 'Claude 3.5 Haiku' : 
                 selectedModel.includes('qwen') ? 'Qwen 3.8 27B' : 
                 selectedModel.includes('gemini') ? 'Gemini 1.5' : providerName}
              </span>
              <span className="engine-status-tag">{apiKey ? 'Ready' : 'Demo Mode'}</span>
            </div>

            {/* Settings Toggle */}
            <button
              onClick={() => setSettingsOpen(!settingsOpen)}
              className={`btn ${settingsOpen ? 'btn-primary' : 'btn-ghost'}`}
              style={{ padding: '8px 16px', gap: 6 }}
            >
              {settingsOpen ? <X size={14} /> : <Sliders size={14} />}
              <span>{settingsOpen ? 'Close' : 'Configure'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* ═══════════════ SETTINGS DROPDOWN PANEL ═══════════════ */}
      {settingsOpen && (
        <div className="settings-panel-wrapper" ref={settingsPanelRef}>
          <div className="settings-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Settings size={16} style={{ color: 'var(--accent)' }} />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text)' }}>
                  API Configuration
                </span>
              </div>
              <button
                onClick={() => setSettingsOpen(false)}
                className="btn btn-ghost"
                style={{ padding: '6px 10px', borderRadius: 12 }}
                aria-label="Close settings"
              >
                <X size={14} />
              </button>
            </div>

            <div className="settings-grid">
              {/* Model Selector */}
              <div className="settings-field">
                <label className="settings-field-label">
                  <Bot size={13} /> Model
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="select-glass"
                  style={{ width: '100%' }}
                >
                  <option value="claude-5-sonnet">Claude 5 Sonnet</option>
                  <option value="claude-4-5-haiku">Claude 4.5 Haiku</option>
                  <option value="claude-5-opus">Claude 5 Opus</option>
                  <option value="qwen/qwen3.8-27b">Qwen 3.8 27B (Groq - Free)</option>
                  <option value="gemini-1.5-flash">Gemini 1.5 Flash (Free)</option>
                </select>
              </div>

              {/* Dynamic API Key */}
              <div className="settings-field">
                <label className="settings-field-label">
                  <Key size={13} /> {providerName} API Key
                </label>
                <input
                  type="password"
                  placeholder={apiPlaceholder}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="input-glass"
                  style={{ width: '100%' }}
                />
              </div>

              {/* LangSmith Key */}
              <div className="settings-field">
                <label className="settings-field-label">
                  <Key size={13} /> LangSmith Key <span style={{ fontWeight: 400, color: 'var(--text-faint)', textTransform: 'none', letterSpacing: 'normal' }}>(optional)</span>
                </label>
                <input
                  type="password"
                  placeholder="lsv2_pt_..."
                  value={langSmithKey}
                  onChange={(e) => setLangSmithKey(e.target.value)}
                  className="input-glass"
                  style={{ width: '100%' }}
                />
              </div>
            </div>

            <p style={{ marginTop: 16, fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-faint)', letterSpacing: '0.02em' }}>
              Keys are saved in browser localStorage and never sent to any server other than the APIs above.
            </p>
          </div>
        </div>
      )}

      {/* ═══════════════ MAIN BODY ═══════════════ */}
      <div className="app-body">
        {/* ── Sidebar: Module Navigation ── */}
        <aside className="sidebar">
          <div className="sidebar-label">
            Modules & Agent Architectures
          </div>
          <div className="sidebar-list">
            {modules.map((m) => {
              const isSelected = m.id === selectedModuleId;
              return (
                <button
                  key={m.id}
                  onClick={() => handleModuleSelect(m.id)}
                  className={`module-card ${isSelected ? 'active' : ''}`}
                >
                  <div className="module-card-title">
                    <span>{m.title}</span>
                    {isSelected && <Zap size={13} style={{ color: 'var(--accent)' }} />}
                  </div>
                  <div className="module-card-desc">{m.description}</div>
                </button>
              );
            })}
          </div>
        </aside>

        {/* ── Main Workspace ── */}
        <main className="main-workspace">
          {selectedModule && (
            <div className="workspace-stack">
              {/* Module Header Card */}
              <div className="card-static">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                  <h2 style={{ fontSize: 28 }}>{selectedModule.title}</h2>
                  <span className="badge" style={{ fontFamily: 'var(--font-mono)' }}>
                    {selectedModule.id}
                  </span>
                </div>
                <p style={{ fontSize: 15 }}>{selectedModule.description}</p>
              </div>

              {/* Interactive Mermaid Graph Diagram */}
              <div>
                <div className="section-label">
                  <Layers size={14} /> Compiled Graph Architecture
                </div>
                <MermaidViewer chart={selectedModule.mermaid} />
              </div>

              {/* Prompt Input Form */}
              <div className="card-static">
                <div className="section-label">
                  <Terminal size={14} /> Test Execution Input
                </div>
                <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Enter query or prompt for agent..."
                    className="input-glass"
                    style={{ flex: 1 }}
                  />
                  <button
                    onClick={() => runModule()}
                    disabled={loading}
                    className="btn btn-primary"
                    style={{ flexShrink: 0 }}
                  >
                    <Play size={14} />
                    <span>{loading ? 'Executing...' : 'Run Agent Graph'}</span>
                  </button>
                </div>
              </div>

              {/* ── HITL Approval Banner ── */}
              {requiresApproval && (
                <div className="hitl-banner">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12, paddingLeft: 12 }}>
                    <ShieldAlert size={20} style={{ color: 'var(--warning)' }} />
                    <h4 style={{ fontFamily: 'var(--font-display)', fontSize: 20, color: 'var(--text)' }}>
                      Human Guardrail Triggered
                    </h4>
                  </div>
                  <p style={{ fontSize: 14, color: 'var(--text-dim)', marginBottom: 16, paddingLeft: 12 }}>
                    Execution has reached an <code style={{ background: 'var(--surface-2)', padding: '2px 6px', borderRadius: 6, fontSize: 12 }}>interrupt_before</code> breakpoint. Approve or reject this action:
                  </p>
                  <div style={{ display: 'flex', gap: 12, paddingLeft: 12 }}>
                    <button
                      onClick={() => handleApproveHITL(true)}
                      className="btn btn-success"
                    >
                      <CheckCircle2 size={14} /> Approve & Continue
                    </button>
                    <button
                      onClick={() => handleApproveHITL(false)}
                      className="btn btn-danger"
                    >
                      Reject & Abort
                    </button>
                  </div>
                </div>
              )}

              {/* ── Execution Results & Inspector ── */}
              {resultData && (
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
                  {/* State & Step Trace */}
                  <div className="card-static">
                    <div className="section-label">
                      <Activity size={14} /> Graph State & Step Trace
                    </div>

                    {/* Step Trace Logs */}
                    {resultData.execution_steps && (
                      <div style={{ marginBottom: 16 }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                          Node Execution Timeline:
                        </span>
                        <div className="code-surface" style={{ marginTop: 8, maxHeight: 200, overflowY: 'auto' }}>
                          <div className="step-trace">
                            {resultData.execution_steps.map((step: string, idx: number) => (
                              <div key={idx} className="step-trace-item">
                                <span className="step-trace-idx">[{idx + 1}]</span>
                                <span className="step-trace-content">{step}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Raw State JSON */}
                    <div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                        Final Returned State JSON:
                      </span>
                      <pre className="code-surface" style={{ marginTop: 8, maxHeight: 320, overflowY: 'auto' }}>
                        {JSON.stringify(resultData, null, 2)}
                      </pre>
                    </div>
                  </div>

                  {/* Execution & Token Metrics Widget */}
                  <div className="card-static" style={{ height: 'fit-content' }}>
                    <div className="section-label">
                      <Activity size={14} /> Execution & Token Metrics
                    </div>

                    {metrics ? (
                      <div style={{ marginTop: 8 }}>
                        <div className="metric-row">
                          <span className="metric-label">Model</span>
                          <span className="metric-value accent">{metrics.model || selectedModel}</span>
                        </div>
                        <div className="metric-row">
                          <span className="metric-label">Input Tokens</span>
                          <span className="metric-value">{metrics.input_tokens.toLocaleString()}</span>
                        </div>
                        <div className="metric-row">
                          <span className="metric-label">Output Tokens</span>
                          <span className="metric-value">{metrics.output_tokens.toLocaleString()}</span>
                        </div>
                        <div className="metric-row">
                          <span className="metric-label">Cache Read</span>
                          <span className="metric-value">{metrics.cache_read_tokens.toLocaleString()}</span>
                        </div>
                        <div className="metric-row">
                          <span className="metric-label">LLM API Calls</span>
                          <span className="metric-value">{metrics.call_count}</span>
                        </div>
                      </div>
                    ) : (
                      <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-faint)', fontStyle: 'italic', marginTop: 8 }}>
                        No LLM API calls recorded for this step.
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* ── Architecture Deep Dive ── */}
              {AGENT_EXPLANATIONS[selectedModuleId] && (() => {
                const info = AGENT_EXPLANATIONS[selectedModuleId];
                return (
                  <div className="card-static">
                    {/* Header */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: 20, borderBottom: '1px solid var(--border)', marginBottom: 20 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                        <div style={{ padding: 10, background: 'rgba(5, 14, 242, 0.06)', border: '1px solid var(--accent-dim)', borderRadius: 16, color: 'var(--accent)' }}>
                          <BookOpen size={20} />
                        </div>
                        <div>
                          <h3 style={{ fontSize: 18, fontFamily: 'var(--font-display)' }}>
                            Architecture Deep Dive: {info.title}
                          </h3>
                          <p style={{ fontSize: 12, color: 'var(--text-faint)', marginTop: 2 }}>
                            Clear conceptual breakdown and production intuition for this agent design.
                          </p>
                        </div>
                      </div>
                      <span className="tag">{info.badge}</span>
                    </div>

                    {/* Deep Dive Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                      {/* What It Is */}
                      <div className="deep-dive-card">
                        <div className="deep-dive-label" style={{ color: 'var(--accent)' }}>
                          <Sparkles size={13} /> What It Is
                        </div>
                        <p className="deep-dive-text">{info.whatItIs}</p>
                      </div>

                      {/* Real-World Analogy */}
                      <div className="deep-dive-card">
                        <div className="deep-dive-label" style={{ color: '#d97706' }}>
                          <Lightbulb size={13} /> Real-World Analogy
                        </div>
                        <p className="deep-dive-text">{info.analogy}</p>
                      </div>

                      {/* How It Works */}
                      <div className="deep-dive-card">
                        <div className="deep-dive-label" style={{ color: '#0284c7' }}>
                          <GitBranch size={13} /> How It Works in LangGraph
                        </div>
                        <p className="deep-dive-text">{info.howItWorks}</p>
                      </div>

                      {/* When to Use */}
                      <div className="deep-dive-card">
                        <div className="deep-dive-label" style={{ color: 'var(--success)' }}>
                          <CheckCircle2 size={13} /> When to Use in Production
                        </div>
                        <p className="deep-dive-text">{info.whenToUse}</p>
                      </div>
                    </div>

                    {/* Key Concepts Tags */}
                    <div className="concept-tags" style={{ marginTop: 16 }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-faint)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Core Concepts:</span>
                      {info.keyConcepts.map((concept: string, idx: number) => (
                        <span key={idx} className="concept-tag">
                          {concept}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </main>
      </div>

      {/* ═══════════════ FOOTER ═══════════════ */}
      <footer className="site-footer">
        <div style={{ maxWidth: 'var(--max-w)', margin: '0 auto', padding: '0 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <p>
            Designed & Built by Chandra Kethan <span style={{ margin: '0 10px', color: 'var(--border)' }}>|</span> LangGraph Mastery Platform
          </p>
          <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
            <a
              href="https://github.com/chandrakethan27/langgraph-agent-architectures"
              target="_blank"
              rel="noopener noreferrer"
              style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', transition: 'color 0.2s' }}
            >
              GitHub
            </a>
            <a
              href="https://linkedin.com/in/chandrakethan-sivarathri/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', transition: 'color 0.2s' }}
            >
              LinkedIn
            </a>
            <a
              href="https://www.youtube.com/@iamchandrakethan27"
              target="_blank"
              rel="noopener noreferrer"
              style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', transition: 'color 0.2s' }}
            >
              YouTube
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
