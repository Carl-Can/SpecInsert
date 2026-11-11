import type { CuddyOutput } from '../types';
import { EDUCATIONAL_DISCLAIMER_EN, EDUCATIONAL_DISCLAIMER_ZH } from '../disclaimer';

interface Props {
  cuddy: CuddyOutput;
}

export default function FinalVerdict({ cuddy }: Props) {
  const { final_diagnosis, whiteboard_summary, cuddy_verdict } = cuddy;

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(14,165,233,0.05) 100%)',
      border: '1px solid rgba(16,185,129,0.4)',
      borderRadius: 12,
      padding: '20px',
      animation: 'slide-in-up 0.5s ease forwards, glow-green 3s ease-in-out 0.5s infinite',
      boxShadow: '0 0 20px rgba(16,185,129,0.2)',
    }}>
      {/* 标题 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span style={{ fontSize: 20 }}>⚖️</span>
        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#34d399' }}>
          House's Final Verdict
        </h3>
        <div style={{
          marginLeft: 'auto',
          padding: '3px 10px',
          background: 'rgba(16,185,129,0.15)',
          border: '1px solid rgba(16,185,129,0.4)',
          borderRadius: 20,
          fontSize: 11,
          color: '#34d399',
          fontWeight: 600,
        }}>教学推演结束</div>
      </div>

      {/* Cuddy 裁决宣言 */}
      <div style={{
        padding: '10px 14px',
        background: 'rgba(99,102,241,0.08)',
        border: '1px solid rgba(99,102,241,0.2)',
        borderRadius: 8,
        marginBottom: 14,
      }}>
        <p style={{ fontSize: 12, color: '#a5b4fc', fontStyle: 'italic' }}>
          ⚖️ "{cuddy_verdict}"
        </p>
      </div>

      {/* 白板一句话总结 */}
      <div style={{
        padding: '12px 14px',
        background: 'rgba(16,185,129,0.06)',
        border: '1px solid rgba(16,185,129,0.25)',
        borderRadius: 8,
        marginBottom: 14,
      }}>
        <p style={{ fontSize: 13, fontWeight: 600, color: '#6ee7b7', lineHeight: 1.5 }}>
          🧬 {whiteboard_summary}
        </p>
      </div>

      {/* 机制总结 */}
      <div style={{ marginBottom: 14 }}>
        <h4 style={{ fontSize: 12, fontWeight: 600, color: '#94a3b8', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          完整生化机制
        </h4>
        <p style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.7 }}>
          {final_diagnosis.mechanism_summary}
        </p>
      </div>

      {/* 临床干预 */}
      <div style={{
        padding: '12px 14px',
        background: 'rgba(14,165,233,0.06)',
        border: '1px solid rgba(14,165,233,0.2)',
        borderRadius: 8,
        marginBottom: final_diagnosis.safety_warning ? 10 : 0,
      }}>
        <h4 style={{ fontSize: 11, color: '#0ea5e9', marginBottom: 6, fontWeight: 600 }}>
          讨论用机制干预（不是医嘱）
        </h4>
        <p style={{ fontSize: 12, color: '#7dd3fc', lineHeight: 1.6 }}>
          {final_diagnosis.intervention}
        </p>
      </div>

      <div style={{
        padding: '10px 14px',
        background: 'rgba(245,158,11,0.08)',
        border: '1px solid rgba(245,158,11,0.35)',
        borderRadius: 8,
        marginTop: 10,
      }}>
        <p style={{ fontSize: 12, color: '#fcd34d', lineHeight: 1.5 }}>
          {EDUCATIONAL_DISCLAIMER_EN}
        </p>
        <p style={{ fontSize: 12, color: '#e7e5e4', lineHeight: 1.5, marginTop: 4 }}>
          {EDUCATIONAL_DISCLAIMER_ZH}
        </p>
      </div>

      {/* 安全警示 */}
      {final_diagnosis.safety_warning && (
        <div style={{
          padding: '10px 14px',
          background: 'rgba(245,158,11,0.08)',
          border: '1px solid rgba(245,158,11,0.3)',
          borderRadius: 8,
          marginTop: 10,
        }}>
          <p style={{ fontSize: 12, color: '#fcd34d', lineHeight: 1.5 }}>
            ⚠️ <strong>安全警示：</strong>{final_diagnosis.safety_warning}
          </p>
        </div>
      )}
    </div>
  );
}
