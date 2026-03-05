# src/gui/d3_viewer.py
from __future__ import annotations

import json
import sys
from typing import Any
import webview

HTML = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>Stable Matching Replay</title>

<style>
:root{
  --bg:#0b0f14;
  --panel:#0f1620;
  --line:#1f2a37;
  --text:#e6edf3;
  --muted:#9aa4b2;
  --res:#4cc9f0;
  --hos:#f72585;
  --edge:#e6edf3;
  --proposal:#ffd166;
  --bad:#ff4d4f;
  --good:#22c55e;
  --active:#ffffff;
}

*{ box-sizing:border-box; }

body{
  margin:0;
  background:var(--bg);
  color:var(--text);
  font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  overflow:hidden;
}

/* Top controls */
#top{
  height:58px;
  padding:8px 10px;
  border-bottom:1px solid var(--line);
  display:flex;
  gap:10px;
  align-items:center;
  justify-content:space-between;
  background:var(--panel);
}

#leftControls{
  display:flex;
  gap:6px;
  align-items:center;
  flex-wrap:wrap;
}

button{
  padding:6px 10px;
  border:1px solid var(--line);
  background:#111b27;
  color:var(--text);
  border-radius:9px;
  cursor:pointer;
  font-size:13px;
}
button:hover{ filter:brightness(1.08); }
button:active{ transform:translateY(1px); }

.pill{
  padding:5px 10px;
  border:1px solid var(--line);
  border-radius:999px;
  font-size:12px;
  color:var(--muted);
}

#speedWrap{
  display:flex;
  align-items:center;
  gap:8px;
  color:var(--muted);
  font-size:12px;
}
input[type="range"]{ width:140px; }

/* Main layout */
#main{
  display:grid;
  grid-template-columns: 1fr 220px;
  height: calc(100vh - 58px);
  min-height:0;
}

#vizWrap{
  position:relative;
  min-width:0;
  min-height:0;
  border-right:1px solid var(--line);
  overflow-y:scroll;
  overflow-x:hidden;
}

#vizWrap::-webkit-scrollbar{
  width:10px;
}

#vizWrap::-webkit-scrollbar-thumb{
  background:#243244;
  border-radius:999px;
}

#vizWrap::-webkit-scrollbar-track{
  background:transparent;
}

#viz{
  display:block;
  background:var(--bg);
}

/* Right panel */
#sidePanel{
  background:var(--panel);
  padding:10px;
  display:flex;
  flex-direction:column;
  min-height:0;
  overflow:hidden;
}

.panelTitle{
  font-size:11px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--muted);
  margin-bottom:8px;
  flex:0 0 auto;
}

#matchList{
  display:flex;
  flex-direction:column;
  gap:6px;
  overflow-y:auto;
  overflow-x:hidden;
  min-height:0;
  padding-right:2px;
}

#matchList::-webkit-scrollbar{
  width:8px;
}
#matchList::-webkit-scrollbar-thumb{
  background:#243244;
  border-radius:999px;
}
#matchList::-webkit-scrollbar-track{
  background:transparent;
}

.matchItem{
  border:1px solid var(--line);
  border-radius:10px;
  padding:8px 10px;
  background:#111b27;
  font-size:13px;
  line-height:1.25;
  flex:0 0 auto;
}

.matchItem .pair{
  font-weight:700;
  color:var(--text);
  word-break:break-word;
}

.matchItem.added{
  border-color: rgba(34,197,94,0.65);
  color: var(--good);
  box-shadow: 0 0 0 1px rgba(34,197,94,0.18) inset;
}

.matchItem.added .pair{
  color: var(--good);
}

.matchItem.removed{
  border-color: rgba(255,77,79,0.65);
  color: var(--bad);
  box-shadow: 0 0 0 1px rgba(255,77,79,0.18) inset;
}

.matchItem.removed .pair{
  color: var(--bad);
}

.matchSub{
  margin-top:3px;
  font-size:11px;
  color:var(--muted);
}

.matchItem.removed .matchSub{
  color: var(--bad);
}

.emptyState{
  color:var(--muted);
  font-size:13px;
  border:1px dashed var(--line);
  border-radius:10px;
  padding:10px;
}

