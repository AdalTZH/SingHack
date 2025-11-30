# Agentic Architecture Diagram

This document contains Mermaid diagrams visualizing the agentic design of the SingHack Backend system.

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        CE[Chrome Extension]
    end
    
    subgraph "Orchestration Layer"
        MA[Master Agent<br/>Port: 9000<br/>Orchestrator]
        DA[Decision Agent<br/>Port: 8004<br/>Page Analysis]
    end
    
    subgraph "Specialized Agents"
        CA[Classifier Agent<br/>Query Classification]
        PA[Predict Agent<br/>Insurance Recommendations]
        RA[Risk Agent<br/>Port: 8003<br/>Risk Assessment]
    end
    
    subgraph "Data Layer"
        DB[(Claims Database)]
        TAX[Taxonomy JSON]
        MCP[MCP Tools<br/>Weather/Disasters]
    end
    
    %% Client to Orchestration
    CE -->|Chat Queries| MA
    CE -->|Page Sync Data| DA
    
    %% Decision Agent Flow
    DA -->|Insurance Prompt Needed| MA
    DA -.->|Skip if Payment Page| CE
    
    %% Master Agent Routing
    MA -->|Route Query| ROUTE{Query Router}
    
    %% Routing Decisions
    ROUTE -->|Insurance Plans| PA
    ROUTE -->|Risk Questions| RA
    ROUTE -->|Compare/Explain| CA
    ROUTE -->|Direct Response| MA
    
    %% Agent Responses
    PA -->|Recommendations| MA
    RA -->|Risk Assessment| MA
    CA -->|Classification + Product Rec| MA
    
    %% Data Dependencies
    PA --> DB
    CA --> TAX
    RA --> MCP
    
    %% Final Response
    MA -->|Synthesized Response| CE
    
    style MA fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    style DA fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style CA fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style PA fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style RA fill:#ffebee,stroke:#b71c1c,stroke-width:2px
```

## Agent Workflow Detail

```mermaid
sequenceDiagram
    participant User
    participant Extension as Chrome Extension
    participant DecisionAgent as Decision Agent
    participant MasterAgent as Master Agent
    participant Router as Query Router
    participant Classifier as Classifier Agent
    participant Predict as Predict Agent
    participant Risk as Risk Agent
    
    %% Page Sync Flow
    rect rgb(255, 250, 240)
        note over User,DecisionAgent: Page Sync Analysis Flow
        User->>Extension: Browse Travel Page
        Extension->>DecisionAgent: POST /analyze (URL, Title, HTML)
        DecisionAgent->>DecisionAgent: Analyze Page Content
        alt Insurance Prompt Needed
            DecisionAgent->>MasterAgent: Forward Insurance Prompt
            MasterAgent->>Extension: Insurance Recommendation
        else Skip (Payment Page)
            DecisionAgent->>Extension: No Prompt
        end
    end
    
    %% Chat Query Flow
    rect rgb(240, 255, 255)
        note over User,MasterAgent: Chat Query Flow
        User->>Extension: Send Chat Message
        Extension->>MasterAgent: POST /chat (message, history)
        MasterAgent->>Router: Route Query
        
        alt Insurance Plan Query
            Router->>Predict: Get Recommendations
            Predict->>Predict: Analyze Claims Data
            Predict->>MasterAgent: Product Recommendations
        else Risk Assessment Query
            Router->>Risk: Assess Risks
            Risk->>Risk: Check Weather/Disasters/Advisories
            Risk->>MasterAgent: Risk Assessment
        else Compare/Explain Query
            Router->>Classifier: Classify Query
            Classifier->>Classifier: Extract Entities<br/>Classify Type<br/>Recommend Product
            Classifier->>MasterAgent: Classification + Recommendation
        end
        
        MasterAgent->>MasterAgent: Synthesize Response
        MasterAgent->>Extension: Final Response
        Extension->>User: Display Response
    end
```

## Master Agent Routing Logic

```mermaid
flowchart TD
    START([User Query]) --> INPUT{Receive Query}
    
    INPUT --> ROUTE[Route Query Node]
    
    ROUTE --> CHECK{Query Pattern Match}
    
    CHECK -->|"recommend/best plan/suitable"| PREDICT[Predict Agent<br/>Insurance Recommendations]
    CHECK -->|"risk/danger/safe/advisory/disaster"| RISK[Risk Agent<br/>Weather & Disaster Assessment]
    CHECK -->|"compare/which/better/difference"| CLASSIFY[Classifier Agent<br/>Query Classification]
    CHECK -->|"explain/what/how/tell me"| CLASSIFY
    CHECK -->|"general queries"| CLASSIFY
    CHECK -->|"other"| DIRECT[Direct Response]
    
    PREDICT --> SYNTH[Synthesize Response]
    RISK --> SYNTH
    CLASSIFY --> SYNTH
    DIRECT --> SYNTH
    
    SYNTH --> RESPONSE[Final Response to User]
    
    RESPONSE --> END([End])
    
    style PREDICT fill:#e8f5e9
    style RISK fill:#ffebee
    style CLASSIFY fill:#f3e5f5
    style SYNTH fill:#e1f5ff
