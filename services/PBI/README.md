# Power BI — Odoo PostgreSQL connection

`R1` contains an import-mode diagnostic table named `Odoo Database Objects`.
It connects to the PostgreSQL database used by the local Odoo simulator and
lists the Odoo tables visible in the `public` schema.

## Connection parameters

| Parameter | Default | Purpose |
|---|---|---|
| `OdooServer` | `localhost` | PostgreSQL host reachable from Power BI Desktop |
| `OdooPort` | `5433` | Host port published by the Odoo Compose stack |
| `OdooDatabase` | `fmcg_erp` | Odoo database name |

When Power BI Desktop runs in a Windows VM, set `OdooServer` to the Linux host
IP address reachable from that VM. Keep port `5433` unless the Compose port
mapping is changed.

## First refresh

1. Start the Odoo PostgreSQL stack.
2. Open `R1.pbip` in Power BI Desktop.
3. Open **Transform data > Edit parameters** and update `OdooServer` when needed.
4. Refresh the model.
5. When prompted, choose **Database** authentication and enter a PostgreSQL
   account that has read-only access to the Odoo database.

Credentials are intentionally not stored in the PBIP project. A successful
refresh returns one row per visible Odoo table. This diagnostic table can be
removed after the business tables and analytics model are defined.
