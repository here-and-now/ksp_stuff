#!/usr/bin/env bash
# Compile kspstuffKerbalism.dll. Does NOT install into GameData.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
KSP="${KSP:-$HOME/Games/KSP-rss}"
MANAGED="$KSP/KSP_Data/Managed"
OUT="$ROOT/kspstuffKerbalism.dll"

refs=(
  "-r:$MANAGED/Assembly-CSharp.dll"
  "-r:$MANAGED/UnityEngine.dll"
  "-r:$MANAGED/UnityEngine.CoreModule.dll"
  "-r:$KSP/GameData/Kerbalism/Kerbalism.dll"
  "-r:$KSP/GameData/000_Harmony/0Harmony.dll"
  "-r:System.dll"
  "-r:System.Core.dll"
)

mcs -nologo -t:library -sdk:4.5 -out:"$OUT" "${refs[@]}" "$ROOT"/src/*.cs
echo "built $OUT"
# never copy to GameData from this script
ls -l "$OUT"
