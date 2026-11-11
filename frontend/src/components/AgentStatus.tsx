import type { DiagnosisStage } from '../types';

interface Props {
  stage: DiagnosisStage;
  statusMessage: string;
}

const AGENTS = [
  {
    id: 'house',
    name: 'Dr. House',
    role: '野性假说生成',
    avatar: '🩺',
    thinkingStage: 'house_thinking' as DiagnosisStage,
    doneStage: 'house_done' as DiagnosisStage,
  },
  {
    id: 'cameron',
    name: 'Cameron',
    role: '循证检索',
    avatar: '🔬',
    thinkingStage: 'cameron_thinking' as DiagnosisStage,
    doneStage: 'cameron_done' as DiagnosisStage,
  },
  {
    id: 'cuddy',
    name: 'Dr. Cuddy',
    role: 'CES 证伪仲裁',
    avatar: '⚖️',
    thinkingStage: 'cuddy_thinking' as DiagnosisStage,
    doneStage: 'cuddy_done' as DiagnosisStage,
  },
];

type AgentState = 'idle' | 'thinking' | 'done';

function getAgentState(agentId: string, stage: DiagnosisStage): AgentState {
  const stageOrder = ['idle', 'house_thinking', 'house_done', 'cameron_thinking', 'cameron_done', 'cuddy_thinking', 'cuddy_done', 'complete'];
  const currentIdx = stageOrder.indexOf(stage);

  if (agentId === 'house') {
    if (currentIdx === 1) return 'thinking';
    if (currentIdx >= 2) return 'done';
  } else if (agentId === 'cameron') {
    if (currentIdx === 3) return 'thinking';
    if (currentIdx >= 4) return 'done';
  } else if (agentId === 'cuddy') {
    if (currentIdx === 5) return 'thinking';
    if (currentIdx >= 6) return 'done';
  }
  return 'idle';
}

export default function AgentStatus({ stage, statusMessage }: Props) {
  if (stage === 'idle') return null;

  return (
    <div style={{
      background: 'rgba(14,25,41,0.95)',
      border: '1px solid #1e2a3a',
      borderRadius: 10,
      padding: '14px 16px',
      marginBottom: 16,
      animation: 'slide-in-up 0.3s ease',
    }}>
      {/* Agent 进度条 */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        {AGENTS.map(agent => {
          const state = getAgentState(agent.id, stage);
          return (
            <div key={agent.id} style={{
              flex: 1,
              padding: '10px 12px',
              borderRadius: 8,
              border: `1px solid ${
                state === 'thinking' ? 'rgba(14,165,233,0.5)' :
                state === 'done' ? 'rgba(16,185,129,0.4)' :
                '#1e2a3a'
              }`,
              background: state === 'thinking' ? 'rgba(14,165,233,0.08)' :
                          state === 'done' ? 'rgba(16,185,129,0.06)' :
                          'rgba(20,25,33,0.5)',
              transition: 'all 0.3s ease',
              boxShadow: state === 'thinking' ? '0 0 12px rgba(14,165,233,0.3)' : 'none',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: 18 }}>{agent.avatar}</span>
                <div>
                  <div style={{
                    fontSize: 12, fontWeight: 600,
                    color: state === 'done' ? '#34d399' :
                           state === 'thinking' ? '#7dd3fc' : '#475569',
                  }}>{agent.name}</div>
                  <div style={{ fontSize: 10, color: '#475569' }}>{agent.role}</div>
                </div>
                {state === 'thinking' && (
                  <div style={{ marginLeft: 'auto', display: 'flex', gap: 3 }}>
                    {[0, 1, 2].map(i => (
                      <div key={i} style={{
                        width: 5, height: 5, borderRadius: '50%',
                        background: '#0ea5e9',
                        animation: `typing-dot 1.2s ${i * 0.2}s infinite`,
                      }} />
                    ))}
                  </div>
                )}
                {state === 'done' && (
                  <span style={{ marginLeft: 'auto', color: '#10b981', fontSize: 14 }}>✓</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* 当前状态消息 */}
      {statusMessage && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '8px 10px',
          background: 'rgba(14,165,233,0.06)',
          borderRadius: 6,
          border: '1px solid rgba(14,165,233,0.15)',
        }}>
          <div style={{
            width: 14, height: 14, borderRadius: '50%',
            border: '2px solid #0ea5e9',
            borderTopColor: 'transparent',
            animation: 'spin 0.8s linear infinite',
            flexShrink: 0,
          }} />
          <span style={{ fontSize: 12, color: '#7dd3fc' }}>{statusMessage}</span>
        </div>
      )}
    </div>
  );
}
