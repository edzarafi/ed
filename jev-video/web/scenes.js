/* Motion timeline for the Jev explainer. Everything hangs off one paused GSAP timeline,
   driven frame-by-frame through window.seek(t) so rendering is deterministic. */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const tl = gsap.timeline({ paused: true });
const SC = Object.fromEntries(TL.scenes.map(s => [s.id, s]));
const L = (id, i) => SC[id].lines[i].t;
const LD = (id, i) => SC[id].lines[i].d;
const ease = "power3.out";

document.querySelectorAll("#introLogo, #outroLogo, #brandMark").forEach(el => (el.innerHTML = LOGO_SVG));
$("#introLogo").style.color = "#F6F1EA";
$("#outroLogo").style.color = "#F6F1EA";

// scene visibility: cross-fade in/out
TL.scenes.forEach((s, i) => {
  const el = $("#s-" + s.id);
  tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: "power1.out" }, Math.max(0, s.start - 0.15));
  if (i < TL.scenes.length - 1) tl.to(el, { opacity: 0, duration: 0.4, ease: "power1.in" }, s.start + s.dur - 0.35);
});
// drifting background glow
tl.fromTo("#g1", { x: 0, y: 0 }, { x: 900, y: 300, duration: TL.total, ease: "sine.inOut" }, 0);
tl.fromTo("#g2", { x: 0, y: 0 }, { x: -700, y: -250, duration: TL.total, ease: "sine.inOut" }, 0);
tl.fromTo("#grid", { y: 0 }, { y: 80, duration: TL.total, ease: "none" }, 0);
// corner brand from after the intro until the outro
tl.to("#brand", { opacity: 0.9, duration: 0.6 }, SC.company.start + 0.3);
tl.to("#brand", { opacity: 0, duration: 0.4 }, SC.outro.start);

/* 1 hook */
{
  const s = SC.hook;
  const words = ("הפנייה של הלקוח עוסקת ככל הנראה בנושא של חיוב כפול, ולכן כדאי לשקול להעביר אותה למחלקת הכספים. " +
    "עם זאת, ייתכן שמדובר גם בתקלה טכנית במערכת התשלומים, ובמקרה כזה מומלץ לערב גם את הצוות הטכני, " +
    "ואולי אף את שירות הלקוחות, כדי לוודא ש...").split(" ");
  $("#aitext").innerHTML = words.map(w => `<span class="w">${w} </span>`).join("");
  tl.from(".hook-title", { y: -30, opacity: 0, duration: 0.8, ease }, s.start + 0.2);
  tl.from(".bubble.user", { y: 40, opacity: 0, scale: 0.92, transformOrigin: "100% 100%", duration: 0.6, ease: "back.out(1.6)" }, s.start + 0.5);
  tl.from(".bubble.ai", { opacity: 0, y: 30, duration: 0.4, ease }, L("hook", 1) - 0.4);
  tl.to("#aitext .w", { opacity: 1, duration: 0.12, stagger: 0.085 }, L("hook", 1) - 0.2);
}

/* 2 problem */
{
  const s = SC.problem;
  tl.from("#s-problem .h2", { y: 50, opacity: 0, duration: 0.8, stagger: 0.5, ease }, L("problem", 0) + 0.1);
  const chips = $$("#s-problem .chip");
  const t2 = L("problem", 2), d2 = LD("problem", 2);
  chips.forEach((c, i) => tl.from(c, { y: 40, opacity: 0, scale: 0.8, duration: 0.55, ease: "back.out(2)" }, t2 + i * d2 * 0.33));
  chips.forEach((c, i) => tl.to(c, { borderColor: "#FF3D8B", backgroundColor: "rgba(255,61,139,.14)", duration: 0.3 }, t2 + i * d2 * 0.33 + 0.2));
}

