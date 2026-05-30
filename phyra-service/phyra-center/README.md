# phyra-center

The **landing page / hub** for the Phyra suite — a tiny zero-dependency
WebUI that lists every sibling service (论文庫、翻譯、未來 tools…) as
clickable tiles, with live "online / offline" indicators.

```
phyra-proj/
├── Phyra/                      # the Claude Code research plugin
└── phyra-center/               # this repo — the hub (:8035)
    ├── script/
    │   ├── server.py           # zero-dep stdlib HTTP server
    │   └── start.sh            # one-shot boot for Center + archbase + dualtrans
    ├── static/
    │   ├── index.html          # the landing page
    │   └── styles.css          # tokens / typography copied from sibling pages
    ├── phyra-archbase/         # → see ./phyra-archbase/README.MD   (:8037)
    └── phyra-dualtrans/        # → see ./phyra-dualtrans/README.md  (:8039)
```

## Quick start — boot everything

```bash
script/start.sh
```

One command:

1. **Regenerates** `phyra-archbase/index.html` (so its "← 返回 Phyra
   Center" banner bakes in the right port).
2. Boots `phyra-archbase` on `:8037`, `phyra-dualtrans` on `:8039`,
   then `phyra-center` itself on `:8035`.
3. Waits for Center's `/healthz`, opens your browser to
   `http://localhost:8035/`.
4. Tails all three logs to your terminal (line-prefixed with the
   service name).
5. `Ctrl+C` cleanly stops all three.

Env knobs (all optional):

| Var | Default | Notes |
|---|---|---|
| `CT_PORT` | `8035` | Center landing-page port. Baked into archbase + dualtrans banners. |
| `AB_PORT` | `8037` | archbase port. |
| `DT_PORT` | `8039` | dualtrans port (also baked into the "save to archive" wiring). |
| `HOST` | `0.0.0.0` | Bind address. `127.0.0.1` for localhost-only. |
| `NO_BROWSER` | unset | Set to `1` to skip auto-opening the browser. |
| `PHYRA_ARCHBASE_ADMIN_PASSWORD` | unset | archbase delete password (unset = delete disabled). Tags are always editable. |

## Center alone

If you just want the landing page without booting the others:

```bash
PORT=8035 python3 script/server.py
```

It serves `static/` plus three tiny endpoints:

- `GET /healthz` → `{"ok": true, "version": "…"}` — readiness probe used by `start.sh`.
- `GET /api/services` → `[{kind, name, port, reachable, latency_ms, …}]` — live state for every known sibling. Probed with stdlib `urllib` against `127.0.0.1`; a dead sibling becomes `reachable:false`, never raises.
- `GET /api/center` → `{"port": <PORT>}` — sibling banners hit this so the "← 返回 Phyra Center" link can build the right URL when running over LAN.

## Why a hub at all?

Before `phyra-center`, archbase's index page doubled as the landing page
(and bore a "📝 雙語翻譯 DualTrans →" banner). That coupled
"the archive UI" with "the project's front door" — making each new
sibling tool a wiring problem (where does its banner go? what links to
what?). With Center as a real first-class page:

- Each sibling service has a single "← 返回 Phyra Center" banner; the
  cross-link mesh disappears.
- New tools just need a tile entry in `script/server.py`'s `SERVICES`
  list — no other code touches.
- The landing page is the only thing that needs to know about every
  sibling; siblings only need to know about Center.

## Visual style

Color tokens, typography, theme-toggle pattern and `:root` /
`[data-theme="dark"]` CSS variables are copied **verbatim** from
`phyra-archbase` / `phyra-dualtrans`. The three pages share one visual
language — light/dark theme choices persist per-app via `localStorage`
keys (`phyra-center-theme`, `phyra-archbase-theme`, `phyra-dualtrans-theme`).

## Security

The server binds `0.0.0.0` and has no auth — same posture as the rest of
Phyra: run on a trusted network, or bind localhost only:

```bash
HOST=127.0.0.1 script/start.sh
```

The landing page exposes **no secrets** and only probes localhost on the
sibling ports — it never proxies, never reads sibling state files.

## License

Apache-2.0 (matches `phyra-dualtrans`).
