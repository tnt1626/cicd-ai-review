![CI](https://github.com/tnt1626/cicd-ai-review/actions/workflows/ci.yml/badge.svg)

# cicd-ai-review

A GitHub Actions pipeline that automatically tests, builds a Docker image, deploys to a GCP VM, and posts an AI-powered code review comment on every Pull Request using Llama 3 via Groq.

---

## Stack

| Layer | Tool |
|---|---|
| API | FastAPI + Python 3.13 |
| Test | pytest + httpx |
| Container | Docker + Docker Hub |
| CI/CD | GitHub Actions |
| AI | Groq API (Llama-3.3-70b-versatile) |
| Server | GCP e2-micro + Nginx + HTTPS (nip.io) |

---

## Architecture

![Architecture Diagram](attachments/cicd_ai_review_architecture.svg)

**Two independent flows run on every event:**

**Flow A — Pull Request:** When a PR is opened, the `ai-review` job generates a git diff, sends it to Llama 3 via Groq, and posts the review as a PR comment via the GitHub API.

**Flow B — Push to main:** When code is merged, the pipeline runs tests → builds and pushes a Docker image to Docker Hub → SSHs into the GCP VM and redeploys the container.

---

## How it works

### AI Code Review Bot

Every time you open a Pull Request:

1. GitHub Actions checks out the branch with full history
2. Generates a diff: `git diff origin/main...HEAD`
3. Sends the diff to Llama 3 (via Groq API) with a structured system prompt
4. Posts the review as a comment on the PR via the GitHub Issues API

The review follows a fixed format — summary, good practices, bugs, security issues, code quality, and optional suggestions.

*PR with bot comment triggered:*
![Bot comment overview](attachments/bot_comment_1.png)

*Full review — bugs, security, suggestions with file:line references:*
![Bot comment detail](attachments/bot_comment_2.png)

### CI/CD Pipeline

```
push to main
    │
    ├── test job       → pytest (Python 3.12, 3.13 matrix)
    │
    ├── build job      → docker build + push to Docker Hub (tagged with commit SHA)
    │
    └── deploy job     → SSH into GCP VM → docker pull → docker run
```

---

## How to run locally

**Prerequisites:** Python 3.13, `uv`, Docker, a Groq API key

```bash
# 1. Clone the repo
git clone https://github.com/tnt1626/cicd-ai-review.git
cd cicd-ai-review

# 2. Install dependencies
uv sync

# 3. Set environment variables
cp .env.example .env
# Fill in GROQ_API_KEY in .env

# 4. Run the app
uv run uvicorn src.main:app --reload

# 5. Run tests
uv run pytest

# 6. Test the AI review script locally
git diff main | uv run -m src.review --pr-number 1 --repo your-username/cicd-ai-review
```

---

## GitHub Secrets setup

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | How to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys |
| `GITHUB_TOKEN` | Auto-injected by GitHub Actions — no setup needed |
| `DOCKERHUB_USERNAME` | Your Docker Hub username (set as a **variable**, not secret) |
| `DOCKERHUB_TOKEN` | Docker Hub → Account Settings → Security → Access Tokens |
| `VPS_HOST` | External IP of your GCP VM (Compute Engine → VM Instances) |
| `VPS_KEY` | SSH private key — run `ssh-keygen -t ed25519 -C "gcp-deploy"` locally, paste the private key here |

---

## What I learned

This was a 2-week project built from scratch as a beginner to DevOps. The hardest parts were networking concepts (firewall, reverse proxy, SSL/HTTPS) and learning GitHub Actions syntax — both of which ended up being the most valuable things I took away.

- **Docker** — Dockerfile, Docker Hub, image tagging, container lifecycle
- **GitHub Actions** — multi-job pipelines, secrets, matrix strategy, conditional jobs
- **Linux server administration** — UFW firewall, user management, SSH keys
- **Networking** — reverse proxy with Nginx, HTTPS with Certbot/Let's Encrypt
- **Cloud infrastructure** — provisioning and configuring a GCP e2-micro VM (always-free tier)
- **AI integration** — Groq API, prompt engineering, GitHub REST API for automated comments

---

## Possible extensions

- [ ] Webhook server — support any repo without GitHub Actions setup
- [ ] Web dashboard — view review history and stats
- [ ] Terraform — provision the GCP VM with IaC instead of manual setup
- [ ] Kubernetes — replace `docker run` with a k8s deployment