#!/usr/bin/env bash
# Compile KRPC.RealAntennas.dll. Does NOT install into GameData.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
KSP="${KSP:-$HOME/Games/KSP-rss}"
MANAGED="$KSP/KSP_Data/Managed"
KRPC="$KSP/GameData/kRPC"
RA="$KSP/GameData/RealAntennas/Plugins"
OUT="$ROOT/KRPC.RealAntennas.dll"

refs=(
  "-r:$MANAGED/Assembly-CSharp.dll"
  "-r:$MANAGED/UnityEngine.dll"
  "-r:$MANAGED/UnityEngine.CoreModule.dll"
  "-r:$MANAGED/UnityEngine.UI.dll"
  "-r:$MANAGED/UnityEngine.PhysicsModule.dll"
  "-r:$MANAGED/UnityEngine.IMGUIModule.dll"
  "-r:$KRPC/KRPC.dll"
  "-r:$KRPC/KRPC.Core.dll"
  "-r:$KRPC/KRPC.SpaceCenter.dll"
  "-r:$RA/RealAntennas.dll"
  "-r:System.dll"
  "-r:System.Core.dll"
)

mcs -nologo -t:library -sdk:4.5 -out:"$OUT" "${refs[@]}" "$ROOT"/src/*.cs
echo "built $OUT"
# never copy to GameData from this script
ls -l "$OUT"
