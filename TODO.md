# TODO List for `sentiment_data` Repository

This document outlines all pending tasks and enhancement ideas for bringing the `sentiment_data` repository to MVP and beyond.

---

## ✅ MVP Completion Tasks

- [ ] **Implement Sentiment Pollers**
  - [ ] Twitter/X sentiment integration
  - [ ] Reddit sentiment scraping (via Pushshift or praw)
  - [ ] News headline sentiment (via FinBERT or HuggingFace models)
  - [ ] Finviz or MarketWatch headline sentiment

- [ ] **Standardize Sentiment Schema**
  - Define unified payload format (e.g., source, symbol, sentiment_score, text_sample, timestamp)

- [ ] **Implement Message Queue Integration**
  - [ ] RabbitMQ support
  - [ ] SQS fallback support
  - [ ] Abstracted `QueueSender` with retries and logging

- [ ] **Vault Secret Integration**
  - Load API keys and credentials from Vault
  - Support fallback to environment variables

---

## 🔁 Data Handling Enhancements

- [ ] **Rate Limiting and Retry Logic**
  - Implement `RateLimiter` utility
  - Add exponential backoff with `retry_request`

- [ ] **Sentiment Scoring Models**
  - [ ] Integrate VADER for short social posts
  - [ ] Integrate FinBERT for financial headlines
  - [ ] Explore zero-shot classification models for unknown sources

---

## 📊 Slack & Alerting

- [ ] **Slack Notification Support**
  - [ ] Send alerts for new sentiment spikes
  - [ ] Notify on polling failures (with cooldowns)
  - [ ] Add toggle for Slack via config

---

## 💾 Caching & Storage

- [ ] **Implement Local Caching (Optional)**
  - Prevent double-fetching or rate-limit burn from identical queries

- [ ] **Store Sentiment Results (Optional)**
  - Dump to JSONL or SQLite for future offline analysis

---

## ⚙️ Configuration & Environment

- [ ] Use `config.py` to abstract all configuration (Vault + env fallback)
- [ ] Enforce presence of required values using `validate_environment_variables`

---

## 🧪 Testing & CI/CD

- [ ] Add pytest unit tests for:
  - [ ] Each poller
  - [ ] Retry behavior
  - [ ] QueueSender integrations
- [ ] Add GitHub Actions for:
  - [ ] Linting
  - [ ] Pytest
  - [ ] Pre-commit
- [ ] Add pre-commit hooks:
  - [ ] Black
  - [ ] Ruff
  - [ ] Mypy
  - [ ] Bandit
  - [ ] Safety

---

## 🚀 Performance Optimizations

- [ ] Optimize network calls with async (if rate limits permit)
- [ ] Add profiling hooks to pollers for long-term optimization

---

## 🧠 Future Considerations

- [ ] Multi-language sentiment analysis support
- [ ] Sentiment trend time-series emitter
- [ ] WebSocket support for real-time delivery

---

_Keep this file up to date as features evolve. Structure PRs around closing checklist items._
