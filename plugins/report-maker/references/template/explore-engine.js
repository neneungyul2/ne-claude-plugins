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

  /* ── 초기 구동 ──
     본문에서 DATA·AXES·패널 등록을 마친 뒤 EXPLORE.start()를 한 번 부른다. */
  E.start = function(){
    E.initState();
    E.bindAxisControls();
    E.renderAll();
  };
})();
