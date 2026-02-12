# 🏗️ Théoria - Architecture Technique

Ce document décrit l'architecture cloud de Théoria, conçue pour être **cost-effective**, **scalable** et **résiliente**.

---

## 📐 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   macOS App     │  │   Web Dashboard │  │   Mobile (fut)  │             │
│  │  (Electron/Swift│  │    (React/Vue)  │  │                 │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│           └────────────────────┼────────────────────┘                       │
│                                │                                            │
│                         HTTPS/WSS                                          │
└────────────────────────────────┼────────────────────────────────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────────────┐
│                           CDN / DNS                                          │
│                      (CloudFlare / Render)                                   │
└────────────────────────────────┼────────────────────────────────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────────────┐
│                         RENDER.COM PLATFORM                                  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Load Balancer                               │   │
│  │              (SSL Termination + Health Checks)                      │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│  ┌───────────────────────────────┼─────────────────────────────────────┐   │
│  │                    API SERVICE (Docker)                             │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │   │
│  │  │   Instance 1    │  │   Instance 2    │  │   Instance N    │    │   │
│  │  │   ┌─────────┐   │  │   ┌─────────┐   │  │   ┌─────────┐   │    │   │
│  │  │   │ FastAPI │   │  │   │ FastAPI │   │  │   │ FastAPI │   │    │   │
│  │  │   │  + Uvicorn│  │  │   │  + Uvicorn│  │  │   │  + Uvicorn│   │    │   │
│  │  │   └────┬────┘   │  │   └────┬────┘   │  │   └────┬────┘   │    │   │
│  │  │        │        │  │        │        │  │        │        │    │   │
│  │  │   ┌────┴────┐   │  │   ┌────┴────┐   │  │   ┌────┴────┐   │    │   │
│  │  │   │ Mistral │   │  │   │ Mistral │   │  │   │ Mistral │   │    │   │
│  │  │   │ Client  │   │  │   │ Client  │   │  │   │ Client  │   │    │   │
│  │  │   └─────────┘   │  │   └─────────┘   │  │   └─────────┘   │    │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │   │
│  │                              ▲                                     │   │
│  │                              │ Auto-scaling (2-10 instances)      │   │
│  └──────────────────────────────┼─────────────────────────────────────┘   │
│                                 │                                          │
│  ┌──────────────────────────────┴─────────────────────────────────────┐   │
│  │                         DATA LAYER                                  │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────┐    ┌─────────────────────────┐        │   │
│  │  │    PostgreSQL 16        │    │     Redis 7             │        │   │
│  │  │  ┌─────────────────┐    │    │  ┌─────────────────┐    │        │   │
│  │  │  │  Multi-Tenant   │    │    │  │   Sessions      │    │        │   │
│  │  │  │  Users          │◄───┼────┼──┤   Cache         │    │        │   │
│  │  │  │  Subscriptions  │    │    │  │   Rate Limit    │    │        │   │
│  │  │  │  Audio Metadata │    │    │  │   Job Queue     │    │        │   │
│  │  │  └─────────────────┘    │    │  └─────────────────┘    │        │   │
│  │  │        ▲                │    │                         │        │   │
│  │  │        │ Multi-AZ       │    │                         │        │   │
│  │  │   ┌────┴────┐           │    │                         │        │   │
│  │  │   │ Standby │           │    │                         │        │   │
│  │  │   └─────────┘           │    │                         │        │   │
│  │  └─────────────────────────┘    └─────────────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  Mistral AI     │  │   AWS S3        │  │  Logtail/       │             │
│  │  (Transcription)│  │ (Audio Storage) │  │  BetterStack    │             │
│  │                 │  │                 │  │  (Monitoring)   │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Principes Architecturaux

### 1. Multi-Tenancy (Shared Database + Row-Level Isolation)

```sql
-- Chaque table contient un tenant_id
CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,  -- ← Isolation multi-tenant
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

-- Index pour performance
CREATE INDEX idx_users_tenant ON users(tenant_id);

-- RLS (Row Level Security) - PostgreSQL
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

**Avantages:**
- ✅ Coût bas (une seule DB)
- ✅ Simplicité opérationnelle
- ✅ Facilement migrable vers schema-per-tenant plus tard

### 2. High Availability (Multi-AZ)

```
┌────────────────────────────────────────────────────────────┐
│                     Availability Zone 1                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  API Server  │    │  PostgreSQL  │    │    Redis     │ │
│  │   Primary    │◄──►│   Primary    │◄──►│   Primary    │ │
│  └──────────────┘    └──────┬───────┘    └──────────────┘ │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │ Replication
                              ▼
┌────────────────────────────────────────────────────────────┐
│                     Availability Zone 2                     │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │  API Server  │    │  PostgreSQL  │                      │
│  │  Standby     │◄──►│   Standby    │                      │
│  └──────────────┘    └──────────────┘                      │
│                            ▲                               │
│                            │ Failover automatique         │
└────────────────────────────┴───────────────────────────────┘
```

**RPO**: 0 (synchronous replication)  
**RTO**: < 60 secondes (Render managed)

### 3. Auto-Scaling

```python
# Stratégie de scaling Render.com
scaling_config = {
    "min_instances": 2,        # HA minimum
    "max_instances": 10,       # Protection coût
    "target_cpu": 70,          # Scale out si CPU > 70%
    "target_memory": 80,       # Scale out si RAM > 80%
    "scale_in_cooldown": 600,  # 10 min avant scale-in
    "scale_out_cooldown": 60,  # 1 min avant scale-out
}
```

**Déclencheurs:**
- CPU > 70% pendant 2 minutes
- Memory > 80% pendant 2 minutes
- Request queue > 100 requêtes
- Latence p99 > 500ms

---

## 🗄️ Schéma de Données

### Tables Principales

```sql
-- Tenants (pour futur multi-tenant complet)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',  -- free, pro, enterprise
    created_at TIMESTAMP DEFAULT NOW(),
    settings JSONB DEFAULT '{}'
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),  -- NULL pour OAuth-only
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    email_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,  -- hashed token
    name VARCHAR(255),
    scopes JSONB DEFAULT '["transcribe"]',  -- permissions
    rate_limit_per_minute INT DEFAULT 60,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP
);

