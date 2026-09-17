/**
 * DAU Second Brain — API Client Layer
 * Kết nối Frontend React với FastAPI Backend (http://localhost:8000)
 * Tự động fallback dữ liệu tĩnh (/data.json) nếu backend offline.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface RAGQueryResponse {
  answer: string | null;
  citations: Array<{
    index: number;
    chunk_id: string;
    doc_id: string;
    so_hieu: string;
    ten_van_ban: string;
    dieu_khoan: string;
    so_trang: number;
    content_preview: string;
  }>;
  message: string;
  nli_status: string;
}

export interface DocumentItem {
  doc_id: string;
  so_hieu: string;
  ten_van_ban: string;
  co_quan_ban_hanh: string;
  ngay_ban_hanh: string;
  loai_van_ban: string;
  trich_yeu: string;
  chu_de: string;
  muc_do_lien_quan_dau: string;
  trang_thai_xuat_ban: string;
  can_cu_dan_chieu: string[];
  file_path: string;
}

export interface DocumentDetailResponse {
  document: DocumentItem;
  total_chunks: number;
  chunks: Array<{
    chunk_id: string;
    dieu_so: number;
    title: string;
    content: string;
    so_trang: number;
  }>;
}

export interface StatsResponse {
  total_documents: number;
  published_documents: number;
  pending_documents: number;
  total_chunks: number;
  published_chunks: number;
  topics: Record<string, number>;
  faiss_index_exists: boolean;
}

/**
 * Gửi câu hỏi đến RAG Backend
 */
export async function queryRAG(
  question: string,
  k = 5,
  runNli = true
): Promise<RAGQueryResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, k, run_nli: runNli }),
    });

    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    console.warn('[API Client] Query failed, Backend may be offline:', err);
    return {
      answer: null,
      citations: [],
      message: 'Backend server không khả dụng. Hãy bật server với: uvicorn api.main:app',
      nli_status: 'OFFLINE',
    };
  }
}

/**
 * Lấy danh sách văn bản với phân trang & bộ lọc
 */
export async function fetchDocuments(params?: {
  page?: number;
  limit?: number;
  q?: string;
  chu_de?: string;
  trang_thai?: string;
}): Promise<{ page: number; total: number; total_pages: number; items: DocumentItem[] }> {
  try {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.q) query.append('q', params.q);
    if (params?.chu_de) query.append('chu_de', params.chu_de);
    if (params?.trang_thai) query.append('trang_thai', params.trang_thai);

    const res = await fetch(`${API_BASE_URL}/documents?${query.toString()}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn('[API Client] Fetch documents offline mode:', err);
    return { page: 1, total: 0, total_pages: 1, items: [] };
  }
}

/**
 * Lấy chi tiết văn bản & danh sách chunks
 */
export async function fetchDocumentDetail(docId: string): Promise<DocumentDetailResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/documents/${docId}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn('[API Client] Fetch doc detail offline mode:', err);
    return null;
  }
}

/**
 * Phê duyệt / Đổi trạng thái văn bản
 */
export async function publishDocument(docId: string, newStatus = 'PUBLISHED'): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/publish/${docId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_status: newStatus }),
    });
    return res.ok;
  } catch (err) {
    console.warn('[API Client] Publish document offline mode:', err);
    return false;
  }
}

/**
 * Lấy thống kê hệ thống
 */
export async function fetchStats(): Promise<StatsResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/stats`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn('[API Client] Fetch stats offline mode:', err);
    return null;
  }
}

