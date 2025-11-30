# Port Mapping Reference

Complete list of all ports used in the SingHack system to avoid conflicts.

## Port Allocation

| Service | Port | Purpose |
|---------|------|---------|
| **Master Agent Server** | **9000** | Main FastAPI orchestration server |
| DynamoDB Local | 8000 | Payments database |
| DynamoDB Admin UI | 8010 | Database management interface |
| Payment Pages | 8085 | Success/cancel pages |
| Stripe Webhook | 8086 | Payment webhook handler |
| Classifier Agent (Reserved) | 8001 | Query classification service |
| Predict Agent (Reserved) | 8002 | Insurance recommendations |
| Risk Agent (Reserved) | 8003 | Risk assessment service |
| PostgreSQL | 5432 | Claims database |

## Configuration

### Master Agent Defaults
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `9000`
- **Override**: Set `MASTER_AGENT_PORT` in `.env`

### Chrome Extension Configuration
```javascript
const CONFIG = {
    MASTER_AGENT_URL: 'http://localhost:9000',
    USE_MASTER_AGENT: true
};
```

### Specialized Agents (Future)
```python
AGENT_URLS = {
    'classifier': 'http://localhost:8001',
    'predict': 'http://localhost:8002',
    'risk': 'http://localhost:8003',
}
```

## Start Commands

```bash
# Master Agent
python -m master_agent.server  # Default: port 9000

# Payments Stack
cd Payments
docker-compose up -d  # 8000, 8010, 8085, 8086
```

## Port Conflicts

If a port is in use:

```bash
# Windows
netstat -ano | findstr :9000

# Mac/Linux
lsof -i :9000

# Change port in .env
MASTER_AGENT_PORT=9001
```

## Testing

```bash
# Master Agent
curl http://localhost:9000/health

# DynamoDB
curl http://localhost:8000  # Payments DB

# Webhook
curl http://localhost:8086/health

# Payment Pages
curl http://localhost:8085/health
```










