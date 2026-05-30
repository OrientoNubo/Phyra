FROM python:3.12-slim

# Ghostscript for lossy compression; curl/ca-certificates for arXiv + uv.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ghostscript curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# uv (package manager / runner)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY phyra_dualtrans ./phyra_dualtrans
RUN uv sync --frozen --no-dev

# BabelDOC models + SourceHan fonts (~340MB) are NOT baked into the image.
# Mount your warmed cache at runtime:
#   -v $HOME/.cache/babeldoc:/root/.cache/babeldoc
# The claude_cli backend is host-only; inside the container use openai/ollama.

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "phyra_dualtrans.web.app:app", \
     "--host", "0.0.0.0", "--port", "8000"]
