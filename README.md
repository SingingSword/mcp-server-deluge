# Deluge MCP Server

MCP Server per gestire Deluge tramite API JSON-RPC.

## Setup

```bash
# Le dipendenze sono già installate nel venv

# IMPORTANTE: Configura le variabili d'ambiente
export DELUGE_URL=https://your-deluge-server.com/json
export DELUGE_PASSWORD=your_password_here

# Oppure crea/modifica .env
echo "DELUGE_URL=https://your-deluge-server.com/json" > .env
echo "DELUGE_PASSWORD=your_password_here" >> .env

# Test server
./server.py
```

## Integrazione con Q CLI

Aggiungi al file di configurazione MCP di Q CLI (`~/.config/q/mcp_servers.json`):

```json
{
  "mcpServers": {
    "deluge": {
      "command": "/home/enrico/Sorgenti/mcp-server-deluge/server.py",
      "args": [],
      "env": {
        "DELUGE_URL": "https://your-deluge-server.com/json",
        "DELUGE_PASSWORD": "your_password_here"
      }
    }
  }
}
```

Oppure usa il comando Q CLI:
```bash
q mcp add deluge /home/enrico/Sorgenti/mcp-server-deluge/server.py
```

## Integrazione con Kiro

Aggiungi al file di configurazione Kiro (`~/.config/kiro/mcp_servers.json`):

```json
{
  "servers": {
    "deluge": {
      "command": "/home/enrico/Sorgenti/mcp-server-deluge/server.py",
      "args": [],
      "env": {
        "DELUGE_URL": "https://your-deluge-server.com/json",
        "DELUGE_PASSWORD": "your_password_here"
      }
    }
  }
}
```

## Funzioni disponibili

- `list_torrents()` - Lista tutti i torrent con stato e velocità
- `add_magnet(magnet_uri)` - Aggiunge torrent via magnet link
- `pause_torrent(torrent_id)` - Mette in pausa un torrent
- `resume_torrent(torrent_id)` - Riprende un torrent in pausa
- `remove_torrent(torrent_id, remove_data=False)` - Rimuove torrent (± file)
- `get_deluge_stats()` - Statistiche del daemon Deluge

## Esempi d'uso

```bash
# In Q CLI o Kiro
list_torrents()
add_magnet("magnet:?xt=urn:btih:...")
pause_torrent("torrent_id_here")
resume_torrent("torrent_id_here")
remove_torrent("torrent_id_here", true)  # rimuove anche i file
get_deluge_stats()
```

## Troubleshooting

- Verifica che Deluge Web UI sia accessibile
- Controlla le credenziali in `.env`
- Assicurati che il virtual environment sia attivo
- Testa la connessione con `python -c "import requests; print(requests.get('https://your-deluge-server.com').status_code)"`
