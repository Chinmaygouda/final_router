# AI Router Flowcharts

This document provides visual representations of the AI Router's internal architecture and feature workflows.

## 1. Overall System Architecture Flow

```mermaid
graph TD
    User([User Request]) --> API[FastAPI /ask endpoint]
    
    API --> RateLimit{Rate Limit Check}
    RateLimit -- Exceeded --> Error[429 Too Many Requests]
    RateLimit -- Pass --> Guardrails[Guardrails & PII]
    
    Guardrails -- Blocked --> Error2[400 Bad Request]
    Guardrails -- Safe --> CacheCheck{Semantic Vault Cache}
    
    CacheCheck -- Hit --> ReturnCache([Return Cached Response])
    CacheCheck -- Miss --> ContextBuilder[Build Context]
    
    ContextBuilder --> History[Append History]
    ContextBuilder --> Memory[Append User Memory]
    ContextBuilder --> Compressor[Prompt Compressor]
    
    Compressor --> Router[Intelligent Router]
    
    Router --> DeBERTa[DeBERTa-v3 Intent Classifier]
    DeBERTa --> Scoring[Filter & Score Models]
    Scoring --> Confidence{Confidence > Threshold?}
    
    Confidence -- Yes --> SelectedModel[Select Top Model]
    Confidence -- No --> Bandit[Thompson Sampling Bandit]
    Bandit --> SelectedModel
    
    SelectedModel --> Dispatcher[Dispatcher Engine]
    
    Dispatcher --> Execute{Provider API Call}
    Execute -- Success --> Output[AI Response]
    Execute -- Fail/429 --> Fallback[Cascading Fallback Chain]
    Fallback --> Execute
    
    Output --> Extractor[Memory Extractor]
    Extractor --> DB[(PostgreSQL)]
    Output --> ReturnNew([Return New Response])
```

## 2. Guardrails & Security Flow

```mermaid
graph TD
    Input([Raw Prompt]) --> RegexPII[Regex PII Scanner]
    RegexPII --> Redact[Redact Emails, Phones, SSN]
    
    Redact --> InjectScan[Prompt Injection Scanner]
    InjectScan -- Detected --> Block([Block Request])
    
    InjectScan -- Clean --> KeywordScan[Harmful Keyword Scanner]
    KeywordScan -- Detected --> Block
    
    KeywordScan -- Clean --> Output([Safe Redacted Prompt])
```

## 3. Intelligent Routing Flow

```mermaid
graph TD
    Input([Compressed Prompt]) --> LocalML[Local DeBERTa-v3]
    LocalML --> Intent(Determine Intent: CODE, CHAT, etc.)
    LocalML --> Complexity(Determine Complexity: 1.0 - 10.0)
    
    Intent --> DBQuery[Query PostgreSQL for Active Models]
    Complexity --> DBQuery
    
    DBQuery --> Filter[Filter by Tier & Rules]
    Filter --> Scorer[Score remaining models]
    
    Scorer --> Formula(Score = Tier Base - Cost Penalty - Complexity Distance)
    Formula --> Sort[Sort Top-K]
    
    Sort --> Confidence[Compute Confidence Gap]
    Confidence --> Select([Final Selected Model])
```

## 4. Cascading Fallback Engine

```mermaid
graph TD
    Fail([Primary Model Fails]) --> SameCat{Same Category Candidates?}
    SameCat -- Yes --> TrySame[Execute Next Model in Category]
    TrySame -- Success --> Success([Return Response])
    TrySame -- Fail --> SameCat
    
    SameCat -- No --> CrossCat{Cross Category Candidates?}
    CrossCat -- Yes --> TryCross[Execute Text-Only Models across DB]
    TryCross -- Success --> Success
    TryCross -- Fail --> CrossCat
    
    CrossCat -- No --> LastResort[Execute Hardcoded Safe Models]
    LastResort --> TrySafe[Execute Gemini 3/2.5 Flash]
    TrySafe -- Success --> Success
    TrySafe -- Fail --> Panic([System Failure 500])
```

## 5. User Memory Extraction Flow

```mermaid
graph TD
    Input([AI Response Output]) --> Regex[Regex Heuristics]
    
    Regex --> IDScan(Scan for 'I am', 'My name is')
    Regex --> PrefScan(Scan for 'I love', 'I hate', 'I prefer')
    
    IDScan --> Facts[List of Facts]
    PrefScan --> Facts
    
    Facts --> Dedupe{Fact already exists?}
    Dedupe -- Yes --> Update[Update Last Used / Importance]
    Dedupe -- No --> Save[(Save to PostgreSQL User Memory)]
```
