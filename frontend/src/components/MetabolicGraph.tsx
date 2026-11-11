import type { CascadeNode } from '../types';

interface Props {
  nodes: CascadeNode[];
}

// 纯 SVG 生化因果图（无需第三方图库）
export default function MetabolicGraph({ nodes }: Props) {
  if (!nodes || nodes.length === 0) return null;

  const nodeWidth = 110;
  const nodeHeight = 36;
  const hGap = 60;
  const vGap = 70;
  const cols = 4;
  const padding = 20;

  // 收集所有唯一节点
  const allNames = new Set<string>();
  nodes.forEach(n => { allNames.add(n.from); allNames.add(n.to); });
  const nameList = Array.from(allNames);

  // 分配坐标（简单网格布局）
  const posMap: Record<string, { x: number; y: number }> = {};
  nameList.forEach((name, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    posMap[name] = {
      x: padding + col * (nodeWidth + hGap),
      y: padding + row * (nodeHeight + vGap),
    };
  });

  const svgWidth = padding * 2 + cols * (nodeWidth + hGap) - hGap;
  const svgHeight = padding * 2 + Math.ceil(nameList.length / cols) * (nodeHeight + vGap);

  const edgeColor = (type: string) =>
    type === 'inhibits' ? '#ef4444' : type === 'activates' ? '#10b981' : '#0ea5e9';

  return (
    <div style={{ overflowX: 'auto', padding: '8px 0' }}>
      <svg
        width={svgWidth}
        height={svgHeight}
        style={{ display: 'block', minWidth: svgWidth }}
      >
        <defs>
          {/* 箭头 marker */}
          {['activates', 'inhibits', 'converts'].map(type => (
            <marker
              key={type}
              id={`arrow-${type}`}
              markerWidth="8" markerHeight="8"
              refX="6" refY="3"
              orient="auto"
            >
              <path
                d="M0,0 L0,6 L8,3 z"
                fill={edgeColor(type)}
                opacity={0.8}
              />
            </marker>
          ))}
          {/* 抑制 bar marker */}
          <marker id="bar-inhibits" markerWidth="6" markerHeight="10"
            refX="3" refY="5" orient="auto">
            <rect x="0" y="0" width="3" height="10" fill="#ef4444" opacity={0.8} />
          </marker>
        </defs>

        {/* 边 */}
        {nodes.map((edge, i) => {
          const from = posMap[edge.from];
          const to = posMap[edge.to];
          if (!from || !to) return null;

          const x1 = from.x + nodeWidth / 2;
          const y1 = from.y + nodeHeight / 2;
          const x2 = to.x + nodeWidth / 2;
          const y2 = to.y + nodeHeight / 2;

          // 贝塞尔曲线控制点
          const mx = (x1 + x2) / 2;
          const my = (y1 + y2) / 2 - 15;
          const color = edgeColor(edge.type);
          const markerId = edge.type === 'inhibits' ? 'bar-inhibits' : `arrow-${edge.type}`;

          return (
            <g key={i}>
              <path
                d={`M${x1},${y1} Q${mx},${my} ${x2},${y2}`}
                stroke={color}
                strokeWidth={1.5}
                fill="none"
                opacity={0.7}
                markerEnd={`url(#${markerId})`}
                strokeDasharray={edge.type === 'inhibits' ? '5,3' : undefined}
              />
              {/* 边标签 */}
              <text
                x={mx} y={my - 4}
                textAnchor="middle"
                fontSize={9}
                fill={color}
                opacity={0.85}
                fontFamily="JetBrains Mono, monospace"
              >
                {edge.label.length > 12 ? edge.label.slice(0, 12) + '…' : edge.label}
              </text>
            </g>
          );
        })}

        {/* 节点 */}
        {nameList.map(name => {
          const pos = posMap[name];
          if (!pos) return null;
          const displayName = name.length > 12 ? name.slice(0, 12) + '…' : name;
          return (
            <g key={name}>
              <rect
                x={pos.x} y={pos.y}
                width={nodeWidth} height={nodeHeight}
                rx={6} ry={6}
                fill="rgba(14,165,233,0.1)"
                stroke="rgba(14,165,233,0.4)"
                strokeWidth={1}
              />
              <text
                x={pos.x + nodeWidth / 2}
                y={pos.y + nodeHeight / 2 + 1}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={10}
                fill="#7dd3fc"
                fontWeight={500}
                fontFamily="JetBrains Mono, monospace"
              >
                {displayName}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