/**
 * Health check
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

// ── Review Queue Interfaces & Functions ────────────────────────────────────

export interface ReviewItemData {
  review_item_id: number;
  document_id: string;
  ten_van_ban: string;
  so_hieu: string;
  citation_id: number | null;
  cau_ai_sinh: string;
  nhan_nli: string;
  do_uu_tien: string;
  trang_thai: string;
  source_chunk: {
    chunk_id: string;
    dieu_khoan: string;
    noi_dung_goc: string;
    so_trang: number;
  } | null;
  created_at: string;
}

export interface AuditLogData {
  log_id: number;
  review_item_id: number;
  document_id: string;
  ten_van_ban: string;
  cau_ai_sinh: string;
  cau_sau_sua: string | null;
  reviewer_id: string;
  hanh_dong: string;
  diem_nli_sau_sua: number | null;
  created_at: string;
}

export interface ReviewQueueResponse {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  items: ReviewItemData[];
}

export async function fetchReviewQueue(params?: {
  page?: number;
  limit?: number;
  status?: string;
  priority?: string;
}): Promise<ReviewQueueResponse> {
  try {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.status) query.append('status', params.status);
    if (params?.priority) query.append('priority', params.priority);

    const res = await fetch(`${API_BASE_URL}/review/queue?${query.toString()}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn('[API Client] fetchReviewQueue failed:', err);
    return { page: 1, limit: 20, total: 0, total_pages: 1, items: [] };
  }
}

export async function submitReviewAction(
  itemId: number,
  action: 'approve' | 'edit' | 'reject',
  editedSentence?: string,
  reviewerId = 'can_bo_dao_tao'
): Promise<{ success: boolean; data?: any; message?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/review/${itemId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action,
        edited_sentence: editedSentence,
        reviewer_id: reviewerId,
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Review action failed');
    return { success: true, data };
  } catch (err: any) {
    console.error('[API Client] submitReviewAction error:', err);
    return { success: false, message: err.message || 'Lỗi xử lý rà soát' };
  }
}

export async function fetchAuditLogs(limit = 50): Promise<AuditLogData[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/review/audit-logs?limit=${limit}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    const data = await res.json();
    return data.logs || [];
  } catch (err) {
    console.warn('[API Client] fetchAuditLogs failed:', err);
    return [];
  }
}

// ── Report Suggestion Interfaces & Functions (UC-05) ─────────────────────

export interface ReportOutlineSection {
  heading: string;
  content: string;
  is_blank: boolean;
  type: string;
}

export interface ReportOutlineResponse {
  doc_id: string;
  quoc_hieu?: string;
  tieu_ngu?: string;
  co_quan_ban_hanh_tren?: string;
  don_vi_bao_cao?: string;
  so_ky_hieu?: string;
  dia_danh_ngay_thang?: string;
  ten_van_ban: string;
  so_hieu: string;
  loai_van_ban: string;
  chu_de: string;
  ten_don_bao_cao?: string;
  trich_yeu?: string;
  kinh_gui?: string;
  template_used: string;
  sections: ReportOutlineSection[];
  noi_nhan?: string[];
  nguoi_ky_chuc_danh?: string;
  nguoi_ky_chu_ky?: string;
}

export async function fetchReportOutline(docId: string): Promise<ReportOutlineResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/report/suggest/${docId}`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn('[API Client] fetchReportOutline failed:', err);
    return null;
  }
}

export function getReportDocxDownloadUrl(docId: string): string {
  return `${API_BASE_URL}/report/export-docx/${docId}`;
}

// ── Document Tree & DAU Application Scope Interfaces & Functions (UC-06) ──

export interface DocumentTreeNode {
  doc_id: string;
  so_hieu: string;
  ten_van_ban: string;
  loai_quan_he: string;
  pham_vi_ap_dung: string;
  diem_tuong_dong?: number;
}

export interface DocumentTreeResponse {
  doc_id: string;
  so_hieu: string;
  ten_van_ban: string;
  pham_vi_ap_dung: string;
  legal_parents: DocumentTreeNode[];
  legal_children: DocumentTreeNode[];
  semantic_related: DocumentTreeNode[];
}

export async function fetchDocumentTree(docId: string): Promise<DocumentTreeResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(docId)}/tree`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn('[API Client] fetchDocumentTree failed:', err);
    return null;
  }
}

export async function updateDocumentScope(docId: string, scope: string): Promise<{ success: boolean; data?: any; message?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(docId)}/scope`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pham_vi_ap_dung: scope }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Update scope failed');
    return { success: true, data };
  } catch (err: any) {
    console.error('[API Client] updateDocumentScope error:', err);
    return { success: false, message: err.message || 'Lỗi cập nhật phạm vi áp dụng' };
  }
}

// ── Topic Dashboard Interfaces & Functions (UC-08) ──────────────────────────

export interface TopicSummaryItem {
  code: string;
  name: string;
  icon: string;
  total_documents: number;
  published_documents: number;
  pending_documents: number;
  total_chunks: number;
  completion_rate: number;
}

export async function fetchTopicsSummary(): Promise<TopicSummaryItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/topics/summary`);
    if (!res.ok) throw new Error(`API error: ${res.statusText}`);
    const data = await res.json();
    return data.topics || [];
  } catch (err) {
    console.warn('[API Client] fetchTopicsSummary failed:', err);
    return [];
  }
}


// ── Summarization Interfaces & Functions (UC-03, WF-03) ──────────────────────

export type SummarizeStrategy = 'extractive' | 'abstractive' | 'hybrid';

export type NLILabel = 'entailment' | 'contradiction' | 'neutral' | 'PENDING';

export interface SummarizeSentenceResult {
  sentence: string;
  chunk_id: string;
  method: string;           // "extractive" | "abstractive" | "extractive_fallback"
  nhan_nli: NLILabel;
  diem_faithfulness: number | null;
  publish_action: string;   // "AUTO_PUBLISH" | "WARN_PENDING_REVIEW" | "BLOCK_PENDING_REVIEW"
}

export interface SummarizeChunkResult {
  chunk_id: string;
  doc_id: string;
  sentences: SummarizeSentenceResult[];
  overall_action: string;
  trang_thai_xuat_ban: string;
  has_contradiction: boolean;
  has_neutral: boolean;
  strategy_used: string;
  nli_stats: {
    entailment: number;
    contradiction: number;
    neutral: number;
    total: number;
  };
}

export interface SummarizeResponse {
  doc_id: string;
  ten_van_ban: string;
  so_hieu: string;
  strategy: SummarizeStrategy;
  overall_action: string;
  trang_thai_xuat_ban: string;
  total_chunks: number;
  total_sentences: number;
  strategies_used: string[];
  avg_faithfulness: number | null;
  nli_stats: {
    entailment: number;
    contradiction: number;
    neutral: number;
    total: number;
  };
  chunk_results: SummarizeChunkResult[];
}

/**
 * Gọi summarization pipeline cho một văn bản.
 * Strategy "hybrid" sẽ tự fallback sang extractive nếu BARTpho không tải được.
 */
export async function summarizeDocument(
  docId: string,
  options: {
    strategy?: SummarizeStrategy;
    run_nli?: boolean;
    max_chunks?: number;
  } = {}
): Promise<SummarizeResponse | null> {
  const { strategy = 'hybrid', run_nli = true, max_chunks } = options;
  try {
    const res = await fetch(`${API_BASE_URL}/summarize/${encodeURIComponent(docId)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy, run_nli, max_chunks: max_chunks ?? null }),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `API error: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.error('[API Client] summarizeDocument failed:', err);
    return null;
  }
}

// ── Ingestion Pipeline (UC-01) ────────────────────────────────────────────────

export async function uploadDocument(file: File, chuDe: string = "KHAC"): Promise<any> {
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("chu_de", chuDe);

    const res = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Upload failed: ${res.statusText}`);
    }
    
    return await res.json();
  } catch (err) {
    console.error('[API Client] uploadDocument failed:', err);
    throw err;
  }
}
