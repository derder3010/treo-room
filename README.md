# Treo Room Discord Bot

Bot Discord tự động kết nối vào voice channel và cung cấp API để gửi tin nhắn.

## Tính năng

- Tự động tham gia và duy trì kết nối vào voice channel
- Gửi tin nhắn ngẫu nhiên từ file quotes.txt định kỳ
- Tích hợp với HuggingChat AI để tạo phản hồi tự động
- API endpoint để gửi tin nhắn thông qua HTTP request
- API endpoint để gửi tin nhắn trực tiếp (DM) cho người dùng cụ thể
- Hỗ trợ gửi tin nhắn có định dạng sử dụng Markdown

## Cài đặt

1. Cài đặt Python 3.7+
2. Clone repository này
3. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```
4. Cấu hình bot trong file `main.py`:

   - Cập nhật `TOKEN` bằng token Discord của bạn
   - Cập nhật `VOICE_CHANNEL_ID` bằng ID của voice channel
   - Cập nhật `API_KEY` bằng khóa bí mật tùy chọn
   - (Tùy chọn) Cập nhật thông tin HuggingChat

5. Chạy bot:
   ```
   python main.py
   ```

## Sử dụng API để gửi tin nhắn kênh (Channel)

Bot cung cấp API endpoint để gửi tin nhắn đến kênh Discord. Bạn có thể sử dụng API này để gửi tin nhắn từ các ứng dụng hoặc dịch vụ khác.

### Endpoint: `/api/send-message`

- **Method**: POST
- **URL**: `http://your-server:10000/api/send-message`
- **Headers**:

  - Content-Type: application/json

- **Body cơ bản (văn bản đơn giản)**:
  ```json
  {
    "api_key": "your_secret_api_key_here",
    "message": "Nội dung tin nhắn",
    "channel_id": 1360161250637647892 // Tùy chọn, mặc định sẽ dùng VOICE_CHANNEL_ID nếu không có
  }
  ```

## Sử dụng API để gửi tin nhắn trực tiếp (DM)

Bot cũng cung cấp API endpoint để gửi tin nhắn trực tiếp (Direct Message) đến một người dùng Discord cụ thể.

### Endpoint: `/api/send-dm`

- **Method**: POST
- **URL**: `http://your-server:10000/api/send-dm`
- **Headers**:

  - Content-Type: application/json

- **Body cơ bản (văn bản đơn giản)**:

  ```json
  {
    "api_key": "your_secret_api_key_here",
    "message": "Nội dung tin nhắn",
    "user_id": 123456789012345678 // ID người dùng Discord mà bạn muốn gửi DM
  }
  ```

- **Body với định dạng Markdown (thay thế cho embed)**:
  ```json
  {
    "api_key": "your_secret_api_key_here",
    "user_id": 123456789012345678,
    "embed": {
      "title": "Tiêu đề của tin nhắn",
      "description": "Mô tả chi tiết hơn",
      "thumbnail": "https://i.imgur.com/xyz789.png",
      "image": "https://i.imgur.com/def456.png",
      "fields": [
        {
          "name": "Tiêu đề mục",
          "value": "Nội dung mục"
        },
        {
          "name": "Tiêu đề mục khác",
          "value": "Nội dung mục khác"
        }
      ]
    }
  }
  ```

### Ví dụ tin nhắn "Chúc mừng" với định dạng Markdown

```json
{
  "api_key": "3010",
  "user_id": "123456789012345678",
  "embed": {
    "title": "Chúc mừng",
    "description": "Bạn đã đạt được hạng Master trong tháng này.",
    "thumbnail": "https://i.imgur.com/rank_icon.png"
  }
}
```

Tin nhắn này sẽ được hiển thị như sau:

```
> **Chúc mừng**
> Bạn đã đạt được hạng Master trong tháng này.
> [Thumbnail](https://i.imgur.com/rank_icon.png)
```

### Ví dụ gửi tin nhắn định dạng sử dụng cURL

```bash
curl -X POST http://your-server:10000/api/send-dm \
  -H "Content-Type: application/json" \
  -d '{
    "api_key":"3010",
    "user_id":"123456789012345678",
    "embed":{
      "title":"Chúc mừng",
      "description":"Bạn đã đạt được hạng Master trong tháng này.",
      "thumbnail":"https://i.imgur.com/rank_icon.png"
    }
  }'
```

### Ví dụ sử dụng Python (Requests)

```python
import requests
import json

url = "http://your-server:10000/api/send-dm"
payload = {
    "api_key": "your_secret_api_key_here",
    "user_id": "123456789012345678",
    "embed": {
        "title": "Chúc mừng",
        "description": "Bạn đã đạt được hạng Master trong tháng này.",
        "thumbnail": "https://i.imgur.com/rank_icon.png"
    }
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)
print(response.text)
```

## Định dạng Markdown hỗ trợ

Discord hỗ trợ các định dạng Markdown sau:

- **In đậm**: `**text**`
- _In nghiêng_: `*text*`
- ~~Gạch ngang~~: `~~text~~`
- `Code`: `` `text` ``
- `Code block`: ` ```text``` `
- > Trích dẫn: `> text`
- Liên kết: `[text](https://example.com)`

## Phản hồi API

- Thành công gửi tin nhắn kênh:

  ```json
  {
    "success": true,
    "message": "Message queued for delivery"
  }
  ```

- Thành công gửi DM:

  ```json
  {
    "success": true,
    "message": "DM sent to Username#1234"
  }
  ```

- Lỗi API key không hợp lệ (401):

  ```json
  {
    "error": "Unauthorized"
  }
  ```

- Lỗi thiếu thông tin tin nhắn (400):

  ```json
  {
    "error": "Either message or embed is required"
  }
  ```

- Lỗi thiếu ID người dùng khi gửi DM (400):

  ```json
  {
    "error": "User ID is required"
  }
  ```

- Lỗi không tìm thấy người dùng (404):

  ```json
  {
    "error": "User not found in any mutual servers. Make sure you share a server with this user."
  }
  ```

- Lỗi không thể gửi tin nhắn cho người dùng (403):

  ```json
  {
    "error": "Cannot send DM to this user. They may have DMs disabled."
  }
  ```

## Các lưu ý

- Đảm bảo firewall cho phép kết nối đến cổng 10000
- Thay đổi `API_KEY` trong file `main.py` để tăng cường bảo mật
- Bot sẽ tự động kết nối lại vào voice channel nếu mất kết nối
- Để gửi DM, bạn cần biết chính xác ID người dùng Discord
- Lưu ý rằng một số người dùng Discord có thể tắt tính năng nhận tin nhắn trực tiếp từ các bot hoặc người dùng không phải bạn bè
