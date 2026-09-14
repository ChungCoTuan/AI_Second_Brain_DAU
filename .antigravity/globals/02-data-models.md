# Tóm tắt Thiết kế Cơ sở Dữ liệu & Data Models

Dưới đây là các Model (Schema) bắt buộc khi trích xuất dữ liệu, đặc biệt phục vụ cho hiển thị Frontend. Bất kỳ sự thay đổi nào cũng phải tương thích với các interface trong `data.ts`.

## 1. DocumentChunk (Đoạn văn bản)
Cấu trúc trung gian để lưu trữ văn bản sau khi parse từ PDF:
```typescript
interface DocumentChunk {
  id: string; // hash
  docId: string; // mã văn bản gốc
  chapter?: string;
  section?: string;
  article: string; // Điều
  clause?: string; // Khoản
  content: string; // Nội dung thô
}
```

## 2. Nghĩa vụ (nghiaVu)
```typescript
interface NghiaVu {
  vb: string; // Số hiệu văn bản
  dieu: string; // Điều chứa nghĩa vụ
  loai: 'đào tạo' | 'tài chính' | 'nhân sự' | 'báo cáo' | 'khác';
  chuThe: string; // Đối tượng phải thực hiện (VD: "trường", "phòng đào tạo")
  noiDung: string; // Nội dung nghĩa vụ
  hanChot?: string; // Hạn chót (VD: "20-11-2026", "--11-20", "tính")
  nguon: string; // Trích dẫn nguyên văn
}
```

## 3. Sự kiện hiệu lực (suKienHieuLuc)
```typescript
interface SuKienHieuLuc {
  cu: string; // Số hiệu văn bản cũ
  tenCu: string; // Tên văn bản cũ
  moi: string; // Số hiệu văn bản mới (bãi bỏ/thay thế)
  tenMoi: string; // Tên văn bản mới
  lyDo: 'thay thế' | 'bãi bỏ một phần' | 'bãi bỏ toàn bộ';
  phamVi?: string; // Nếu bãi bỏ một phần thì ghi rõ Điều/Khoản nào
  nguon: string; // Câu dẫn chứng
  tuNgay?: string; // Ngày hiệu lực
}
```

## 4. Con số chốt (conSoChot)
```typescript
interface ConSoChot {
  vb: string;
  dieu: string;
  giaTri: string; // VD: "30 ngày", "20%"
  yNghia: string; // Mục đích của con số
  nguon: string;
}
```

## 5. Cảnh báo (Warning / Cross-Auditing)
```typescript
interface WarningItem {
  canCu: string; // Văn bản/Luật bị trích dẫn sai
  thayBang: string; // Đã bị thay thế bằng văn bản nào
  lyDo: string; // "bị thay thế" / "bị bãi bỏ"
}
interface Warning {
  docId: string; // ID quy chế nội bộ
  soHieu: string; 
  items: WarningItem[];
}
```
