# AI-to-Animated-Game-Asset Pipeline (FastAPI)

Ứng dụng gồm backend FastAPI + web UI đơn giản để:
1. Upload ảnh nhân vật 2D.
2. Tách nền (chỗ tích hợp Gemini API).
3. Sinh hoạt ảnh theo các action idle/walk/attack/hurt (chỗ tích hợp Banana/Replicate).
4. Hậu xử lý thành spritesheet + metadata.json.
5. Tải về file ZIP.

## Chạy local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Mở: `http://127.0.0.1:8000`

## API

### `POST /api/build`
Multipart form:
- `image`: file ảnh
- `character_name`
- `style_prompt`
- `actions` (`idle,walk,attack,hurt`)
- `frame_width`, `frame_height`, `frames_per_action`
- `tags`

### `GET /api/download/{job_id}`
Tải ZIP output.

## Ghi chú tích hợp API thật
- `app/services/ai_clients.py` đang chứa fallback demo để chạy offline.
- Bạn có thể thay bằng gọi Gemini và Banana/Replicate thực tế trong 2 method:
  - `GeminiClient.segment_character`
  - `VideoGenerationClient.generate_action_clip`
