# Server Port Assignments

## Current Port Allocation

| Port | Service | Status |
|------|---------|--------|
| 8004 | Decision Agent | ✅ Active |
| 8005 | Speech to Text | ✅ Active |
| 8006 | Policy Eligibility Scanner | ✅ Active |
| 8007 | PDF Extractor | ✅ Active |
| 8008 | Insights Agent | ✅ Active |
| 8009 | Quotation API | ✅ Active |
| 8020 | **Summary Agent** | ✅ **NEW** |
| 9000 | Master Agent | ✅ Active |

## Port Conflict Resolution

### ⚠️ Original Conflict
- Summary Agent was initially set to port **8006**
- Port 8006 is already used by **Policy Eligibility Scanner**

### ✅ Resolution
- Summary Agent moved to port **8020**
- No conflicts detected

## Environment Variables

Update your `.env` file:

```bash
# Decision Agent
DECISION_AGENT_PORT=8004

# Speech to Text
SPEECH_TO_TEXT_PORT=8005

# Policy Eligibility Scanner
POLICY_ELIGIBILITY_PORT=8006

# PDF Extractor
PDF_EXTRACTOR_PORT=8007

# Insights Agent
INSIGHTS_AGENT_PORT=8008

# Quotation API
QUOTATION_API_PORT=8009

# Summary Agent (NEW)
SUMMARY_AGENT_PORT=8020

# Master Agent
MASTER_AGENT_PORT=9000
```

## Quick Health Checks

```bash
# Decision Agent
curl http://localhost:8004/health

# Speech to Text
curl http://localhost:8005/health

# Policy Eligibility Scanner
curl http://localhost:8006/health

# PDF Extractor
curl http://localhost:8007/health

# Insights Agent
curl http://localhost:8008/health

# Quotation API
curl http://localhost:8009/health

# Summary Agent (NEW)
curl http://localhost:8020/health

# Master Agent
curl http://localhost:9000/health
```

## Start All Servers

```bash
# Terminal 1 - Decision Agent
python Server/start_decision_agent.py

# Terminal 2 - Speech to Text
python Server/start_speech_to_text.py

# Terminal 3 - Policy Eligibility Scanner
python Server/start_policy_eligibility_scanner.py

# Terminal 4 - PDF Extractor
python Server/start_pdf_extractor.py

# Terminal 5 - Insights Agent
python Server/start_insights_agent.py

# Terminal 6 - Quotation API
python Server/start_quotation_api.py

# Terminal 7 - Summary Agent (NEW)
python Server/start_summary_agent.py

# Terminal 8 - Master Agent
python Server/start_master_agent.py
```

## Reserved Ports

The following ports are available for future services:

- 8010-8019
- 8021-8999
- 9001-9999

## Notes

- All services use localhost/0.0.0.0
- Ports can be changed via environment variables
- Always check this file before assigning new ports
- Update this file when adding new services


