import type { Scenario } from '../types';

interface Props {
  scenarios: Scenario[];
  activeId: string | null;
  onSelect: (scenario: Scenario) => void;
  onNewCase: () => void;
}

export default function Sidebar({ scenarios, activeId, onSelect, onNewCase }: Props) {
  return (
    <aside style={{
      width: 240,
      flexShrink: 0,
      background: 'rgba(10,13,18,0.98)',
      borderRight: '1px solid #1e2a3a',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Logo */}
      <div style={{
        padding: '18px 16px 14px',
        borderBottom: '1px solid #1e2a3a',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <span style={{ fontSize: 20 }}>🧬</span>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>Bio-House</div>
            <div style={{ fontSize: 10, color: '#475569' }}>赛博豪斯</div>
          </div>
        </div>
        <p style={{ fontSize: 10, color: '#374151', fontStyle: 'italic', lineHeight: 1.4, marginTop: 4 }}>
          "Everybody lies, but metabolic pathways don't."
        </p>
      </div>

      {/* 新建案例按钮 */}
      <div style={{ padding: '12px 12px 8px' }}>
        <button
          onClick={onNewCase}
          style={{
            width: '100%',
            padding: '8px 12px',
            background: 'rgba(14,165,233,0.12)',
            border: '1px solid rgba(14,165,233,0.35)',
            borderRadius: 8,
            color: '#7dd3fc',
            fontSize: 12,
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 6,
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(14,165,233,0.2)';
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(14,165,233,0.12)';
          }}
        >
          <span style={{ fontSize: 14 }}>+</span> 新建自由推演
        </button>
      </div>

      {/* 分隔标题 */}
      <div style={{ padding: '8px 16px 4px' }}>
        <span style={{ fontSize: 10, fontWeight: 600, color: '#374151', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          预置疑案剧本
        </span>
      </div>

      {/* 场景列表 */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '4px 8px' }}>
        {scenarios.map(s => (
          <button
            key={s.id}
            onClick={() => onSelect(s)}
            style={{
              width: '100%',
              padding: '10px 10px',
              marginBottom: 4,
              background: activeId === s.id
                ? 'rgba(14,165,233,0.15)'
                : 'transparent',
              border: activeId === s.id
                ? '1px solid rgba(14,165,233,0.4)'
                : '1px solid transparent',
              borderRadius: 8,
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={e => {
              if (activeId !== s.id)
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.03)';
            }}
            onMouseLeave={e => {
              if (activeId !== s.id)
                (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <span style={{ fontSize: 16, flexShrink: 0 }}>{s.emoji}</span>
              <div>
                <div style={{
                  fontSize: 12, fontWeight: 500,
                  color: activeId === s.id ? '#7dd3fc' : '#94a3b8',
                  lineHeight: 1.3, marginBottom: 2,
                }}>{s.title}</div>
                <div style={{ fontSize: 10, color: '#374151', lineHeight: 1.3 }}>
                  {s.description}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* 底部状态 */}
      <div style={{
        padding: '10px 14px',
        borderTop: '1px solid #1e2a3a',
        fontSize: 10,
        color: '#374151',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981' }} />
          <span>MVP v1.0 · Hackathon Edition</span>
        </div>
      </div>
    </aside>
  );
}
