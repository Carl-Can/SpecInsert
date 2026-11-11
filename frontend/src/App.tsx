import { useState, useEffect, useRef } from 'react';
import './App.css';
import type { Scenario, DiagnosisState, HouseOutput, CameronOutput, CuddyOutput } from './types';
import { fetchScenarios, streamDiagnose, checkHealth } from './api';
import Sidebar from './components/Sidebar';
import Whiteboard from './components/Whiteboard';

const INITIAL_STATE: DiagnosisState = {
  stage: 'idle',
  house: null,
  cameron: null,
  cuddy: null,
  statusMessage: '',
  error: null,
};

export default function App() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(null);
  const [caseInput, setCaseInput] = useState('');
  const [diagState, setDiagState] = useState<DiagnosisState>(INITIAL_STATE);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'ok' | 'error'>('checking');
  const [llmConfigured, setLlmConfigured] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 检查后端健康状态
  useEffect(() => {
    checkHealth()
      .then(h => {
        setBackendStatus('ok');
        setLlmConfigured(h.llm_configured);
      })
      .catch(() => setBackendStatus('error'));
  }, []);

  // 加载剧本列表
  useEffect(() => {
    if (backendStatus === 'ok') {
      fetchScenarios()
        .then(data => setScenarios(data.scenarios ?? []))
        .catch(console.error);
    }
  }, [backendStatus]);

  // 选择预置剧本
  const handleSelectScenario = (s: Scenario) => {
    setActiveScenario(s);
    setCaseInput(s.input);
    setDiagState(INITIAL_STATE);
  };

  // 新建自由推演
  const handleNewCase = () => {
    setActiveScenario(null);
    setCaseInput('');
    setDiagState(INITIAL_STATE);
    setTimeout(() => textareaRef.current?.focus(), 100);
  };

  // 启动三智能体诊断
  const handleDiagnose = async () => {
    if (!caseInput.trim()) return;
    if (diagState.stage !== 'idle' && diagState.stage !== 'complete' && diagState.stage !== 'error') return;

    setDiagState({ ...INITIAL_STATE, stage: 'house_thinking', statusMessage: '正在启动诊断流水线...' });

    try {
      await streamDiagnose(
        {
          case_input: caseInput,
          scenario_id: activeScenario?.id ?? 'custom',
        },
        (event) => {
          const { stage, message, data } = event as {
            stage: string;
            message?: string;
            data?: Record<string, unknown>;
          };

          setDiagState(prev => {
            const next = { ...prev, stage: stage as DiagnosisState['stage'] };

            if (message) next.statusMessage = message;

            if (stage === 'house_done' && data) {
              next.house = data as unknown as HouseOutput;
            } else if (stage === 'cameron_done' && data) {
              next.cameron = data as unknown as CameronOutput;
            } else if (stage === 'cuddy_done' && data) {
              next.cuddy = data as unknown as CuddyOutput;
            } else if (stage === 'complete' && data) {
              const full = data as { house?: HouseOutput; cameron?: CameronOutput; cuddy?: CuddyOutput };
              if (full.house) next.house = full.house;
              if (full.cameron) next.cameron = full.cameron;
              if (full.cuddy) next.cuddy = full.cuddy;
              next.statusMessage = '✅ 诊断完成';
            } else if (stage === 'error') {
              next.error = message ?? '未知错误';
              next.statusMessage = `❌ 错误: ${message}`;
            }

            return next;
          });
        }
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setDiagState(prev => ({
        ...prev,
        stage: 'error',
        error: msg,
        statusMessage: `❌ ${msg}`,
      }));
    }
  };

  const isRunning = !['idle', 'complete', 'error'].includes(diagState.stage);
  const canDiagnose = caseInput.trim().length > 0 && !isRunning && backendStatus === 'ok';

  return (
    <div style={{ display: 'flex', height: '100vh', flexDirection: 'column', overflow: 'hidden' }}>
      {/* 顶部状态栏 */}
      <header style={{
        height: 40,
        background: 'rgba(10,13,18,0.98)',
        borderBottom: '1px solid #1e2a3a',
        display: 'flex',
        alignItems: 'center',
        padding: '0 16px',
        gap: 12,
        flexShrink: 0,
        zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 14 }}>🧬</span>
          <span style={{ fontSize: 12, fontWeight: 700, color: '#0ea5e9' }}>Bio-House</span>
          <span style={{ fontSize: 11, color: '#374151' }}>赛博豪斯 · 生物医药机理侦探</span>
        </div>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, alignItems: 'center' }}>
          {/* 后端状态 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10 }}>
            <div style={{
              width: 6, height: 6, borderRadius: '50%',
              background: backendStatus === 'ok' ? '#10b981' : backendStatus === 'error' ? '#ef4444' : '#f59e0b',
              animation: backendStatus === 'checking' ? 'pulse-glow 1s infinite' : undefined,
            }} />
            <span style={{ color: '#475569' }}>
              {backendStatus === 'ok' ? '后端在线' : backendStatus === 'error' ? '后端离线' : '连接中...'}
            </span>
          </div>

          {/* LLM 状态 */}
          {backendStatus === 'ok' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10 }}>
              <div style={{
                width: 6, height: 6, borderRadius: '50%',
                background: llmConfigured ? '#10b981' : '#f59e0b',
              }} />
              <span style={{ color: '#475569' }}>
                {llmConfigured ? 'LLM 已配置' : 'LLM 未配置'}
              </span>
            </div>
          )}

          {backendStatus === 'error' && (
            <span style={{ fontSize: 10, color: '#6b7280' }}>
              请确保后端在 localhost:8000 运行
            </span>
          )}
        </div>
      </header>

      {/* 主体区 */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* 侧边栏 */}
        <Sidebar
          scenarios={scenarios}
          activeId={activeScenario?.id ?? null}
          onSelect={handleSelectScenario}
          onNewCase={handleNewCase}
        />

        {/* 右侧主舞台 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* 白板区域 */}
          <Whiteboard state={diagState} />

          {/* 底部输入区 */}
          <div style={{
            padding: '12px 16px',
            borderTop: '1px solid #1e2a3a',
            background: 'rgba(10,13,18,0.98)',
            flexShrink: 0,
          }}>
            {/* 错误提示 */}
            {diagState.error && (
              <div style={{
                marginBottom: 8, padding: '8px 12px',
                background: 'rgba(239,68,68,0.08)',
                border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: 8, fontSize: 12, color: '#fca5a5',
              }}>
                ❌ {diagState.error}
              </div>
            )}

            <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
              <textarea
                ref={textareaRef}
                value={caseInput}
                onChange={e => setCaseInput(e.target.value)}
                placeholder="输入离奇化验指标、补剂列表或生物医药疑案...&#10;例如：某患者服用 X+Y+Z 后出现以下症状..."
                rows={3}
                style={{
                  flex: 1,
                  background: 'rgba(20,25,33,0.9)',
                  border: '1px solid #1e2a3a',
                  borderRadius: 10,
                  color: '#e2e8f0',
                  fontSize: 13,
                  padding: '10px 14px',
                  resize: 'vertical',
                  fontFamily: 'Inter, sans-serif',
                  outline: 'none',
                  lineHeight: 1.6,
                  minHeight: 72,
                  maxHeight: 160,
                  transition: 'border-color 0.2s',
                }}
                onFocus={e => { e.target.style.borderColor = 'rgba(14,165,233,0.5)'; }}
                onBlur={e => { e.target.style.borderColor = '#1e2a3a'; }}
                onKeyDown={e => {
                  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    if (canDiagnose) handleDiagnose();
                  }
                }}
              />
              <button
                onClick={handleDiagnose}
                disabled={!canDiagnose}
                style={{
                  padding: '10px 20px',
                  background: canDiagnose
                    ? 'linear-gradient(135deg, #0ea5e9, #0284c7)'
                    : 'rgba(30,42,58,0.8)',
                  border: `1px solid ${canDiagnose ? 'rgba(14,165,233,0.5)' : '#1e2a3a'}`,
                  borderRadius: 10,
                  color: canDiagnose ? '#fff' : '#374151',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: canDiagnose ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s ease',
                  whiteSpace: 'nowrap',
                  boxShadow: canDiagnose ? '0 0 12px rgba(14,165,233,0.3)' : 'none',
                  height: 72,
                  minWidth: 100,
                  display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center', gap: 4,
                }}
              >
                {isRunning ? (
                  <>
                    <div style={{
                      width: 16, height: 16, borderRadius: '50%',
                      border: '2px solid rgba(255,255,255,0.3)',
                      borderTopColor: '#fff',
                      animation: 'spin 0.8s linear infinite',
                    }} />
                    <span style={{ fontSize: 11 }}>推理中...</span>
                  </>
                ) : (
                  <>
                    <span style={{ fontSize: 18 }}>⏎</span>
                    <span>启动会诊</span>
                  </>
                )}
              </button>
            </div>
            <p style={{ fontSize: 10, color: '#374151', marginTop: 6, textAlign: 'right' }}>
              Ctrl+Enter 快捷启动 · 三智能体对抗推理 · CES 双侧证伪
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
