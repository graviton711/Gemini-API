# Hướng dẫn Deploy lên Vercel

Dưới đây là các bước để đưa API này lên Vercel miễn phí.

## Bước 1: Chuẩn bị
1.  Đảm bảo bạn đã có tài khoản [GitHub](https://github.com/) và [Vercel](https://vercel.com/).
2.  Đẩy toàn bộ code trong thư mục này lên một repository mới trên GitHub.

## Bước 2: Deploy
1.  Đăng nhập vào **Vercel Dashboard**.
2.  Bấm nút **"Add New..."** -> **"Project"**.
3.  Chọn repository GitHub bạn vừa tạo -> Bấm **Import**.
4.  Ở màn hình "Configure Project":
    *   **Framework Preset**: Chọn **Other**.
    *   **Root Directory**: Để mặc định (`./`).
    *   **Environment Variables** (Cấu hình Key và Database):
        *   **GEMINI_API_KEYS** (Bắt buộc): Nhập danh sách key của bạn, cách nhau bằng dấu phẩy.
            *   Ví dụ: `AIzaSy...1,AIzaSy...2,AIzaSy...3`
        *   **FIREBASE_SERVICE_ACCOUNT** (Tùy chọn): Copy nội dung file `serviceAccountKey.json` để lưu database lâu dài.
5.  Bấm **Deploy**.

## Bước 3: Tắt bảo vệ (Quan trọng)
Mặc định Vercel sẽ khóa API lại. Bạn cần mở nó ra:
1.  Vào **Settings** -> **Deployment Protection**.
2.  Mục **Vercel Authentication**: Chọn **Disabled**.
3.  Bấm **Save**.

## Bước 4: Sử dụng
Sau khi deploy xong, Vercel sẽ cấp cho bạn một tên miền (ví dụ: `gemini-proxy.vercel.app`).

Thay thế URL trong code của bạn:
```python
# Cũ (Local)
client = genai.Client(http_options={'base_url': 'http://localhost:8000'})

# Mới (Vercel)
client = genai.Client(http_options={'base_url': 'https://gemini-proxy.vercel.app'})
```

Chúc mừng! Bạn đã có API riêng online 24/7.