-- Transcriptions
CREATE TABLE transcriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    
    -- Audio metadata
    original_filename VARCHAR(500),
    audio_duration_seconds DECIMAL(10,2),
    audio_size_bytes BIGINT,
    audio_format VARCHAR(10),  -- wav, mp3, m4a
    
    -- Transcription results
    raw_transcript TEXT,
    structured_text TEXT,
    language_detected VARCHAR(10),
    
    -- Processing metadata
    model_used VARCHAR(100),
    processing_time_ms INT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Usage Metrics (pour billing)
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE CASCADE,
    
    -- Usage data
    action VARCHAR(50),  -- transcribe, structure
    audio_duration_seconds DECIMAL(10,2),
    tokens_input INT,
    tokens_output INT,
    
    -- Cost tracking
    estimated_cost_usd DECIMAL(10,6),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes pour performance
CREATE INDEX idx_transcriptions_user ON transcriptions(user_id, created_at DESC);
CREATE INDEX idx_transcriptions_status ON transcriptions(status) WHERE status = 'processing';
CREATE INDEX idx_usage_logs_user_date ON usage_logs(user_id, created_at);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
```

---

## 🔒 Sécurité

### Architecture de Sécurité

```
┌─────────────────────────────────────────────────────────────┐
│                        PÉRIMÈTRE                             │
│  • HTTPS uniquement (TLS 1.3)                               │
│  • CloudFlare / Render SSL                                  │
│  • Rate limiting par IP + API key                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION                             │
│  • Authentication: API Key (header X-API-Key)               │
│  • Authorization: RBAC (scopes par clé API)                 │
│  • Input validation: Pydantic schemas                       │
│  • CORS: Origins whitelist                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DONNÉES                                │
│  • Encryption at rest: PostgreSQL native (AES-256)          │
│  • Encryption in transit: TLS 1.3                           │
│  • Row-Level Security pour isolation multi-tenant           │
│  • No plaintext secrets in code/logs                        │
└─────────────────────────────────────────────────────────────┘
```

### Rate Limiting

```python
# Configuration Redis-based rate limiting
rate_limits = {
    "free": {"requests_per_minute": 10, "audio_per_day": 50},
    "pro": {"requests_per_minute": 60, "audio_per_day": 1000},
    "enterprise": {"requests_per_minute": 300, "audio_per_day": None},
}
```

---

## 📊 Flow de Requête

### Transcription Audio

```
1. Client ──POST /v1/transcribe──► API Gateway (Render)
                                    │
                                    ▼