#moveBar{
  position:fixed;
  left:10px;
  right:230px;
  bottom:10px;
  padding:10px 12px;
  border:1px solid var(--line);
  background:rgba(15,22,32,0.92);
  border-radius:12px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.35);
  z-index:1000;
}

#moveTitle{
  font-size:10px;
  letter-spacing:0.16em;
  text-transform:uppercase;
  color:var(--muted);
  margin-bottom:4px;
}

#moveText{
  font-size:17px;
  font-weight:700;
  color:var(--text);
  line-height:1.2;
}

/* Nodes / edges */
circle.res{ fill:var(--res); }
circle.hos{ fill:var(--hos); }

circle.res.exhausted{
  fill: var(--bad);
}

circle.activeRing{
  fill:none;
  stroke:var(--active);
  stroke-width:3;
  opacity:0;
}

circle.activeRing.visible{
  opacity:1;
}

text{
  fill:var(--text);
  font-size:13px;
}

text.resLabel.exhausted{
  fill: var(--bad);
  font-weight:700;
}

line.edge{
  stroke:var(--edge);
  stroke-width:3.2;
  opacity:0.92;
}

/* Overlay action lines */
line.action{
  stroke-width:3;
  opacity:0.98;
}
line.action.proposal{
  stroke: var(--proposal);
  stroke-dasharray: 7 5;
}
line.action.reject{
  stroke: var(--bad);
  stroke-dasharray: 7 5;
}
</style>

<script src="https://d3js.org/d3.v7.min.js"></script>
</head>

<body>

<div id="top">
  <div id="leftControls">
    <button id="btnPlay">Play</button>
    <button id="btnStep">Step</button>
    <button id="btnBack">Back</button>
    <button id="btnReset">Reset</button>
    <span class="pill" id="stepInfo">t=0</span>
  </div>

  <div id="speedWrap">
    <span>Speed</span>
    <input id="speed" type="range" min="40" max="900" value="220"/>
  </div>
</div>

<div id="main">
  <div id="vizWrap">
    <svg id="viz"></svg>

    <div id="moveBar">
      <div id="moveTitle">CURRENT MOVE</div>
      <div id="moveText">Ready. Press Step.</div>
    </div>
  </div>

  <div id="sidePanel">
    <div class="panelTitle">Current Matches</div>
    <div id="matchList"></div>
  </div>
</div>

<script>
window.__EVENTS__ = __EVENTS_JSON__;
</script>

<script>
let events = window.__EVENTS__ || [];
let t = 0;
let timer = null;

let residents = [];
let hospitals = [];
let capacity = {};
let held = {}; // h -> Set(residents)
let exhausted = new Set();

let activeResident = null;

/*
matchFlash maps "R|H" -> "added" | "removed"
This is transient per currently displayed step.
*/
let matchFlash = new Map();

/*
removedPairs stores recently removed pairs so the panel can show:
R3 — H1 (removed)
for one step.
*/
let removedPairs = [];

let svg = null;

function setStepInfo(){
  document.getElementById("stepInfo").textContent =
    `t=${t}/${Math.max(0, events.length-1)}`;
}

function setMove(msg){
  document.getElementById("moveText").textContent = msg;
}

function ensureD3(){
  if (typeof d3 === "undefined"){
    setMove("ERROR: D3 failed to load.");
    return false;
  }
  svg = d3.select("#viz");
  return true;
}

function pairKey(r, h){
  return `${r}|${h}`;
}

function clearTransientMatchState(){
  matchFlash = new Map();
  removedPairs = [];
}

function initFromStart(startEv){
  residents = startEv.residents || [];
  hospitals = startEv.hospitals || [];
  capacity = startEv.capacity || {};

  held = {};
  hospitals.forEach(h => held[h] = new Set());

  exhausted = new Set();
  activeResident = null;
  clearTransientMatchState();

  drawStatic();
  renderMatchPanel();

  t = 0;
  setStepInfo();
  setMove(`Loaded events: ${events.length}. Press Step.`);
}

function resetReplay(){
  pause();
  document.getElementById("btnPlay").textContent = "Play";
  const startEv = events.find(e => e && e.type === "start");
  if (!startEv) return;
  initFromStart(startEv);
}