/* 3 intro */
{
  const s = SC.intro;
  tl.from("#introLogo", { scale: 0.4, rotation: -30, opacity: 0, duration: 1.1, ease: "expo.out" }, s.start + 0.25);
  tl.fromTo("#introLogo", { color: "#F6F1EA" }, { color: "#FF3D8B", duration: 0.5, yoyo: true, repeat: 1 }, s.start + 1.0);
  tl.from("#jevword", { y: 80, opacity: 0, letterSpacing: "0.2em", duration: 1.0, ease: "expo.out" }, L("intro", 0) - 0.1);
  tl.from("#s-intro .p", { y: 30, opacity: 0, duration: 0.7, stagger: 0.6, ease }, L("intro", 1));
}

/* 4 company */
{
  tl.from("#co1", { x: 120, opacity: 0, duration: 0.8, ease }, L("company", 0));
  tl.from("#co2", { x: -120, opacity: 0, duration: 0.8, ease }, L("company", 1) - 0.1);
  const o = { v: 0 };
  tl.to(o, { v: 40, duration: 1.4, ease: "power2.out", onUpdate: () => ($("#money").textContent = `$${Math.round(o.v)}M`) }, L("company", 1));
}

/* 5 system one */
{
  const s = SC.systemone;
  tl.from("#s-systemone .h3", { y: -30, opacity: 0, duration: 0.7, ease }, L("systemone", 0));
  tl.from("#sys1", { y: 80, opacity: 0, duration: 0.8, ease }, L("systemone", 1));
  tl.from("#sys2", { y: 80, opacity: 0, duration: 0.8, ease }, L("systemone", 1) + 0.25);
  tl.from(".kahn", { opacity: 0, duration: 0.8 }, L("systemone", 1) + 0.8);
  const t2 = L("systemone", 2), d2 = LD("systemone", 2);
  tl.to("#sys1", { scale: 1.05, boxShadow: "0 0 90px rgba(255,61,139,.35)", duration: 0.5, ease }, t2);
  tl.fromTo(".bolt", { scale: 0.6, opacity: 0.3, transformOrigin: "50% 50%" }, { scale: 1.1, opacity: 1, duration: 0.25, yoyo: true, repeat: 3 }, t2 + 0.1);
  tl.to("#sys1", { scale: 1, boxShadow: "0 0 0 rgba(0,0,0,0)", duration: 0.5 }, t2 + d2 * 0.5);
  tl.to("#sys2", { scale: 1.05, borderColor: "rgba(124,135,255,.7)", duration: 0.5, ease }, t2 + d2 * 0.5);
  tl.fromTo(".slowdots i", { opacity: 0.15 }, { opacity: 1, duration: 0.5, stagger: 0.45, ease: "none" }, t2 + d2 * 0.5);
}

/* 6 how */
{
  tl.from(".demo-note", { opacity: 0, duration: 0.6 }, L("how", 0));
  const t1 = L("how", 1), d1 = LD("how", 1);
  tl.from("#h-state", { x: 80, opacity: 0, duration: 0.7, ease }, t1);
  tl.from("#h-ar1", { scaleX: 0, transformOrigin: "100% 50%", duration: 0.4 }, t1 + d1 * 0.5);
  tl.from("#h-q", { x: 80, opacity: 0, duration: 0.7, ease }, t1 + d1 * 0.52);
  tl.from("#h-q .q", { opacity: 0, y: 14, stagger: 0.35, duration: 0.4 }, t1 + d1 * 0.6);
  const t2 = L("how", 2), d2 = LD("how", 2);
  tl.from("#h-ar2", { scaleX: 0, transformOrigin: "100% 50%", duration: 0.3 }, t2 - 0.4);
  tl.from("#h-eng", { scale: 0, rotation: 90, duration: 0.6, ease: "back.out(1.8)" }, t2 - 0.2);
  tl.to("#h-eng", { scale: 1.12, duration: 0.18, yoyo: true, repeat: 1 }, t2 + 0.6);
  tl.from("#h-ar3", { scaleX: 0, transformOrigin: "100% 50%", duration: 0.25 }, t2 + 0.8);
  tl.from("#h-a", { x: 60, opacity: 0, duration: 0.5, ease }, t2 + 0.95);
  // all answers land together: that is the point of the model
  tl.from("#h-a .a", { opacity: 0, x: 30, duration: 0.35, ease }, t2 + 1.2);
  tl.from("#h-a .conf", { opacity: 0, duration: 0.4 }, t2 + d2 * 0.75);
}

