# LLM Derby

## Prerequisites

- [Rust](https://www.rust-lang.org/tools/install)
- [Foundry](https://book.getfoundry.sh/getting-started/installation)
- [Bun](https://bun.sh/docs/installation)
- [uv](https://github.com/astral-sh/uv)

## Setup

### Setup envs

```
cd contracts
cp .env.example .env
```

### Installation

```
cd agent
uv sync
```

```
cd contracts
bun install
```

```
cd web
pnpm install
```

### Running

```
pnpm dev
```