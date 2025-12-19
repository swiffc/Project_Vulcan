# System Architecture: The Universal Connector

This diagram visualizes the strictly hierarchical control flow: **Render -> Tailscale -> MCP Server -> Apps**.

```mermaid
graph TD
    %% Styling
    classDef cloud fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef vpn fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef local fill:#fff3e0,stroke:#ef6c00,stroke-width:4px;
    classDef app fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef agent fill:#bbdefb,stroke:#1565c0,stroke-width:1px,stroke-dasharray: 5 5;

    subgraph CLOUD ["☁️ CLOUD (Render)"]
        User([User UI])
        
        subgraph BRAIN ["🧠 CrewAI Orchestrator"]
            TA[Trading Agent]
            CA[CAD Agent]
        end
        
        User ==> BRAIN
    end

    subgraph TUNNEL ["🔒 SECURE VPN"]
        VPN[Tailscale Tunnel]
    end

    subgraph PC ["💻 LOCAL PC"]
        MCPServer[⚡ MCP SERVER / WRAPPER]
        
        subgraph APPS ["Controlled Apps"]
            SW[SolidWorks]
            TV[TradingView]
        end
    end

    %% Connections
    BRAIN ==>|JSON Request| VPN
    VPN ==>|Forward| MCPServer
    
    %% The Critical Branching
    MCPServer ==>|COM API| SW
    MCPServer ==>|PyAutoGUI| TV

    %% Agent Logic
    TA -.->|Analyze| TV
    CA -.->|Design| SW

    class User,BRAIN cloud;
    class TA,CA agent;
    class VPN vpn;
    class MCPServer local;
    class SW,TV app;
```

### Key Components

1.  **Cloud (Render)**:
    *   Hosts the **Intelligence** (LLMs, Agents).
    *   Runs 24/7.
    *   No access to your physical devices *except* via the tunnel.

2.  **The Tunnel (Tailscale)**:
    *   Makes your local PC appear as if it's "on the same wifi" as the Cloud Server.
    *   Zero public ports opened on your router (Safe!).

3.  **Local Desktop Server (The MCP Endpoint)**:
    *   **The Guard**: Checks the Kill Switch and Circuit Breaker.
    *   **The Translator**: Converts "Make a Box" (AI Speak) into `SketchManager.CreateCornerRectangle(0,0,0, 10,10,0)` (CAD Speak).
    *   **The Queue**: Ensures your PC does one thing at a time.

### 🔒 Security Note: No Direct Connection
*   **SolidWorks & TradingView Stay Local**: They do **NOT** connect to Render or the Internet directly.
*   **The Proxy Pattern**: Render talks *only* to the Python Script (`server.py`). The Script then talks to the Apps.
*   **Why?**: This means hackers cannot touch your TradingView or CAD files. Use the server as a "bouncer."