/* 7 types */
{
  const t1 = L("types", 1), d1 = LD("types", 1);
  tl.from("#s-types .card", { y: 80, opacity: 0, duration: 0.7, stagger: 0.15, ease }, L("types", 0));
  tl.to(["#ty2", "#ty3"], { opacity: 0.35, duration: 0.3 }, t1 - 0.1);
  tl.from("#ty1sel", { backgroundColor: "rgba(0,0,0,0)", borderColor: "rgba(246,241,234,.12)", duration: 0.4 }, t1 + 0.4);
  const tB = t1 + d1 * 0.3;
  tl.to("#ty1", { opacity: 0.35, duration: 0.3 }, tB);
  tl.to("#ty2", { opacity: 1, duration: 0.3 }, tB);
  const o = { v: 0 };
  tl.to(o, { v: 88, duration: 1.0, ease: "power2.out", onUpdate: () => ($("#ty2n").textContent = Math.round(o.v)) }, tB + 0.1);
  tl.to("#ty2m", { width: "88%", duration: 1.0, ease: "power2.out" }, tB + 0.1);
  const tC = t1 + d1 * 0.55;
  tl.to("#ty2", { opacity: 0.35, duration: 0.3 }, tC);
  tl.to("#ty3", { opacity: 1, duration: 0.3 }, tC);
  tl.to("#ty3m", { width: "93%", duration: 0.9, ease: "power2.out" }, tC + 0.1);
  tl.to(["#ty1", "#ty2"], { opacity: 1, duration: 0.4 }, t1 + d1 + 0.1);
}