function drawStatic(){
  const wrap = document.getElementById("vizWrap");
  const width = wrap.clientWidth;
  const viewportHeight = wrap.clientHeight;

  const leftX = Math.max(110, Math.floor(width * 0.20));
  const rightX = Math.min(width - 110, Math.floor(width * 0.80));

  const topPad = 48;
  const bottomPad = 95;

  const maxCount = Math.max(residents.length, hospitals.length);
  const minHeight = maxCount * 40 + topPad + bottomPad;
  const height = Math.max(viewportHeight, minHeight);

  svg.attr("width", width).attr("height", height);
  svg.selectAll("*").remove();

  const yRes = d3.scalePoint()
    .domain(residents)
    .range([topPad, height - bottomPad])
    .padding(0.5);

  const yHos = d3.scalePoint()
    .domain(hospitals)
    .range([topPad, height - bottomPad])
    .padding(0.5);

  const defs = svg.append("defs");

  defs.append("marker")
    .attr("id", "arrowProposal")
    .attr("viewBox", "0 -4 8 8")
    .attr("refX", 8)
    .attr("refY", 0)
    .attr("markerWidth", 5)
    .attr("markerHeight", 5)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-4L8,0L0,4")
    .attr("fill", "#ffd166");

  defs.append("marker")
    .attr("id", "arrowReject")
    .attr("viewBox", "0 -4 8 8")
    .attr("refX", 8)
    .attr("refY", 0)
    .attr("markerWidth", 5)
    .attr("markerHeight", 5)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-4L8,0L0,4")
    .attr("fill", "#ff4d4f");

  // Residents group
  const resG = svg.append("g").attr("id", "residents");

  resG.selectAll("circle.activeRing")
    .data(residents).enter().append("circle")
    .attr("class","activeRing")
    .attr("cx", leftX).attr("cy", d => yRes(d))
    .attr("r", 14);

  resG.selectAll("circle.res")
    .data(residents).enter().append("circle")
    .attr("class","res")
    .attr("cx", leftX).attr("cy", d => yRes(d))
    .attr("r", 11);

  resG.selectAll("text.res")
    .data(residents).enter().append("text")
    .attr("class","resLabel")
    .attr("x", leftX - 20).attr("y", d => yRes(d)+4)
    .attr("text-anchor","end")
    .text(d => d);

  // Hospitals
  svg.append("g").selectAll("circle.hos")
    .data(hospitals).enter().append("circle")
    .attr("class","hos")
    .attr("cx", rightX).attr("cy", d => yHos(d))
    .attr("r", 13);

  svg.append("g").selectAll("text.hos")
    .data(hospitals).enter().append("text")
    .attr("x", rightX + 16).attr("y", d => yHos(d)+4)
    .attr("text-anchor","start")
    .text(d => `${d} (cap ${capacity[d] ?? 0})`);

  svg.append("g").attr("id","edges");
  svg.append("g").attr("id","overlay");

  svg.node().__yRes = yRes;
  svg.node().__yHos = yHos;
  svg.node().__leftX = leftX;
  svg.node().__rightX = rightX;

  renderEdges();
  clearActionLine();
  updateExhaustedStyles();
  updateActiveResidentStyles();
}

function updateExhaustedStyles(){
  svg.selectAll("circle.res")
    .classed("exhausted", d => exhausted.has(d));

  svg.selectAll("text.resLabel")
    .classed("exhausted", d => exhausted.has(d));
}

function updateActiveResidentStyles(){
  svg.selectAll("circle.activeRing")
    .classed("visible", d => activeResident === d);
}

function renderEdges(){
  const yRes = svg.node().__yRes;
  const yHos = svg.node().__yHos;
  const leftX = svg.node().__leftX;
  const rightX = svg.node().__rightX;

  const edges = [];
  for (const h of hospitals){
    for (const r of held[h]){
      edges.push({r, h});
    }
  }

  const g = svg.select("#edges");
  const sel = g.selectAll("line.edge").data(edges, d => d.r + "->" + d.h);

  sel.enter().append("line")
    .attr("class","edge")
    .attr("x1", leftX).attr("y1", d => yRes(d.r))
    .attr("x2", rightX).attr("y2", d => yHos(d.h));

  sel
    .attr("x1", leftX).attr("y1", d => yRes(d.r))
    .attr("x2", rightX).attr("y2", d => yHos(d.h));

  sel.exit().remove();
}

