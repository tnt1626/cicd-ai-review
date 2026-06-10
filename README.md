![CI](https://github.com/tnt1626/cicd-ai-review/actions/workflows/ci.yml/badge.svg)

# 1. Project này làm gì?
- Xây dựng github action pipeline, bao gồm:
    + test
    + build a Docker image
    + deploy to a VPS
    + automatically post an ai-review comment on every pull request

# 2. Stack được sử dụng trong project
- FastAPI 
- Python
- pytest + Docker 
- GitHub Actions 
- Groq API 
- Nginx 
- Linux VPS

# 3. Project này giải quyết vấn đề gì
## 3.1 Những vấn đề mà CICD giải 
- Phát triển và triển khai thủ công, chậm chạp và dễ gặp lỗi
- Khi merge nhiều nhánh dễ tạo ra conflict
- Quy trình test và build code ở final stage dẫn đến bug tìm ra trễ
- Việc triển khai tốn nhiều thời gian

## 3.2 AI-review automatically đã giải quyết những gì
- Tóm tắt nội dung vừa được PR
- Nêu ra những điểm tốt và bug hoặc lỗi tìm ẩn của PR ở dòng nào và file 
- Đưa ra hướng cải tiến cho đoạn code vừa được PR (optional)

# 4. Phần nào khó nhất khi build
- Những nội dung liên quan đến máy ảo và mạng máy tính
    - Chưa được trang bị nhiều kiến thức liên quan đến mạng máy tính như: tường lửa, proxy, reverse proxy, ssl, http, https
> Tuy là nội dung cảm thấy khó nhất nhưng cũng mạng lại rất nhiều kiến thức và khiến mình cảm thấy rất hào hứng

- Lần đầu làm quen với github action nên khá lạ lẫm với cách viết và logic

# 5. Những nội dung đã học được sau project này
- Được thực hành nhiều hơn với Docker, DockerHub, Dockerfile, Docker CLI, đặc biệt là các image hoàn toàn mới...
- Biết về cách hoạt động của GitHub Action, set các secret và variables 
- Biết thêm nhiều nội dung hơn về Linux, đặc biệt là các nội dung liên quan đến hệ  (tôi đang sử dụng Linux nhưng chưa có cơ hội làm việc với Linux là 1 server)
- Được ôn lại kiến thức về backend (REST API, http methods, path, headers, media types,..) và test với pytest
- Biết cách setup cấu hình và tạo 1 VM instance với GCP, làm việc SSH public và private key
- Làm quen với các kiến thức về mạng máy tính: firewall, proxy, reverse proxy

# 6. Architecture Diagram

![Architecture Diagram](attachments/cicd_ai_review_architecture.svg)

# 7. How to run locally
1. Clone repository
```bash
git clone <repo-url>
cd cicd-ai-review
```

2. Install dependencies
```bash
uv sync
```

# 8. "How it workds" section and demo with screen shot

# 9. GitHub Secrets and how to set them up