2.                         [Rate Limit Check]
                              Redis INCR key
                                    │
                    ┌───────────────┴───────────────┐
                    │ Rate limit OK                 │ Rate limit exceeded
                    ▼                               ▼
3.           [Auth Check]                    429 Too Many Requests
              API Key validation
                    │
        ┌───────────┴───────────┐
        │ Key valid             │ Key invalid
        ▼                       ▼
4.  [File Upload]           401 Unauthorized
     Validate size/type
     Save temp file
        │
        ▼
5.  [Process Audio]
    ├──► Call Mistral API
    ├──► Structure text (si demandé)
    └──► Save results DB
        │
        ▼
6.  [Response]
    {
      "transcript": "...",
      "text": "...",  // structured
      "processing_time_ms": 1234
    }
        │
        ▼
7.  [Cleanup]
    ├──► Delete temp file
    ├──► Log usage metrics
    └──► Update rate limit counters
```

---

## 💰 Estimation des Coûts

### Phase MVP (0-1000 users)

| Service | Provider | Plan | Coût/mois |
|---------|----------|------|-----------|
| API Server | Render | Starter (512MB) | $7 |
| PostgreSQL | Render | Starter (256MB) | $0 (inclus) |
| Redis | Render | Starter (256MB) | $0 (inclus) |
| Mistral API | Mistral | Pay-as-you-go | ~$20-50 |
| Monitoring | Logtail | Free tier | $0 |
| **Total** | | | **~$30-60/mois** |

### Phase Growth (1000-10000 users)

| Service | Provider | Plan | Coût/mois |
|---------|----------|------|-----------|
| API Server | Render | Standard (2GB) × 2 | $50 |
| PostgreSQL | Render | Standard (4GB) | $25 |
| Redis | Render | Standard (5GB) | $20 |
| Mistral API | Mistral | Volume pricing | ~$200-500 |
| Monitoring | Logtail | Pro | $20 |
| CDN | CloudFlare | Pro | $20 |
| **Total** | | | **~$350-650/mois** |

---

## 🚀 Roadmap Technique

### Phase 1: MVP (Actuel)
- [x] API FastAPI basique
- [x] PostgreSQL + Redis
- [x] Déploiement Render
- [ ] Tests automatisés
- [ ] Rate limiting

### Phase 2: Beta
- [ ] Authentification OAuth2
- [ ] WebSocket pour streaming temps réel
- [ ] File d'attente de jobs (Celery + Redis)
- [ ] Dashboard web
- [ ] Webhooks

### Phase 3: Scale
- [ ] Migration vers AWS/GCP
- [ ] Kubernetes (EKS/GKE)
- [ ] CDN global
- [ ] Analytics avancés
- [ ] Machine Learning personnalisé

---

## 📝 Décisions d'Architecture (ADRs)

### ADR-001: Hébergement sur Render.com
**Statut**: Accepté

**Contexte**: Besoin de déployer rapidement avec peu d'ops

**Décision**: Utiliser Render.com pour le MVP

**Conséquences**:
- ✅ Déploiement en 5 minutes
- ✅ SSL, backups, monitoring inclus
- ✅ Scaling simple
- ❌ Vendor lock-in
- ❌ Moins de contrôle qu'AWS

### ADR-002: Multi-tenancy Shared Database
**Statut**: Accepté

**Contexte**: MVP B2C avec coûts contrôlés

**Décision**: Shared DB + row-level tenant_id

**Conséquences**:
- ✅ Coût minimal
- ✅ Simple à gérer
- ⚠️ Migration plus complexe si besoin de isolation stricte

---

## 🔗 Ressources

- [Render.com Docs](https://render.com/docs)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