function clearActionLine(){
  svg.select("#overlay").selectAll("line.action").remove();
}

function drawActionLine(kind, r, h){
  const yRes = svg.node().__yRes;
  const yHos = svg.node().__yHos;
  const leftX = svg.node().__leftX;
  const rightX = svg.node().__rightX;

  clearActionLine();

  let x1, y1, x2, y2, marker;
  if (kind === "proposal"){
    x1 = leftX;  y1 = yRes(r);
    x2 = rightX; y2 = yHos(h);
    marker = "url(#arrowProposal)";
  } else {
    x1 = rightX; y1 = yHos(h);
    x2 = leftX;  y2 = yRes(r);
    marker = "url(#arrowReject)";
  }

  svg.select("#overlay").append("line")
    .attr("class", `action ${kind}`)
    .attr("x1", x1).attr("y1", y1)
    .attr("x2", x2).attr("y2", y2)
    .attr("marker-end", marker);
}

function getCurrentPairs(){
  const pairs = [];
  for (const h of hospitals){
    for (const r of held[h]){
      pairs.push({r, h, removed:false});
    }
  }

  removedPairs.forEach(p => {
    pairs.push({r:p.r, h:p.h, removed:true});
  });

  pairs.sort((a, b) => {
    if (a.h !== b.h) return a.h.localeCompare(b.h);
    return a.r.localeCompare(b.r);
  });

  return pairs;
}

function renderMatchPanel(){
  const container = document.getElementById("matchList");
  const pairs = getCurrentPairs();

  if (pairs.length === 0){
    container.innerHTML = `<div class="emptyState">No current matches yet.</div>`;
    return;
  }

  container.innerHTML = pairs.map(p => {
    const key = pairKey(p.r, p.h);
    const flash = matchFlash.get(key);
    const klass = flash ? `matchItem ${flash}` : "matchItem";
    const removedText = p.removed ? " <span class=\"matchSub\">(removed)</span>" : "";
    const subText = flash === "added"
      ? `<div class="matchSub">new match</div>`
      : flash === "removed"
        ? `<div class="matchSub">(removed)</div>`
        : `<div class="matchSub">stable so far</div>`;

    return `
      <div class="${klass}">
        <div class="pair">${p.r} — ${p.h}${p.removed ? ' (removed)' : ''}</div>
        ${subText}
      </div>
    `;
  }).join("");
}

