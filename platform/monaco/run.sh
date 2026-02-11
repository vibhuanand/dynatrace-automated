#!/usr/bin/env bash
set -euo pipefail

MANIFEST_PATH="${MANIFEST_PATH:-platform/monaco/manifest.yaml}"
MONACO_VERSION="${MONACO_VERSION:-v2.28.1}"
MONACO_BIN="${MONACO_BIN:-.tools/monaco/monaco}"

[[ -f "$MANIFEST_PATH" ]] || { echo "manifest not found: $MANIFEST_PATH"; exit 2; }

os="$(uname -s | tr "[:upper:]" "[:lower:]")"
arch="$(uname -m)"
case "$arch" in x86_64|amd64) arch="amd64" ;; arm64|aarch64) arch="arm64" ;; *) echo "arch not supported: $arch"; exit 2 ;; esac
case "$os" in linux) asset="monaco-linux-$arch" ;; darwin) asset="monaco-darwin-$arch" ;; *) echo "os not supported: $os"; exit 2 ;; esac
[[ "$MONACO_VERSION" == v* ]] || MONACO_VERSION="v${MONACO_VERSION}"

base="https://github.com/Dynatrace/dynatrace-configuration-as-code/releases/download/${MONACO_VERSION}"

download() { curl -fsSL "$1" -o "$2"; }

verify_sha() {
  local bin="$1" sha="$2"
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$(dirname "$bin")" && sha256sum -c "$(basename "$sha")")
  elif command -v shasum >/dev/null 2>&1; then
    local expected actual
    expected="$(cut -d" " -f1 "$sha")"
    actual="$(shasum -a 256 "$bin" | awk "{print \$1}")"
    [[ "$expected" == "$actual" ]]
  else
    return 0
  fi
}

if [[ ! -x "$MONACO_BIN" ]]; then
  tmp="$(mktemp -d)"; trap "rm -rf $tmp" EXIT
  download "${base}/${asset}" "${tmp}/monaco"
  download "${base}/${asset}.sha256" "${tmp}/monaco.sha256"
  chmod +x "${tmp}/monaco"
  verify_sha "${tmp}/monaco" "${tmp}/monaco.sha256" || { echo "sha failed"; exit 2; }
  mkdir -p "$(dirname "$MONACO_BIN")"
  mv "${tmp}/monaco" "$MONACO_BIN"
fi

: "${DT_ENV_URL:?DT_ENV_URL required}"
: "${DT_PLATFORM_TOKEN:?DT_PLATFORM_TOKEN required}"

cmd=("$MONACO_BIN" deploy "$MANIFEST_PATH")

[[ "${MONACO_DRY_RUN:-false}" == "true" ]] && cmd+=("--dry-run")
[[ -n "${MONACO_GROUP:-}" ]] && cmd+=("--group" "$MONACO_GROUP")
[[ -n "${MONACO_ENVIRONMENT:-}" ]] && cmd+=("--environment" "$MONACO_ENVIRONMENT")
[[ -n "${MONACO_PROJECT:-}" ]] && cmd+=("--project" "$MONACO_PROJECT")

exec "${cmd[@]}"
