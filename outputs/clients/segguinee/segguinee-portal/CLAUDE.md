@AGENTS.md

## graphify

A persistent knowledge graph of this codebase lives in `graphify-out/`.
Before answering codebase questions or making changes, check the graph:

```bash
python3.11 -c "
import json
from pathlib import Path
from networkx.readwrite import json_graph
import networkx as nx
data = json.loads(Path('graphify-out/graph.json').read_text())
G = json_graph.node_link_graph(data, edges='links')
print(f'{G.number_of_nodes()} nodes, {G.number_of_edges()} edges')
"
```

**God nodes** (most connected — touch carefully):
1. `atList()` — 40 edges — every API route depends on this
2. `atCreate()` — 24 edges — all POST endpoints write through this
3. `sendMessage()` — 15 edges — WhatsApp delivery for invoices, alerts, briefings
4. `atUpdate()` — 9 edges — invoice signing, status updates
5. `routeMessage()` — 8 edges — webhook message router

**Communities**:
- Dashboard Shell — `src/app/dashboard-client.tsx` (all UI panels)
- Airtable Client — `src/lib/airtable.ts` (ALL data flows through here)
- Invoice API — `src/app/api/data/invoices/` + WhatsApp send
- WhatsApp Webhook — `src/app/api/webhook/whatsapp/` + AI router
- Auth & Login — `src/app/login/` + `src/middleware.ts`

**No import cycles detected.**

After every code change, the git hook auto-rebuilds the graph.
To update manually: `python3.11 -m graphify src --update`
To query: `python3.11 -m graphify query "how does invoice creation work"`