```

## Classifier Agent Workflow

```mermaid
graph LR
    START([Query Input]) --> EXTRACT[Extract Entities<br/>- Products<br/>- Benefits<br/>- Keywords]
    
    EXTRACT --> CLASSIFY[Classify Query<br/>- Comparison<br/>- Explanation<br/>- Eligibility<br/>- Scenario Analysis]
    
    CLASSIFY --> VALIDATE[Validate Classification<br/>- Check Confidence<br/>- Add Metadata]
    
    VALIDATE --> RECOMMEND[Recommend Product<br/>- Product A/B/C<br/>- Reasoning]
    
    RECOMMEND --> END([Return Result])
    
    style EXTRACT fill:#fff9c4
    style CLASSIFY fill:#e1bee7
    style VALIDATE fill:#c5e1a5
    style RECOMMEND fill:#ffccbc
```

## Decision Agent Analysis Flow

```mermaid
flowchart TD
    START([Page Sync Data]) --> CHECK[Check if Stripe Payment Page]
    
    CHECK -->|Is Payment Page| SKIP[Skip Analysis<br/>No Prompt]
    
    CHECK -->|Not Payment Page| ANALYZE[Analyze Page with LLM]
    
    ANALYZE --> DECIDE{Decision Logic}
    
    DECIDE -->|Travel Related?| TRAVEL{Insurance Needed?}
    DECIDE -->|Not Travel Related| NO_PROMPT[should_prompt: false]
    
    TRAVEL -->|Yes| CONFIDENCE{Confidence ≥ Threshold?}
    TRAVEL -->|No| NO_PROMPT
    
    CONFIDENCE -->|Yes| PROMPT[should_prompt: true<br/>Generate Insurance Prompt]
    CONFIDENCE -->|No| NO_PROMPT
    
    PROMPT --> FORWARD[Forward to Master Agent]
    NO_PROMPT --> END([End])
    SKIP --> END
    FORWARD --> END
    
    style PROMPT fill:#c8e6c9
    style NO_PROMPT fill:#ffccbc
    style SKIP fill:#ffcdd2
```

## Component Interaction

```mermaid
graph TB
    subgraph "Entry Points"
        CE[Chrome Extension]
    end
    
    subgraph "API Endpoints"
        MA_API[Master Agent API<br/>POST /chat<br/>POST /speech-to-text]
        DA_API[Decision Agent API<br/>POST /analyze]
        RA_API[Risk Agent API<br/>POST /assess]
    end
    
    subgraph "Core Agents"
        MA_CORE[Master Agent Core<br/>LangGraph Workflow]
        DA_CORE[Decision Agent Core<br/>Page Analysis Logic]
        CA_CORE[Classifier Agent<br/>LangGraph Classification]
        PA_CORE[Predict Agent<br/>Claims Data Analysis]
        RA_CORE[Risk Agent<br/>MCP Tools Integration]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API<br/>LLM + Whisper]
        MCP_TOOLS[MCP Tools<br/>Weather APIs<br/>Travel Advisories]
    end
    
    CE --> MA_API
    CE --> DA_API
    
    MA_API --> MA_CORE
    DA_API --> DA_CORE
    
    MA_CORE --> CA_CORE
    MA_CORE --> PA_CORE
    MA_CORE --> RA_CORE
    
    DA_CORE --> MA_CORE
    
    CA_CORE --> OPENAI
    DA_CORE --> OPENAI
    MA_CORE --> OPENAI
    RA_CORE --> MCP_TOOLS
    
    style MA_CORE fill:#e1f5ff
    style DA_CORE fill:#fff3e0
    style CA_CORE fill:#f3e5f5
```

## Port Allocation

```mermaid
graph LR
    subgraph "Server Ports"
        P9000[Port 9000<br/>Master Agent]
        P8004[Port 8004<br/>Decision Agent]
        P8003[Port 8003<br/>Risk Agent]
    end
    
    subgraph "Internal Agents"
        CA[Classifier Agent<br/>No Port<br/>Direct Import]
        PA[Predict Agent<br/>No Port<br/>Direct Import]
    end
    
    P9000 -.->|Calls| CA
    P9000 -.->|Calls| PA
    P9000 -->|HTTP| P8003
    
    style P9000 fill:#01579b,color:#fff
    style P8004 fill:#e65100,color:#fff
    style P8003 fill:#b71c1c,color:#fff
```

## Data Flow

```mermaid
graph TB
    subgraph "User Input"
        QUERY[User Query]
        PAGE[Page Content]
    end
    
    subgraph "Processing"
        ROUTE[Route & Classify]
        ANALYZE[Analyze & Extract]
        RECOMMEND[Generate Recommendations]
    end
    
    subgraph "Data Sources"
        DB[(Claims Database)]
        TAX[Taxonomy]
        API[External APIs]
    end
    
    subgraph "Output"
        RESPONSE[Final Response]
    end
    
    QUERY --> ROUTE
    PAGE --> ANALYZE
    
    ROUTE --> ANALYZE
    ANALYZE --> RECOMMEND
    
    RECOMMEND --> DB
    RECOMMEND --> TAX
    RECOMMEND --> API
    
    DB --> RESPONSE
    TAX --> RESPONSE
    API --> RESPONSE
    
    style QUERY fill:#e3f2fd
    style RESPONSE fill:#c8e6c9
```









