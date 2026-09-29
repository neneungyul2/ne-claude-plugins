(function(){
  /* ── 탐색형 공용 계산 엔진 ──
     base.js(툴팁·모달·목차·드릴다운 열고닫기)와 함께 붙는다. assemble.py에
     "--js base.js,explore-engine.js" 로 이어 붙인다 — 이 파일이 base.js를 대신하지 않는다.

     이 파일은 손으로 고쳐 쓰지 않는다. 패널마다 계산이 새로 필요하면
     여기에 함수를 추가한다 (build-explore/SKILL.md 4장). 산출물마다 값이 다르지만
     함수 자체는 바뀌지 않아야 한다 — explore-model.md §4. */

  var E = window.EXPLORE = window.EXPLORE || {};

  /* ── 데이터·상태 ──
     본문(content.html)에서 EXPLORE.DATA = [...] (그레인 원자료, 긴 형식)와
     EXPLORE.AXES = [{id,...}] 를 채운 뒤 이 스크립트가 실행된다. */
  E.DATA = E.DATA || [];
  E.AXES = E.AXES || [];
  E.state = E.state || {};
  E._panels = {};

  /* 축 기본값으로 state를 초기화한다. 본문에서 한 번만 부른다. */
  E.initState = function(){
    E.AXES.forEach(function(ax){ if(!(ax.id in E.state)) E.state[ax.id] = ax.default; });
    return E.state;
  };

  /* ── 필터 ──
     axesUsed에 없는 축은 그 패널에 영향을 주지 않는다 — panels[].axes_used를 그대로 넣는다. */
  E.filterRows = function(rows, state, axesUsed){
    axesUsed = axesUsed || Object.keys(state);
    return rows.filter(function(r){
      return axesUsed.every(function(id){
        var v = state[id];
        if(v == null || v === '__all__') return true;
        if(Array.isArray(v)) return v.length === 0 || v.indexOf(r[id]) !== -1;
        if (typeof v === 'object' && v.from != null) { // 기간 range {from,to}
          return r[id] >= v.from && r[id] <= v.to;
        }
        return r[id] === v;
      });
    });
  };

  /* ── 집계 ── */
  E.sum = function(rows, key){ return rows.reduce(function(a,r){ return a + (Number(r[key])||0); }, 0); };
  E.avg = function(rows, key){ return rows.length ? E.sum(rows,key)/rows.length : 0; };

  /* 가중평균 — 비율 지표(공급률 등)를 단순 평균이 아니라 분모로 가중해 합친다.
     예: wavg(rows, 'supRate', 'amt') → amt로 가중한 supRate 평균 */
  E.wavg = function(rows, valueKey, weightKey){
    var wsum = E.sum(rows, weightKey);
    if(!wsum) return 0;
    return rows.reduce(function(a,r){ return a + (Number(r[valueKey])||0) * (Number(r[weightKey])||0); }, 0) / wsum;
  };

  E.pct = function(part, whole){ return whole ? part/whole*100 : 0; };

  /* dimKey(예: '부문')로 그룹핑하고, valueKeys(예:['rev','qty']) 각각을 합산한다.
     반환: [{key, rev, qty, __rows:[원본 행들]}, ...] — __rows는 드릴다운에 쓴다 */
  E.rollupBy = function(rows, dimKey, valueKeys){
    var map = {};
    rows.forEach(function(r){
      var k = r[dimKey];
      if(!map[k]) { map[k] = { key:k, __rows:[] }; valueKeys.forEach(function(vk){ map[k][vk]=0; }); }
      valueKeys.forEach(function(vk){ map[k][vk] += Number(r[vk])||0; });
      map[k].__rows.push(r);
    });
    return Object.keys(map).map(function(k){ return map[k]; });
  };

  /* 상위 N + 기타로 나눈다. sortKey 기준 내림차순.
     반환: {top:[...], etc:{key:'기타', ...합계, __rows:[etc에 속한 원본 행 전체]}} */
  E.splitTopN = function(rolled, sortKey, topN){
    var sorted = rolled.slice().sort(function(a,b){ return b[sortKey]-a[sortKey]; });
    var top = sorted.slice(0, topN);
    var rest = sorted.slice(topN);
    if(!rest.length) return { top: top, etc: null };
    var etc = { key: '기타', __rows: [] };
    Object.keys(rest[0]).forEach(function(k){
      if(k === 'key' || k === '__rows') return;
      etc[k] = rest.reduce(function(a,r){ return a + (Number(r[k])||0); }, 0);
    });
    rest.forEach(function(r){ etc.__rows = etc.__rows.concat(r.__rows || []); });
    return { top: top, etc: etc };
  };

  /* 재정규화 — 상위 N만 남기고 비중을 다시 100%로 맞춘다 (기타를 뺐을 때만 쓴다) */
  E.renorm = function(rolled, valueKey){
    var total = E.sum(rolled, valueKey);
    return rolled.map(function(r){
      var o = Object.assign({}, r);
      o.__share = total ? r[valueKey]/total*100 : 0;
      return o;
    });
  };

  /* ── 기간 비교 (전기·전년) ──
     periodKey: state에서 기간을 담는 축 id. shiftFn(value) → 이전 구간의 값으로 변환.
     예: comparePeriod(rows, state, 'date', prevMonth) */
  E.comparePeriod = function(rows, state, periodKey, shiftFn, axesUsed){
    var prevState = Object.assign({}, state);
    prevState[periodKey] = shiftFn(state[periodKey]);
    return E.filterRows(rows, prevState, axesUsed);
  };

  E.delta = function(cur, prev){ return prev ? (cur-prev)/Math.abs(prev)*100 : null; };

  /* ── 숫자 표기 ── */
  E.f0 = function(n){ return Math.round(n).toLocaleString('ko-KR'); };
  E.f1 = function(n){ return (Math.round(n*10)/10).toLocaleString('ko-KR', {minimumFractionDigits:1}); };
  E.f2 = function(n){ return (Math.round(n*100)/100).toLocaleString('ko-KR', {minimumFractionDigits:2}); };
  E.fpct = function(n){ return E.f1(n)+'%'; };

  /* ── 패널 등록·재렌더 ──
     본문에서 각 패널마다: EXPLORE.registerPanel('p1', {axes_used:[...], render:function(state,rows){...}})
     축 컨트롤이 바뀌면 axes_used와 겹치는 패널만, 애매하면 전부 다시 그린다 (build-explore §2). */
  E.registerPanel = function(id, def){ E._panels[id] = def; };

  E.renderAll = function(changedAxis){
    Object.keys(E._panels).forEach(function(id){
      var p = E._panels[id];
      if(changedAxis && p.axes_used && p.axes_used.indexOf(changedAxis) === -1) return;
      var rows = E.filterRows(E.DATA, E.state, p.axes_used);
      p.render(E.state, rows);
    });
    E.reflectState();
  };

  /* 현재 선택된 축 조합을 화면 상단 배지에 반영한다. [data-state-badge]가 있으면 채운다. */
  E.reflectState = function(){
    var badge = document.querySelector('[data-state-badge]');
    if(!badge) return;
    var parts = E.AXES.map(function(ax){
      var v = E.state[ax.id];
      return ax.name + ': ' + (Array.isArray(v) ? (v.length? v.join(', ') : '전체') : (v==null||v==='__all__' ? '전체' : v));
    });
    badge.textContent = parts.join(' · ');
  };

  /* ── 축 컨트롤 바인딩 ──
     [data-axis="<축id>"] 를 가진 select/input을 찾아 바꾸면 state를 갱신하고 다시 그린다.
     chips(다중 선택)는 [data-axis][data-chip-value]에 클릭 리스너를 건다. */
  E.bindAxisControls = function(){
    document.querySelectorAll('select[data-axis], input[data-axis]').forEach(function(el){
      el.addEventListener('change', function(){
        E.state[el.dataset.axis] = el.value === '__all__' ? '__all__' : el.value;
        E.renderAll(el.dataset.axis);
      });
    });
    document.querySelectorAll('[data-axis][data-chip-value]').forEach(function(chip){
      chip.addEventListener('click', function(){
        var axis = chip.dataset.axis, val = chip.dataset.chipValue;
        var cur = Array.isArray(E.state[axis]) ? E.state[axis].slice() : [];
        var i = cur.indexOf(val);
        if(i === -1) cur.push(val); else cur.splice(i,1);
        chip.classList.toggle('sel', i === -1);
        E.state[axis] = cur;
        E.renderAll(axis);
      });
    });
  };


  /* ── 위계(대분류 > 중분류 > 소분류) ──
     levels: 상위→하위 차원 키 배열. path: 지금까지 고른 상위 값들.
     반환: path 바로 아래 단계 항목별 {key, value, share} (share = 상위 분류 안 비중, %) 내림차순 */
  E.hierShares = function(rows, levels, path, valueKey){
    path = path || [];
    var sub = rows.filter(function(r){ return path.every(function(v, i){ return r[levels[i]] === v; }); });
    var lv = levels[path.length];
    if(lv == null) return [];
    var rolled = E.rollupBy(sub, lv, [valueKey]);
    var total = E.sum(rolled, valueKey);
    return rolled.map(function(g){ return { key: g.key, value: g[valueKey], share: E.pct(g[valueKey], total), __rows: g.__rows }; })
                 .sort(function(a, b){ return b.value - a.value; });
  };

  /* 트리 표 행. open: {'<경로 키>': true} — 펼친 곳만 아래 단계를 넣는다.
     반환: [{depth, key, path, pathKey, value, share, hasChild, open}] 화면 순서대로 */
  E.treeRows = function(rows, levels, valueKey, open){
    open = open || {};
    var out = [];
    (function walk(path){
      E.hierShares(rows, levels, path, valueKey).forEach(function(n){
        var p = path.concat([n.key]), pk = p.join('›'), hasChild = p.length < levels.length;
        out.push({ depth: path.length, key: n.key, path: p, pathKey: pk, value: n.value, share: n.share, hasChild: hasChild, open: !!open[pk], __rows: n.__rows });
        if(hasChild && open[pk]) walk(p);
      });
    })([]);
    return out;
  };

  /* ── 비교 단위 ──
     perUnit: 크기 맞춘 값. 예) 인구 1천 명당 매출 = perUnit(매출, 인구, 1000). 분모가 0이면 null
     groupAvg: 비교군 1곳 평균 = 비교군 합 ÷ 대상 수. keyOf(r) → 대상 id */
  E.perUnit = function(value, denom, scale){ return denom ? value / denom * (scale || 1) : null; };
  E.groupAvg = function(rows, keyOf, valueKey){
    var ids = {}; rows.forEach(function(r){ ids[keyOf(r)] = 1; });
    var n = Object.keys(ids).length;
    return n ? E.sum(rows, valueKey) / n : null;
  };

  /* ── 사이드바 목차 (sections가 있을 때) ──
     .xapp > .gnb 안의 a.l1 / a.l2 (href="#섹션id"), 접기 버튼 .fold, 현재 위치 [data-loc].
     스크롤하면 지금 보는 항목(.on)과 그 대분류(.pa)를 표시하고, 접힘 상태를 기억한다. */
  E.bindGnb = function(){
    var app = document.querySelector('.xapp'); if(!app) return;
    var links = [].slice.call(app.querySelectorAll('.gnb a[href^="#"]'));
    var fold = app.querySelector('.gnb .fold');
    function spy(){
      var y = window.scrollY + 140, cur = null;
      links.forEach(function(a){ var t = document.querySelector(a.getAttribute('href')); if(t && t.getBoundingClientRect().top + window.scrollY <= y) cur = a; });
      var i0 = links.indexOf(cur), par = null;
      for(var j = i0; j >= 0; j--) if(links[j].classList.contains('l1')){ par = links[j]; break; }
      links.forEach(function(a){ a.classList.toggle('on', a === cur); a.classList.toggle('pa', a === par && a !== cur); });
      var loc = document.querySelector('[data-loc]');
      var lab = function(a){ var i = a.querySelector('i'), t = a.querySelector('.tx'); return i && t ? i.textContent.trim() + ' ' + t.textContent.trim() : a.textContent.trim(); };
      if(loc) loc.textContent = cur ? '현재 위치: ' + (par ? lab(par) : '') + (cur !== par ? ' › ' + lab(cur) : '') : '';
    }
    function setFold(c){
      app.classList.toggle('collapsed', c);
      if(fold){ fold.textContent = c ? '»' : '«'; fold.setAttribute('aria-expanded', String(!c)); fold.setAttribute('aria-label', c ? '목차 펼치기' : '목차 접기'); }
      try { localStorage.setItem('xgnbFold', c ? '1' : '0'); } catch(x) {}
    }
    if(fold) fold.addEventListener('click', function(){ setFold(!app.classList.contains('collapsed')); });
    try { if(localStorage.getItem('xgnbFold') === '1') setFold(true); } catch(x) {}
    window.addEventListener('scroll', spy, { passive: true });
    spy();
  };

  /* ── ⓘ 뒤로 옮기기 ──
     .block / .xsec / .foot 안의 직계 p.note(기준·비고)와 p.note.guide(사용법)를 화면에서 걷고,
     제목 옆에 ⓘ 버튼을 단다. 호버 → 짧은 툴팁(data-tip), 클릭 → 모달(#mask 안, base.js가 연다).
     렌더 함수가 note 내용을 바꿔도 모달은 열 때마다 새로 채운다. */
  E.bindInfo = function(){
    var mask = document.getElementById('mask'); if(!mask) return;
    var n = 0;
    document.querySelectorAll('.block, .xsec, .foot').forEach(function(box){
      var notes = [].filter.call(box.children, function(c){ return c.classList.contains('note'); });
      if(!notes.length) return;
      var prev = box.previousElementSibling;
      var hd = box.querySelector(':scope > h2, :scope > h3, :scope > .fh') || (prev && prev.classList.contains('shead') ? prev.querySelector('h2') : null);
      if(!hd) return;
      var id = 'xinfo-' + (++n), hold = document.createElement('div');
      hold.className = 'xinfo-hold'; hold.hidden = true; hold.id = id + '-hold';
      notes.forEach(function(x){ hold.appendChild(x); }); box.appendChild(hold);
      var g = notes.some(function(x){ return x.classList.contains('guide'); });
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'xinfo' + (g ? '' : ' bare'); b.setAttribute('data-modal', id); b.dataset.hold = hold.id;
      b.setAttribute('aria-label', (g ? '사용법·' : '') + '기준 보기');
      b.innerHTML = '<span aria-hidden="true">i</span>' + (g ? '가이드' : '');
      hd.appendChild(b);
      var m = document.createElement('div');
      m.className = 'modal'; m.dataset.id = id; m.hidden = true;
      m.innerHTML = '<header><div><h3></h3></div><button class="x" data-close aria-label="닫기">×</button></header><div class="body"></div>';
      mask.appendChild(m);
    });
    function fill(b){
      var hold = document.getElementById(b.dataset.hold), m = mask.querySelector('.modal[data-id="' + b.getAttribute('data-modal') + '"]');
      var gs = [], ks = [];
      [].forEach.call(hold.children, function(x){ if(x.textContent.trim()) (x.classList.contains('guide') ? gs : ks).push('<p>' + x.innerHTML + '</p>'); });
      m.querySelector('h3').textContent = b.parentNode.textContent.replace(/i(가이드)?$/, '').trim();
      m.querySelector('.body').innerHTML = (gs.length ? '<h4>사용법</h4>' + gs.join('') : '') + (ks.length ? '<h4>기준·비고</h4>' + ks.join('') : '');
      b.setAttribute('data-tip', hold.textContent.replace(/\s+/g, ' ').replace(/\|/g, '/').trim().slice(0, 160) + ' … 누르면 전체');
    }
    document.addEventListener('mouseover', function(e){ var b = e.target.closest && e.target.closest('.xinfo'); if(b) fill(b); }, true);
    document.addEventListener('click', function(e){ var b = e.target.closest && e.target.closest('.xinfo'); if(b) fill(b); }, true);
  };

  /* ── 초기 구동 ──
     본문에서 DATA·AXES·패널 등록을 마친 뒤 EXPLORE.start()를 한 번 부른다. */
  E.start = function(){
    E.initState();
    E.bindAxisControls();
    E.renderAll();
    E.bindGnb();
    E.bindInfo();
  };
})();
