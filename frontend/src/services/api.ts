// API Client Service kết nối React Frontend tới Backend FastAPI (/api)

const API_BASE_URL = 'http://localhost:8000/api';

export interface DocumentItem {
  doc_id: str;
  so_hieu: str;
  ten_van_ban: str;
  co_quan_ban_hanh: str;
  ngay_ban_hanh: str;
  loai_van_ban: str;
  trich_yeu: str;
  chu_de: string;
  muc_do_lien_quan_dau: string;
  trang_thai_xuat_ban: string;
  can_cu_dan_chieu: string[];
  file_path: string;
}

export interface ChunkItem {
  chunk_id: string;
  doc_id: string;
  so_hieu: string;
  dieu_so?: number;
  khoan_so?: number;
  so_trang: number;
  title: string;
  content: string;
  token_count: number;
  chu_de: string;
  muc_do_lien_quan_dau: string;
}

export interface RelationItem {
  relation_id: string;
  document_id_a: string;
  document_id_b: string;
  loai_quan_he: string;
  mo_ta?: string;
  diem_tuong_dong?: number;
}

export interface TopicSummary {
  id: string;
  title: string;
  count: number;
  icon: string;
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return res.json();
}

export async function fetchTopics(): Promise<TopicSummary[]> {
  const res = await fetch(`${API_BASE_URL}/topics`);
  return res.json();
}

export async function fetchDocuments(params?: { topic?: string; search?: string; status?: string }): Promise<DocumentItem[]> {
  const query = new URLSearchParams();
  if (params?.topic) query.append('topic', params.topic);
  if (params?.search) query.append('search', params.search);
  if (params?.status) query.append('status', params.status);

  const res = await fetch(`${API_BASE_URL}/documents?${query.toString()}`);
  return res.json();
}

export async function fetchDocumentDetail(docId: string): Promise<{ document: DocumentItem; chunks: ChunkItem[]; relations: RelationItem[] }> {
  const res = await fetch(`${API_BASE_URL}/documents/${docId}`);
  if (!res.ok) throw new Error('Document not found');
  return res.json();
}

export async function fetchReviewItems() {
  const res = await fetch(`${API_BASE_URL}/review`);
  return res.json();
}

export async function updateDocumentStatus(docId: string, status: string) {
  const res = await fetch(`${API_BASE_URL}/documents/${docId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  return res.json();
}
