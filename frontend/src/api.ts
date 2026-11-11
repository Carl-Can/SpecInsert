// Bio-House API 客户端

const API_BASE = 'http://localhost:8000';

export interface DiagnoseRequest {
  case_input: string;
  scenario_id?: string;
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/api/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch scenarios');
  return res.json();
}

export async function fetchScenario(id: string) {
  const res = await fetch(`${API_BASE}/api/scenarios/${id}`);
  if (!res.ok) throw new Error('Failed to fetch scenario');
  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error('Backend unreachable');
  return res.json();
}

/**
 * 流式诊断接口 - 通过 SSE 接收三个 Agent 的推理过程
 * @param request 诊断请求
 * @param onEvent 每收到一个 SSE 事件时回调
 */
export async function streamDiagnose(
  request: DiagnoseRequest,
  onEvent: (event: Record<string, unknown>) => void
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/diagnose/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Diagnose request failed');
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE 格式解析：每行 "data: {...}\n\n"
    const lines = buffer.split('\n\n');
    buffer = lines.pop() ?? ''; // 保留不完整的最后一块

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('data: ')) {
        try {
          const json = JSON.parse(trimmed.slice(6));
          onEvent(json);
        } catch {
          // 忽略解析失败的行
        }
      }
    }
  }
}
