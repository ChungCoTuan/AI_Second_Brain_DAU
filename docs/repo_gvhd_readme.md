# Rà soát Văn bản: bản demo tĩnh (gửi trường)

Web **tĩnh hoàn toàn** (chỉ `index.html` + `data.js`), không cần backend, không cần cơ sở dữ liệu.
Tái hiện phần giá trị của DocOps: **26 văn bản của trường đang viện dẫn căn cứ pháp lý đã hết hiệu lực**,
gộp theo **10 lần luật thay đổi**, kèm **đồ thị tác động**. Dữ liệu trích từ rà soát thực tế.

Nền trắng + nhấn đỏ maroon (đồng bộ logo và website của trường).

## Bản cập nhật 19/08/2026: nạp thêm văn bản mới nhất của Bộ

Đã bóc tách **18 văn bản pháp quy công khai** (Bộ GDĐT, Chính phủ, Quốc hội, Bộ TTTT; đợt 2024 tới 2026)
tới mức **điều khoản**, và nối vào kho văn bản của trường.

Con số sau khi nạp (đã sửa theo kết quả QA độc lập, xem mục cuối):

| Khối | Số lượng |
|---|---|
| Văn bản pháp quy đã bóc | 18 (14 Bộ GDĐT, 2 Thủ tướng, 1 Quốc hội, 1 Bộ TTTT) |
| Điều khoản | 417 Điều, cộng 4 Phụ lục |
| Nghĩa vụ | 297, trong đó 287 là việc của trường |
| Con số chốt (ngưỡng, tỉ lệ, thời hạn) | 354 |
| Lần đổi hiệu lực có kèm nguyên văn | 45 |
| Mốc thời hạn | 42, trong đó **1 mốc quá hạn thuộc về trường** |
| Bản ghi tra cứu được | 137 (119 của trường + 18 văn bản pháp quy) |

**Phát hiện đáng kể nhất:** 4 văn bản trong kho không chỉ *viện dẫn* căn cứ đã chết mà **chính chúng đã
hết hiệu lực**: TT 17/2021, TT 35/2021, TT 02/2022 (đều bị TT 54/2026 thay thế) và TT 08/2021
(bị TT 56/2026 thay thế). Thêm **QĐ 1982/QĐ-TTg sẽ hết hiệu lực ngày 07/09/2026** (bị QĐ 39/2026/QĐ-TTg
thay thế), tính tới mốc dữ liệu 19/08/2026 thì nó **vẫn còn hiệu lực**.

Lưu ý: "hết hiệu lực" không đồng nghĩa "mọi thứ trích từ đó vô giá trị ngay". Các văn bản thay thế
đều có **điều khoản chuyển tiếp** cho phép áp dụng tiếp với khoá tuyển sinh hoặc hồ sơ đã có.

### Các mục mới trên trang

- **Chính văn bản đã bị khai tử**: mức nghiêm trọng hơn mục cảnh báo cũ.
- **Hạn chót và mốc chưa tới**: dòng thời gian, đánh dấu mốc đã qua và mốc còn dưới 120 ngày.
- **Tra cứu kho văn bản**: tìm không dấu, lọc theo nguồn và theo loại, tô vàng đoạn khớp.
- **Việc phải làm**: 297 nghĩa vụ, lọc theo văn bản và theo loại việc.
- **Sổ tra ngưỡng**: 354 con số định lượng.
- **Mọi lần đổi hiệu lực**: 45 lần, mỗi lần kèm nguyên văn điều khoản.
- **Chỗ hệ thống chưa biết**: khai thẳng giới hạn của bản demo.
- **Ô chi tiết** nay hiển thị được văn bản Bộ ở mức điều khoản, nghĩa vụ và con số.

### Nguyên tắc dữ liệu