/* 8 parallel */
{
  const words = "הפנייה עוסקת ככל הנראה בחיוב כפול ולכן כדאי".split(" ");
  $("#toks").innerHTML = words.map(w => `<div class="tok">${w}</div>`).join("");
  const t0 = L("parallel", 0);
  tl.from("#s-parallel .lane .name", { opacity: 0, y: 20, duration: 0.5, stagger: 0 }, SC.parallel.start + 0.1);
  tl.set("#s-parallel .lane:nth-child(2)", { opacity: 0.3 }, SC.parallel.start);
  tl.to(".tok", { opacity: 1, duration: 0.1, stagger: 0.42 }, t0 + 0.2);
  const t1 = L("parallel", 1);
  tl.to("#s-parallel .lane:nth-child(1)", { opacity: 0.45, duration: 0.4 }, t1 - 0.2);
  tl.to("#s-parallel .lane:nth-child(2)", { opacity: 1, duration: 0.4 }, t1 - 0.3);
  tl.fromTo(".ans", { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2.2)" }, t1 + LD("parallel", 1) * 0.35);
}

/* 9 no invent */
{
  const t0 = L("noinvent", 0), d0 = LD("noinvent", 0);
  tl.from("#s-noinvent .h2", { y: -30, opacity: 0, duration: 0.7, ease }, SC.noinvent.start + 0.2);
  tl.from("#set", { scale: 0.9, opacity: 0, duration: 0.7, ease }, SC.noinvent.start + 0.4);
  tl.from("#set .chip", { opacity: 0, y: 20, stagger: 0.12, duration: 0.4 }, SC.noinvent.start + 0.7);
  tl.from("#intr", { opacity: 0, y: 60, duration: 0.5, ease }, t0 + 0.4);
  tl.to("#intr", { y: -90, duration: 0.45, ease: "power2.in" }, t0 + d0 * 0.55);
  tl.to("#intr", { y: 30, duration: 0.6, ease: "bounce.out" }, t0 + d0 * 0.55 + 0.45);
  tl.to("#intrx", { scaleX: 1, duration: 0.35, ease }, t0 + d0 * 0.55 + 1.0);
  tl.to("#intr", { opacity: 0.35, duration: 0.4 }, t0 + d0 * 0.55 + 1.4);
  const t1 = L("noinvent", 1);
  tl.to("#set .chip.pinkc", { scale: 1.15, duration: 0.25, yoyo: true, repeat: 1 }, t1 + 0.6);
  tl.to("#set", { borderColor: "rgba(255,61,139,1)", duration: 0.4 }, t1 + 0.2);
}

/* 10 numbers */
{
  const t0 = L("numbers", 0), t1 = L("numbers", 1), d1 = LD("numbers", 1);
  tl.from("#n1", { y: 80, opacity: 0, duration: 0.7, ease }, t0 + 0.2);
  const a = { v: 0 }, b = { v: 0 };
  tl.to(a, { v: 70, duration: 1.0, ease: "power2.out", onUpdate: () => ($("#ms1").textContent = Math.round(a.v)) }, t0 + 0.9);
  tl.to(b, { v: 500, duration: 1.4, ease: "power2.out", onUpdate: () => ($("#ms2").textContent = Math.round(b.v)) }, t0 + 1.4);
  tl.from("#n2", { y: 80, opacity: 0, duration: 0.7, ease }, t1);
  const p = { v: 0 };
  tl.to(p, { v: 0.042, duration: 1.3, ease: "power2.out", onUpdate: () => ($("#price").textContent = "$" + p.v.toFixed(3)) }, t1 + 0.4);
  tl.from("#free", { scale: 0, opacity: 0, duration: 0.5, ease: "back.out(2.4)" }, t1 + d1 * 0.78);
}

/* 11 calibration */
{
  // 60 cases from the jev-latest run: 40 at confidence 1.000 (all right), 15 right below 1.000, 5 misses
  const kinds = [...Array(40).fill("hi")];
  const rest = ["lo", "lo", "miss", "lo", "lo", "lo", "miss", "lo", "lo", "lo", "miss", "lo", "lo", "lo", "miss", "lo", "lo", "miss", "lo", "lo"];
  $("#dots").innerHTML = kinds.concat(rest).map(k => `<div class="dot" data-k="${k}"></div>`).join("");
  const t1 = L("calibration", 1), t2 = L("calibration", 2);
  tl.from("#s-calibration .h3", { y: -30, opacity: 0, duration: 0.7, ease }, L("calibration", 0));
  tl.to(".dot", { scale: 1, duration: 0.3, stagger: 0.012, ease: "back.out(2)" }, L("calibration", 0) + 0.5);
  tl.to('.dot[data-k="hi"]', { backgroundColor: "#3DDC97", borderColor: "#3DDC97", duration: 0.25, stagger: 0.03 }, t1 + 0.3);
  tl.to("#lg1", { opacity: 1, duration: 0.5 }, t1 + 1.2);
  tl.to('.dot[data-k="lo"]', { backgroundColor: "rgba(61,220,151,.35)", borderColor: "rgba(61,220,151,.6)", duration: 0.25, stagger: 0.04 }, t2);
  tl.to("#lg2", { opacity: 1, duration: 0.5 }, t2 + 0.4);
  tl.to('.dot[data-k="miss"]', { backgroundColor: "#FF5C6C", borderColor: "#FF5C6C", duration: 0.25, stagger: 0.12 }, t2 + 0.9);
  tl.to("#lg3", { opacity: 1, duration: 0.5 }, t2 + 1.4);
  tl.from("#s-calibration .src", { opacity: 0, duration: 0.6 }, t1);
}

/* 12 reality */
{
  const t1 = L("reality", 1), t2 = L("reality", 2), t3 = L("reality", 3), d3 = LD("reality", 3);
  tl.from("#rv1", { x: 100, opacity: 0, duration: 0.8, ease }, t1 - 0.2);
  tl.from("#rv1 .metric", { opacity: 0, y: 20, stagger: 0.8, duration: 0.5 }, t1 + 0.8);
  tl.from("#rv1 .stamp", { opacity: 0, duration: 0.5 }, t2 - 0.6);
  tl.from("#rv2", { x: -100, opacity: 0, duration: 0.8, ease }, t2);
  const m = $$("#rv2 .metric");
  m.forEach((el, i) => tl.from(el, { opacity: 0, y: 20, duration: 0.5 }, t3 + i * d3 * 0.24));
  tl.from("#rv2 .stamp", { scale: 0, opacity: 0, duration: 0.5, ease: "back.out(2)" }, t3 + d3 * 0.8);
}

/* 13 limits */
{
  const items = $$("#s-limits .li");
  const t1 = L("limits", 1), d1 = LD("limits", 1);
  tl.from("#s-limits .lim", { opacity: 0, duration: 0.3 }, SC.limits.start);
  items.slice(0, 3).forEach((el, i) => {
    const at = t1 + i * d1 * 0.32;
    tl.to(el, { opacity: 1, duration: 0.4 }, at - 0.2);
    tl.fromTo(el.querySelector(".txt"), { "--s": "0%" }, { "--s": "100%", duration: 0.5, ease: "power2.inOut" }, at + 0.4);
    tl.to(el, { opacity: 0.55, duration: 0.4 }, at + 0.9);
  });
  tl.to(items[3], { opacity: 1, duration: 0.6 }, L("limits", 2) + 0.4);
  tl.from(items[3], { x: 60, duration: 0.6, ease }, L("limits", 2) + 0.4);
}

/* 14 outro */
{
  const s = SC.outro, t1 = L("outro", 1), d1 = LD("outro", 1);
  tl.from("#d1", { y: 60, opacity: 0, duration: 0.7, ease }, t1);
  tl.from("#dplus", { scale: 0, opacity: 0, duration: 0.4 }, t1 + d1 * 0.4);
  tl.from("#d2", { y: 60, opacity: 0, duration: 0.7, ease }, t1 + d1 * 0.45);
  tl.to("#d1", { x: -330, duration: 0.7, ease: "power2.inOut" }, t1 + d1 + 0.2);
  tl.to("#d2", { x: 330, duration: 0.7, ease: "power2.inOut" }, t1 + d1 + 0.2);
  tl.to("#duo", { opacity: 0, scale: 0.9, duration: 0.5 }, t1 + d1 + 0.7);
  tl.to("#final", { opacity: 1, duration: 0.8 }, t1 + d1 + 1.0);
  tl.from("#outroLogo", { scale: 0.5, rotation: -25, duration: 1.0, ease: "expo.out" }, t1 + d1 + 1.0);
  tl.from("#final .jev-word, #final .tag", { y: 40, opacity: 0, duration: 0.8, stagger: 0.2, ease }, t1 + d1 + 1.3);
  tl.from("#final .srcs", { opacity: 0, duration: 0.8 }, t1 + d1 + 2.0);
  tl.to("#stage", { opacity: 0, duration: 0.8 }, TL.total - 0.8);
}

// progress bar
tl.fromTo("#progress", { width: "0%" }, { width: "100%", duration: TL.total, ease: "none" }, 0);
tl.set({}, {}, TL.total); // pin the timeline length

/* subtitles: picked per frame from the voice timings */
const LINES = TL.scenes.flatMap(s => s.lines);
const subEl = $("#subtext"), subBox = $("#subs");
function subsAt(t) {
  const l = LINES.find(l => t >= l.t - 0.08 && t <= l.t + l.d + 0.3);
  if (!l) { subBox.style.opacity = 0; return; }
  if (subEl.textContent !== l.sub) subEl.textContent = l.sub;
  const a = Math.min(1, (t - (l.t - 0.08)) / 0.15, (l.t + l.d + 0.3 - t) / 0.15);
  subBox.style.opacity = Math.max(0, a);
}

window.seek = t => { tl.seek(t, false); subsAt(t); };
window.TOTAL = TL.total;
window.READY = document.fonts.ready.then(() => { window.seek(0); return true; });
