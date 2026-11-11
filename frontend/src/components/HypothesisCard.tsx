import type { Hypothesis, CESAnalysis } from '../types';

interface Props {
  hypothesis: Hypothesis;
  cesAnalysis?: CESAnalysis;
  isAnimating?: boolean;
}

const verdictConfig = {
  CONFIRMED: { label: '✅ 已确认', color: '#10b981', glow: 'rgba(16,185,129,0.4)', bg: 'rgba(16,185,129,0.08)' },
  PROBABLE: { label: '⚠️ 高度可疑', color: '#f59e0b', glow: 'rgba(245,158,11,0.4)', bg: 'rgba(245,158,11,0.08)' },
  REFUTED: { label: '❌ 已证伪', color: '#ef4444', glow: 'rgba(239,68,68,0.4)', bg: 'rgba(239,68,68,0.06)' },
  INSUFFICIENT_EVIDENCE: { label: '🔍 证据不足', color: '#6366f1', glow: 'rgba(99,102,241,0.4)', bg: 'rgba(99,102,241,0.08)' },
};

export default function HypothesisCard({ hypothesis, cesAnalysis, isAnimating }: Props) {
  const verdict = cesAnalysis?.verdict;
  const config = verdict ? verdictConfig[verdict] : null;
  const isRefuted = verdict === 'REFUTED';
  const isConfirmed = verdict === 'CONFIRMED';
  const confidence = cesAnalysis?.updated_confidence ?? hypothesis.confidence;

  return (
    <div
      style={{
        background: config ? config.bg : 'rgba(20, 25, 33, 0.9)',
        border: `1px solid ${config ? config.color + '50' : '#1e2a3a'}`,
        borderRadius: 12,
        padding: '16px',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: config ? `0 0 15px ${config.glow}` : undefined,
        animation: isAnimating ? 'slide-in-up 0.4s ease forwards' : undefined,
        opacity: isRefuted ? 0.65 : 1,
        transition: 'all 0.4s ease',
        flexShrink: 0,
        width: 240,
      }}
    >
      {/* 确认假说绿光效果 */}
      {isConfirmed && (
        <div style={{
          position: 'absolute', inset: 0, borderRadius: 12,
          animation: 'glow-green 2s ease-in-out infinite',
          pointerEvents: 'none',
        }} />
      )}

      {/* 证伪红线划掉效果 */}
      {isRefuted && (
        <div style={{
          position: 'absolute', top: '50%', left: 0, right: 0,
          height: 2,
          background: 'linear-gradient(90deg, transparent, #ef4444, transparent)',
          animation: 'strike-through 0.6s ease forwards',
          zIndex: 10,
          pointerEvents: 'none',
        }} />
      )}

      {/* 假说 ID */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 11,
          color: '#0ea5e9',
          background: 'rgba(14,165,233,0.1)',
          padding: '2px 8px',
          borderRadius: 4,
          border: '1px solid rgba(14,165,233,0.2)',
        }}>{hypothesis.id}</span>
        {config && (
          <span style={{ fontSize: 11, color: config.color }}>{config.label}</span>
        )}
      </div>

      {/* 假说标题 */}
      <h3 style={{
        fontSize: 13,
        fontWeight: 600,
        color: isRefuted ? '#6b7280' : '#e2e8f0',
        marginBottom: 8,
        lineHeight: 1.4,
        textDecoration: isRefuted ? 'line-through' : 'none',
        textDecorationColor: '#ef4444',
      }}>{hypothesis.title}</h3>

      {/* 置信度条 */}
      <div style={{ marginBottom: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 11, color: '#64748b' }}>置信度</span>
          <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: config?.color ?? '#94a3b8' }}>
            {confidence}%
          </span>
        </div>
        <div style={{ height: 4, background: '#1e2a3a', borderRadius: 2, overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${confidence}%`,
            background: config
              ? `linear-gradient(90deg, ${config.color}80, ${config.color})`
              : 'linear-gradient(90deg, #0ea5e9, #22d3ee)',
            borderRadius: 2,
            transition: 'width 0.8s ease',
          }} />
        </div>
      </div>

      {/* 机制简述 */}
      <p style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.5, marginBottom: 8 }}>
        {hypothesis.mechanism}
      </p>

      {/* 关键生物标志物 */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6,
        padding: '6px 8px',
        background: 'rgba(14,165,233,0.06)',
        borderRadius: 6,
        border: '1px solid rgba(14,165,233,0.15)',
        marginBottom: 8,
      }}>
        <span style={{ fontSize: 11, color: '#0ea5e9' }}>🔬</span>
        <span style={{ fontSize: 11, color: '#7dd3fc', fontFamily: 'var(--font-mono)' }}>
          {hypothesis.key_biomarker}
        </span>
      </div>

      {/* House 俏皮话 */}
      <p style={{
        fontSize: 11,
        color: '#475569',
        fontStyle: 'italic',
        borderTop: '1px solid #1e2a3a',
        paddingTop: 8,
        lineHeight: 1.4,
      }}>"{hypothesis.house_quip}"</p>

      {/* 证伪原因 */}
      {isRefuted && cesAnalysis?.refute_reason && (
        <div style={{
          marginTop: 8,
          padding: '6px 8px',
          background: 'rgba(239,68,68,0.08)',
          borderRadius: 6,
          border: '1px solid rgba(239,68,68,0.2)',
        }}>
          <p style={{ fontSize: 11, color: '#fca5a5', lineHeight: 1.4 }}>
            ⚠️ {cesAnalysis.refute_reason}
          </p>
        </div>
      )}
    </div>
  );
}
