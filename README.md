```bash
docker run -v $(pwd):/data plantuml/plantuml -tsvg classes_grouped.puml
```
```bash
docker run -v $(pwd):/data plantuml/plantuml -tsvg classes_original.puml
```
```bash
uvx --from mcpdoc mcpdoc --urls FastMCP:https://gofastmcp.com/llms.txt --transport sse --port 8083 --host localhost
```

```json
{
  "servers": {
    "fast-mcp": {
      "command": "/home/ai/.local/bin/uvx",
      "args": [
        "--from",
        "mcpdoc",
        "mcpdoc",
        "--urls",
        "FastMCP:https://gofastmcp.com/llms.txt",
        "--transport",
        "stdio"
      ]
    }
  }
}
```