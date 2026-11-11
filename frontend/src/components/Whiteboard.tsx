import type { DiagnosisState } from '../types';
import HypothesisCard from './HypothesisCard';
import MetabolicGraph from './MetabolicGraph';
import FinalVerdict from './FinalVerdict';
import AgentStatus from './AgentStatus';
import { CITATION_NOTE_ZH } from '../disclaimer';

interface Props {
  state: DiagnosisState;
}

export default function Whiteboard({ state }: Props) {
  const { stage, house, cameron, cuddy, statusMessage } = state;

  // 建立 hypothesis_id → CES 分析的映射
  const cesMap: Record<string, import('../types').CESAnalysis> = {};
  cuddy?.ces_analysis?.forEach(c => { cesMap[c.hypothesis_id] = c; });

  const isActive = stage !== 'idle';

  if (!isActive) {
    return (
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        color: '#374151', userSelect: 'none',
        padding: 40,
      }}>
        <div style={{ fontSize: 64, marginBottom: 16, opacity: 0.5 }}>🧬</div>
        <h2 style={{ fontSize: 18, fontWeight: 600, color: '#475569', marginBottom: 8 }}>
          鉴别诊断白板
        </h2>
        <p style={{ fontSize: 13, color: '#374151', textAlign: 'center', maxWidth: 360, lineHeight: 1.6 }}>
          从左侧选择预置疑案剧本，或在下方输入自定义病例，然后点击"启动会诊"
        </p>
        <p style={{ fontSize: 11, color: '#57534e', textAlign: 'center', maxWidth: 360, lineHeight: 1.5, marginTop: 10 }}>
          {CITATION_NOTE_ZH}
        </p>
        <div style={{
          marginTop: 24, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, maxWidth: 420,
        }}>
          {['🩺 Dr. House 野性假说生成', '🔬 Cameron 循证检索', '⚖️ Cuddy CES 双侧证伪', '🧬 生化因果级联图'].map(item => (
            <div key={item} style={{
              padding: '8px 12px',
              background: 'rgba(14,165,233,0.04)',
              border: '1px solid rgba(14,165,233,0.12)',
              borderRadius: 8, fontSize: 11, color: '#475569', textAlign: 'center',
            }}>{item}</div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Agent 进度状态 */}
      <AgentStatus stage={stage} statusMessage={statusMessage} />

      {/* 假说白板 */}
      {house && (
        <div style={{
          background: 'rgba(14,25,41,0.8)',
          border: '1px solid #1e2a3a',
          borderRadius: 12,
          padding: '16px',
          animation: 'slide-in-up 0.4s ease',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <span style={{ fontSize: 18 }}>🩺</span>
            <h3 style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>Dr. House 的鉴别诊断</h3>
            <span style={{
              marginLeft: 'auto', padding: '2px 8px', borderRadius: 4,
              background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)',
              fontSize: 11, color: '#fbbf24',
            }}>假说生成阶段</span>
          </div>

          {/* House 评语 */}
          <div style={{
            padding: '8px 12px', marginBottom: 14,
            background: 'rgba(20,25,33,0.6)',
            border: '1px solid #1e2a3a', borderRadius: 8,
            borderLeft: '3px solid #0ea5e9',
          }}>
            <p style={{ fontSize: 12, color: '#94a3b8', fontStyle: 'italic' }}>
              💬 {house.house_comment}
            </p>
          </div>

          {/* 假说卡片 */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {house.hypotheses?.map((h, i) => (
              <HypothesisCard
                key={h.id}
                hypothesis={h}
                cesAnalysis={cesMap[h.id]}
                isAnimating={i < 4}
              />
            ))}
          </div>

          {/* 优先调查方向 */}
          {house.priority_investigation && (
            <div style={{
              marginTop: 12, padding: '8px 12px',
              background: 'rgba(14,165,233,0.06)',
              border: '1px solid rgba(14,165,233,0.15)',
              borderRadius: 8,
            }}>
              <span style={{ fontSize: 11, color: '#0ea5e9', fontWeight: 600 }}>🎯 优先调查：</span>
              <span style={{ fontSize: 12, color: '#7dd3fc', marginLeft: 6 }}>
                {house.priority_investigation}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Cameron 证据分析 + 生化图 */}
      {cameron && (
        <div style={{
          background: 'rgba(14,25,41,0.8)',
          border: '1px solid #1e2a3a',
          borderRadius: 12,
          padding: '16px',
          animation: 'slide-in-up 0.4s ease',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <span style={{ fontSize: 18 }}>🔬</span>
            <h3 style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>Cameron 循证分析</h3>
            <span style={{
              marginLeft: 'auto', padding: '2px 8px', borderRadius: 4,
              background: 'rgba(14,165,233,0.1)', border: '1px solid rgba(14,165,233,0.3)',
              fontSize: 11, color: '#7dd3fc',
            }}>示意笔记 · 待核验</span>
          </div>

          {/* Cameron 评述 */}
          <div style={{
            padding: '8px 12px', marginBottom: 12,
            background: 'rgba(20,25,33,0.6)',
            border: '1px solid #1e2a3a', borderRadius: 8,
            borderLeft: '3px solid #22d3ee',
          }}>
            <p style={{ fontSize: 12, color: '#94a3b8', fontStyle: 'italic' }}>
              💬 {cameron.cameron_note}
            </p>
          </div>

          {/* 证据列表 */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 14 }}>
            {cameron.evidence_analysis?.map(ev => (
              <div key={ev.hypothesis_id} style={{
                padding: '12px',
                background: 'rgba(20,25,33,0.5)',
                border: '1px solid #1e2a3a',
                borderRadius: 8,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span style={{
                    fontSize: 11, fontFamily: 'var(--font-mono)',
                    color: '#0ea5e9',
                    background: 'rgba(14,165,233,0.1)',
                    padding: '1px 6px', borderRadius: 3,
                  }}>{ev.hypothesis_id}</span>
                  <span style={{
                    fontSize: 10, padding: '1px 6px', borderRadius: 3,
                    background: ev.evidence_strength === '强' ? 'rgba(16,185,129,0.1)' :
                                ev.evidence_strength === '中' ? 'rgba(245,158,11,0.1)' : 'rgba(107,114,128,0.1)',
                    color: ev.evidence_strength === '强' ? '#34d399' :
                           ev.evidence_strength === '中' ? '#fbbf24' : '#9ca3af',
                    border: `1px solid ${ev.evidence_strength === '强' ? 'rgba(16,185,129,0.3)' :
                                         ev.evidence_strength === '中' ? 'rgba(245,158,11,0.3)' : 'rgba(107,114,128,0.3)'}`,
                  }}>证据{ev.evidence_strength}</span>
                </div>

                {/* 生化因果链 */}
                <div style={{
                  fontFamily: 'var(--font-mono)', fontSize: 11,
                  color: '#22d3ee', lineHeight: 1.6,
                  padding: '6px 10px',
                  background: 'rgba(34,211,238,0.04)',
                  borderRadius: 6, marginBottom: 8,
                  overflowX: 'auto', whiteSpace: 'nowrap',
                }}>
                  {ev.causal_chain}
                </div>

                {/* 证据点 */}
                <div style={{ display: 'flex', gap: 8 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 10, color: '#10b981', fontWeight: 600, marginBottom: 4 }}>支持证据</div>
                    {ev.support_evidence?.map((e, i) => (
                      <div key={i} style={{ fontSize: 11, color: '#6ee7b7', lineHeight: 1.5, marginBottom: 2 }}>
                        ✓ {e}
                      </div>
                    ))}
                  </div>
                  {ev.vulnerability && (
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 10, color: '#f59e0b', fontWeight: 600, marginBottom: 4 }}>潜在漏洞</div>
                      <div style={{ fontSize: 11, color: '#fcd34d', lineHeight: 1.5 }}>
                        ⚠ {ev.vulnerability}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* 生化因果图 */}
          {cameron.metabolic_cascade_nodes?.length > 0 && (
            <div>
              <h4 style={{ fontSize: 12, fontWeight: 600, color: '#94a3b8', marginBottom: 8 }}>
                🕸️ 生化级联因果拓扑图
              </h4>
              <div style={{
                padding: 12, background: 'rgba(10,13,18,0.8)',
                border: '1px solid #1e2a3a', borderRadius: 8,
              }}>
                <MetabolicGraph nodes={cameron.metabolic_cascade_nodes} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Cuddy 最终裁决 */}
      {cuddy && stage !== 'cuddy_thinking' && (
        <FinalVerdict cuddy={cuddy} />
      )}

      {/* 底部占位 */}
      <div style={{ height: 20 }} />
    </div>
  );
}