Khẳng định bóc từ 18 văn bản pháp quy (thay thế, bãi bỏ, ngày hiệu lực, hạn chót, nghĩa vụ, con số)
đều lưu kèm **nguyên văn** câu trong văn bản gốc, mở ra được ngay trên giao diện. Dữ liệu cảnh báo
**có sẵn từ trước** thì không có nguyên văn, nên giao diện gắn nhãn riêng chứ không trộn lẫn.

Ba loại nhãn phân biệt mức độ chắc chắn, có cài đặt thật trong dữ liệu chứ không chỉ là lời khai:

- `coNguon` trên từng lượt viện dẫn: có nguyên văn đối chứng hay chỉ suy luận từ số hiệu.
- `nguonNgay` trên từng mốc hạn chót: ngày **chép** từ văn bản hay **tính** ra bằng phép cộng.
- `nguonDoSo` trên từng con số: câu nguyên văn kèm theo có chứa chính con số đó không.
- `chuThe` trên từng nghĩa vụ: việc của trường, của cơ quan quản lý, của trường công lập,
  của đại học quốc gia và đại học vùng, hay của bậc học khác. Nhận diện bằng cụm từ có thật
  ở đầu câu, không suy đoán.

### Giới hạn đã biết

- **17/41 lượt viện dẫn có nguyên văn đối chứng; 24 lượt còn lại là suy luận từ số hiệu**, vì các
  văn bản thay thế NĐ 91/2026, NĐ 37/2025, TT 10/2016 và TT 08/2021 chưa có bản gốc trong kho.
  Đây là giới hạn nặng nhất của hệ thống.
- **Tỉ lệ hỏng trên phần đã rà là 100%, không phải 14%.** Trong 26 văn bản bóc được danh sách căn cứ
  thì cả 26 đều dính căn cứ hết hiệu lực. Hệ thống khai tổng kho 181 văn bản, nhưng 62 cái không có
  bản trích xuất và 93 cái chưa bóc căn cứ, tức **155 văn bản chưa hề được kiểm**. Chưa kiểm không
  có nghĩa là sạch.
- **8 lượt** đề xuất chuyển sang một căn cứ mà chính nó cũng đã hết hiệu lực (TT 08/2021). Đã gắn
  cảnh báo tại chỗ, nhưng dây chuyền thay thế mới chạy được một bậc.
- **25 nghĩa vụ và 6 con số** được bóc từ TT 35/2021, văn bản đã hết hiệu lực từ 30/06/2026. Vẫn
  hiển thị để đối chiếu lịch sử nhưng đã gắn nhãn đỏ.
- **10/297 nghĩa vụ không phải việc của trường.** Trong 3 mốc đã quá hạn, chỉ 1 mốc thuộc về trường;
  2 mốc còn lại là việc của Ủy ban nhân dân cấp xã và của trường công lập (trường này là tư thục).
- **9 mốc hạn chót là do cộng ra**, không in trong văn bản. **18 con số** có câu nguyên văn không
  chứa chính con số đó (ví dụ tổng số tiêu chí là do đếm). Cả hai nhóm đều đã gắn nhãn riêng.
- TT 65/2026 đọc từ bản scan qua OCR. Ngày hiệu lực đã đọc lại bằng mắt trên ảnh trang gốc
  (26/9/2026) và được kiểm chéo độc lập; vẫn nên đối chiếu Công báo trước khi dùng cho việc có
  hậu quả pháp lý. Bản OCR trung gian đọc sai thành tháng 7, đừng dùng lại nó.
- Phụ lục dạng bảng nhiều cột của **11 văn bản** bị công cụ bóc trộn chữ giữa các cột nên không lấy
  nguyên văn từ vùng đó. Số điều khoản, nghĩa vụ và con số chỉ tính **phần thân** văn bản.
- Trường nguyên văn là bản **đã nối lại** các chỗ tệp gốc ngắt dòng giữa số hiệu, không phải chuỗi
  ký tự thô.
- Điểm tin cậy trích xuất là **điểm tự đánh giá của bộ trích xuất**, không phải sai số đo được so
  với bản gốc.

### Đã sửa sau đợt QA độc lập (6 agent, 19/08/2026)