function applyEvent(ev){
  if (!ev || !ev.type) return;

  clearTransientMatchState();

  if (ev.type === "proposal"){
    activeResident = ev.r;
    updateActiveResidentStyles();
    drawActionLine("proposal", ev.r, ev.h);
    setMove(`Proposal: ${ev.r} → ${ev.h}`);
  }
  else if (ev.type === "reject"){
    activeResident = ev.r;
    updateActiveResidentStyles();
    drawActionLine("reject", ev.r, ev.h);
    setMove(`Reject: ${ev.r} ← ${ev.h} (${ev.reason})`);
  }
  else if (ev.type === "hold_add"){
    held[ev.h].add(ev.r);
    matchFlash.set(pairKey(ev.r, ev.h), "added");
    renderEdges();
    clearActionLine();
    renderMatchPanel();
    setMove(`Hold: ${ev.h} accepts ${ev.r}`);
  }
  else if (ev.type === "kick"){
    held[ev.h].delete(ev.kicked);
    removedPairs.push({r: ev.kicked, h: ev.h});
    matchFlash.set(pairKey(ev.kicked, ev.h), "removed");
    renderEdges();
    drawActionLine("reject", ev.kicked, ev.h);
    renderMatchPanel();
    setMove(`Kick: ${ev.h} removes ${ev.kicked}`);
  }
  else if (ev.type === "exhausted"){
    activeResident = ev.r;
    exhausted.add(ev.r);
    updateActiveResidentStyles();
    updateExhaustedStyles();
    clearActionLine();
    renderMatchPanel();
    setMove(`Exhausted: ${ev.r} has no more choices`);
  }
  else if (ev.type === "finish"){
    activeResident = null;
    updateActiveResidentStyles();
    clearActionLine();
    renderMatchPanel();
    setMove(`Finished in ${ev.elapsedMs} ms`);
  }
  else if (ev.type === "pop_free"){
    activeResident = ev.r;
    updateActiveResidentStyles();
    clearActionLine();
    renderMatchPanel();
    setMove(`Pick: ${ev.r}`);
  }
  else if (ev.type === "requeue"){
    activeResident = ev.r;
    updateActiveResidentStyles();
    clearActionLine();
    renderMatchPanel();
    setMove(`Requeue: ${ev.r} (${ev.reason})`);
  }
  else if (ev.type === "skip_already_matched"){
    activeResident = ev.r;
    updateActiveResidentStyles();
    clearActionLine();
    renderMatchPanel();
    setMove(`Skip: ${ev.r} already matched to ${ev.h}`);
  }
  else if (ev.type === "start"){
    activeResident = null;
    updateActiveResidentStyles();
    clearActionLine();
    renderMatchPanel();
    setMove(`Start: ${residents.length} residents, ${hospitals.length} hospitals`);
  }
  else {
    clearActionLine();
    renderMatchPanel();
    setMove(`${ev.type}: ` + JSON.stringify(ev));
  }
}

function rebuildTo(step){
  held = {};
  hospitals.forEach(h => held[h] = new Set());
  exhausted = new Set();
  activeResident = null;
  clearTransientMatchState();

  renderEdges();
  clearActionLine();
  updateExhaustedStyles();
  updateActiveResidentStyles();

  for (let i = 0; i <= step && i < events.length; i++){
    const ev = events[i];
    if (ev.type === "start") continue;
    applyEvent(ev);
  }

  t = Math.min(step, events.length - 1);
  setStepInfo();
  renderMatchPanel();
}

function stepForward(){
  if (t >= events.length - 1) return;
  t += 1;
  const ev = events[t];
  if (ev.type !== "start") applyEvent(ev);
  setStepInfo();
}

function stepBack(){
  if (t <= 0) return;
  rebuildTo(t - 1);
}

function play(){
  if (timer) return;
  const delay = Number(document.getElementById("speed").value);
  timer = setInterval(() => {
    if (t >= events.length - 1){
      pause();
      document.getElementById("btnPlay").textContent = "Play";
      return;
    }
    stepForward();
  }, delay);
}

function pause(){
  if (!timer) return;
  clearInterval(timer);
  timer = null;
}

document.getElementById("btnReset").onclick = resetReplay;
document.getElementById("btnStep").onclick = () => stepForward();
document.getElementById("btnBack").onclick = () => stepBack();
document.getElementById("btnPlay").onclick = () => {
  if (timer){
    pause();
    document.getElementById("btnPlay").textContent = "Play";
  } else {
    play();
    document.getElementById("btnPlay").textContent = "Pause";
  }
};

window.addEventListener("resize", () => {
  drawStatic();
  rebuildTo(t);
});

(function main(){
  if (!Array.isArray(events) || events.length === 0){
    setMove("No events received.");
    return;
  }
  if (!ensureD3()) return;

  const startEv = events.find(e => e && e.type === "start");
  if (!startEv){
    setMove("Missing start event.");
    return;
  }
  initFromStart(startEv);
})();
</script>

</body>
</html>
"""

def run_viewer(events_json: list[dict[str, Any]]) -> None:
    injected = json.dumps(events_json, ensure_ascii=False)
    html = HTML.replace("__EVENTS_JSON__", injected)

    webview.create_window(
        "Stable Matching Replay",
        html=html,
        width=1100,
        height=560,
        resizable=False
    )
    webview.start()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m gui.d3_viewer <events_json_path>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        events = json.load(f)

    if not isinstance(events, list):
        raise ValueError("events JSON must be a list")

    run_viewer(events)

if __name__ == "__main__":
    main()