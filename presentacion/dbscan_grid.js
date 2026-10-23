// DBSCAN esférico con índice de rejilla 3D. Función autocontenida: se inyecta tal cual en un Web Worker.
// Radio grande (>= 18 km): celdas de lado chord/sqrt(3), de modo que dos puntos de la misma celda siempre están a menos de eps;
//   cada celda con algún núcleo es un nodo del union-find (rápido cuando hay mucha densidad).
// Radio pequeño (< 18 km): celdas de lado chord (27 celdas vecinas) y union-find punto a punto (rápido cuando casi todo es disperso).
function gridDBSCAN(ux, uy, uz, epsKm, minPts){
  const N = ux.length, theta = epsKm/6371, cosT = Math.cos(theta), chord = 2*Math.sin(theta/2);
  const small = epsKm < 18, s = small ? chord : chord/Math.sqrt(3), R = small ? 1 : 2;
  const SH = R + 2, M = Math.ceil(2/s) + 2*SH + 2;
  const map = new Map(), cellOf = new Int32Array(N), cx = [], cy = [], cz = [], cnt = [];
  let nc = 0;
  for(let i=0;i<N;i++){
    const a = Math.floor((ux[i]+1)/s)+SH, b = Math.floor((uy[i]+1)/s)+SH, c = Math.floor((uz[i]+1)/s)+SH, k = a + M*(b + M*c);
    let id = map.get(k);
    if(id === undefined){ id = nc++; map.set(k,id); cx.push(a); cy.push(b); cz.push(c); cnt.push(0); }
    cellOf[i] = id; cnt[id]++;
  }
  const start = new Int32Array(nc+1);
  for(let c=0;c<nc;c++) start[c+1] = start[c] + cnt[c];
  const fill = start.slice(0,nc), items = new Int32Array(N);
  for(let i=0;i<N;i++) items[fill[cellOf[i]]++] = i;
  // celdas vecinas: las que pueden tener puntos a menos de chord
  const offs = [];
  for(let dx=-R;dx<=R;dx++) for(let dy=-R;dy<=R;dy++) for(let dz=-R;dz<=R;dz++){
    const m = Math.max(Math.abs(dx)-1,0)**2 + Math.max(Math.abs(dy)-1,0)**2 + Math.max(Math.abs(dz)-1,0)**2;
    if(m*s*s < chord*chord*(1-1e-9) || small) offs.push([dx,dy,dz]);
  }
  const nb = new Array(nc);
  for(let c=0;c<nc;c++){
    const l = [];
    for(const [dx,dy,dz] of offs){ const id = map.get((cx[c]+dx) + M*((cy[c]+dy) + M*(cz[c]+dz))); if(id !== undefined) l.push(id); }
    nb[c] = l;
  }
  const near = (i, j) => ux[i]*ux[j]+uy[i]*uy[j]+uz[i]*uz[j] >= cosT;
  // puntos núcleo
  const core = new Uint8Array(N), cellCore = new Uint8Array(nc);
  for(let c=0;c<nc;c++){
    if(!small && cnt[c] >= minPts){ for(let p=start[c];p<start[c+1];p++) core[items[p]] = 1; cellCore[c] = 1; continue; }
    if(small && nb[c].length === 1 && cnt[c] < minPts) continue;   // punto(s) sin celdas vecinas y pocos: no puede haber núcleo
    for(let p=start[c];p<start[c+1];p++){
      const i = items[p]; let n = 0;
      outer: for(const d of nb[c]) for(let q=start[d];q<start[d+1];q++){
        if(near(i, items[q]) && ++n >= minPts) break outer;
      }
      if(n >= minPts){ core[i] = 1; cellCore[c] = 1; }
    }
  }
  const lab = new Int32Array(N).fill(-1);
  let K = 0;
  if(!small){
    const par = new Int32Array(nc); for(let c=0;c<nc;c++) par[c] = c;
    const find = x => { while(par[x] !== x){ par[x] = par[par[x]]; x = par[x]; } return x; };
    for(let c=0;c<nc;c++){
      if(!cellCore[c]) continue;
      for(const d of nb[c]){
        if(d <= c || !cellCore[d] || find(c) === find(d)) continue;
        let hit = false;
        for(let p=start[c];p<start[c+1] && !hit;p++){ const i = items[p]; if(!core[i]) continue;
          for(let q=start[d];q<start[d+1];q++){ const j = items[q]; if(core[j] && near(i, j)){ hit = true; break; } } }
        if(hit) par[find(d)] = find(c);
      }
    }
    const idOf = new Int32Array(nc).fill(-1);
    for(let c=0;c<nc;c++) if(cellCore[c]){ const r = find(c); if(idOf[r] < 0) idOf[r] = K++; }
    for(let i=0;i<N;i++){
      if(core[i]){ lab[i] = idOf[find(cellOf[i])]; continue; }
      const c = cellOf[i];
      found: for(const d of nb[c]) for(let q=start[d];q<start[d+1];q++){
        const j = items[q];
        if(core[j] && near(i, j)){ lab[i] = idOf[find(d)]; break found; }
      }
    }
  } else {
    const par = new Int32Array(N); for(let i=0;i<N;i++) par[i] = i;
    const find = x => { while(par[x] !== x){ par[x] = par[par[x]]; x = par[x]; } return x; };
    for(let c=0;c<nc;c++){
      if(!cellCore[c]) continue;
      for(let p=start[c];p<start[c+1];p++){
        const i = items[p]; if(!core[i]) continue;
        for(const d of nb[c]) for(let q=start[d];q<start[d+1];q++){
          const j = items[q];
          if(j > i && core[j] && near(i, j)){ const a = find(i), b = find(j); if(a !== b) par[b] = a; }
        }
      }
    }
    const idOf = new Int32Array(N).fill(-1);
    for(let i=0;i<N;i++) if(core[i]){ const r = find(i); if(idOf[r] < 0) idOf[r] = K++; }
    for(let i=0;i<N;i++){
      if(core[i]){ lab[i] = idOf[find(i)]; continue; }
      const c = cellOf[i];
      found2: for(const d of nb[c]) for(let q=start[d];q<start[d+1];q++){
        const j = items[q];
        if(core[j] && near(i, j)){ lab[i] = idOf[find(j)]; break found2; }
      }
    }
  }
  return {lab, K};
}
if(typeof module !== 'undefined') module.exports = gridDBSCAN;