| Lỗi | Trước | Sau |
|---|---|---|
| Đếm lặp do số hiệu ghi hai kiểu | 10 lần luật thay đổi | 8 |
| Đếm lặp ở danh sách căn cứ chưa có văn bản thay | 7 | 5 |
| Không so ngày với mốc hôm nay | 5 văn bản đã hết hiệu lực | 4, cộng 1 sắp hết |
| Đếm Phụ lục lẫn vào Điều | 421 điều | 417 Điều + 4 Phụ lục |
| Nhãn trái nguyên văn (Luật 34/2018) | 32 thay thế / 9 bãi bỏ | 38 / 3 |
| Văn bản thay thế sai số hiệu | Luật 74/2014 bị thay bởi Luật 124/2025 | Luật 125/2025 |
| Gán cứng phạm vi | 35/35 quan hệ ghi "toàn bộ" | 14 quan hệ có phạm vi hẹp hoặc mệnh đề trừ |
| Bỏ trống ngày văn bản cũ | 35/45 có ngày | 39/45 |
| Mẫu số gây hiểu ngược | "26 / 181" | "26/26 đã rà đều hỏng" và "155 chưa kiểm" tách riêng |

## Xem thử tại máy
Mở thẳng `index.html` bằng trình duyệt (nhấp đúp), chạy ngay, không cần cài gì.

## Đưa lên mạng cho trường xem (GitHub cá nhân → Vercel)
1. Tạo repo mới trên **GitHub cá nhân** (không phải tài khoản công ty), ví dụ `ra-soat-van-ban-demo`.
2. Đẩy 3 file này lên: `index.html`, **`data.enc`**, `README.md`.
   **Tuyệt đối không đẩy `data.js`**: đó là dữ liệu thô chưa mã hoá. Nó đã nằm trong `.gitignore`,
   đừng gỡ ra. Sinh `data.enc` bằng `PASSWORD='...' node encrypt-data.mjs` trước khi đẩy.
   ```bash
   cd docops-demo-truong
   git init && git add . && git commit -m "demo ra soat van ban"
   git branch -M main
   git remote add origin https://github.com/<tài-khoản-cá-nhân>/ra-soat-van-ban-demo.git
   git push -u origin main
   ```
3. Vào https://vercel.com → **Add New Project** → chọn repo vừa đẩy → **Deploy**.
   Vercel tự nhận là site tĩnh, không cần cấu hình. Có link `https://<tên>.vercel.app` để gửi trường.

> Không cần `vercel.json` hay build step. Vercel phục vụ trực tiếp `index.html`.

## Cổng đăng nhập (mã hoá)
Trang có cổng mật khẩu dùng chung. Dữ liệu **được mã hoá** thành `data.enc` (AES-GCM +
PBKDF2); trình duyệt chỉ giải mã được khi nhập đúng mật khẩu. Repo **không** chứa dữ liệu
thô và **không** chứa mật khẩu.

- File thô `data.js` để **cục bộ** (đã gitignore), chỉ dùng để sinh lại `data.enc`.
- **Đổi mật khẩu:** chạy `PASSWORD='mật-khẩu-mới' node encrypt-data.mjs` (sinh lại `data.enc`) rồi push.
- Cổng chạy được trên `https://` hoặc `localhost` (Web Crypto yêu cầu ngữ cảnh an toàn).

> Lưu ý: đây là cổng dùng chung, không phải hệ tài khoản. Ai có mật khẩu đều xem được.

## Cập nhật dữ liệu
`data.js` (cục bộ) sinh từ kết quả rà soát thật. Đổi số liệu thì cập nhật `data.js`, chạy lại
`encrypt-data.mjs`, rồi push `data.enc`.

## Ghi chú
- Không thu thập dữ liệu người dùng; toàn bộ chạy trong trình duyệt.
- Đây là bản trình bày; bản đầy đủ (nhập kho văn bản của trường, rà tự động, on-prem) là hệ thống có backend riêng.
