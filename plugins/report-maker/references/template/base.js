(function(){
  /* ── 저장용 원본. 다른 코드가 화면을 건드리기 전에 가장 먼저 잡아 둔다 ──
     편집 내용을 저장할 때 이 원본에 편집 기록(rm-edits)만 바꿔 끼워 문서를 다시 만든다 */
  var PRISTINE={
    title:document.title,
    styles:[].map.call(document.querySelectorAll('head style'),function(s){return s.textContent;}),
    body:document.body.innerHTML
  };

  /* ── 용어 사전. spec 의 glossary 를 그대로 넣는다 ──
     본문의 <script type="application/json" id="rm-glossary">에서 읽는다 */
  /* d 에는 뜻만 적지 않는다. 그 말이 오해받는 지점까지 적는다
     (예: 외부 기준 지표라면 "사내 기준과 합산하지 않는다"까지) */
  var GLOSSARY = {};   /* 비워 둔다. 용어는 본문의 rm-glossary(JSON)에 넣는다 */

  try{ var gj=document.getElementById('rm-glossary');
       if(gj){ var gd=JSON.parse(gj.textContent||'{}'); for(var gk in gd) GLOSSARY[gk]=gd[gk]; } }catch(_){}

  /* ── 툴팁: [data-tip] 과 [data-term] 공용 ── */
  var tt=document.getElementById('tt');
  function show(html,x,y){
    tt.innerHTML=html; tt.classList.add('on');
    var r=tt.getBoundingClientRect();
    tt.style.left=Math.min(x+14, innerWidth-r.width-10)+'px';
    tt.style.top=Math.min(y+14, innerHeight-r.height-10)+'px';
  }
  function esc(s){return String(s).replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
  document.addEventListener('mouseover',function(e){
    var t=e.target.closest('[data-tip]');
    if(t){
      var p=t.getAttribute('data-tip').split('|');
      var h='<div class="tt">'+esc(p[0])+'</div>';
      for(var i=1;i<p.length;i++){
        var kv=p[i].split(/\s(?=[^\s]*$)/);
        h+= kv.length>1 ? '<div class="tr2"><span>'+esc(kv[0])+'</span><b>'+esc(kv[1])+'</b></div>'
                        : '<div>'+esc(p[i])+'</div>';
      }
      show(h,e.clientX,e.clientY); return;
    }
    var g=e.target.closest('[data-term]');
    if(g){
      var k=GLOSSARY[g.getAttribute('data-term')];
      if(k) show('<div class="tt">'+esc(k.t)+'</div>'+esc(k.d), e.clientX, e.clientY);
    }
  });
  document.addEventListener('mousemove',function(e){
    if(tt.classList.contains('on')) show(tt.innerHTML,e.clientX,e.clientY);
  });
  document.addEventListener('mouseout',function(e){
    if(e.target.closest('[data-tip],[data-term]')) tt.classList.remove('on');
  });
  /* 키보드·터치에서도 용어 설명을 연다 — 마우스가 없는 사람도 읽을 수 있어야 한다 */
  document.addEventListener('focusin',function(e){
    var g=e.target.closest&&e.target.closest('[data-term]'); if(!g) return;
    var k=GLOSSARY[g.getAttribute('data-term')], r=g.getBoundingClientRect();
    if(k) show('<div class="tt">'+esc(k.t)+'</div>'+esc(k.d), r.left, r.bottom);
  });
  document.addEventListener('focusout',function(e){
    if(e.target.closest&&e.target.closest('[data-term]')) tt.classList.remove('on');
  });

  /* ── 모달 ── */
  var mask=document.getElementById('mask');
  function open(id){
    [].forEach.call(mask.querySelectorAll('.modal'),function(m){ m.hidden = m.dataset.id!==id; });
    mask.classList.add('on'); document.body.style.overflow='hidden';
  }
  function close(){ mask.classList.remove('on'); document.body.style.overflow=''; }
  document.addEventListener('click',function(e){
    var o=e.target.closest('[data-modal]'); if(o){ open(o.getAttribute('data-modal')); return; }
    if(e.target.closest('[data-close]') || e.target===mask) close();
  });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') close(); });

  /* ── 목차 스크롤 연동 ── */
  var heads=[].slice.call(document.querySelectorAll('.shead[id]'));
  var links=[].slice.call(document.querySelectorAll('.toc a'));
  if(heads.length && links.length && 'IntersectionObserver' in window){
    new IntersectionObserver(function(es){
      es.forEach(function(en){
        if(!en.isIntersecting) return;
        links.forEach(function(a){ a.classList.toggle('on', a.getAttribute('href')==='#'+en.target.id); });
      });
    },{rootMargin:'-110px 0px -70% 0px'}).observe && heads.forEach(function(h){
      new IntersectionObserver(function(es){
        es.forEach(function(en){
          if(!en.isIntersecting) return;
          links.forEach(function(a){ a.classList.toggle('on', a.getAttribute('href')==='#'+en.target.id); });
        });
      },{rootMargin:'-110px 0px -70% 0px'}).observe(h);
    });
  }

  /* ── 범례 호버로 계열 강조 (선택) ── */
  document.querySelectorAll('.legend>span[data-series]').forEach(function(s){
    s.addEventListener('mouseenter',function(){
      var k=s.dataset.series;
      document.querySelectorAll('.chartwrap svg').forEach(function(svg){
        svg.classList.add('dim');
        svg.querySelectorAll('.cell').forEach(function(c){ c.classList.toggle('on', c.dataset.series===k); });
      });
    });
    s.addEventListener('mouseleave',function(){
      document.querySelectorAll('.chartwrap svg').forEach(function(svg){ svg.classList.remove('dim'); });
    });
  });

  /* ── 축 전환 토글 ── */
  document.querySelectorAll('.seg').forEach(function(seg){
    seg.addEventListener('click',function(e){
      var b=e.target.closest('button[data-view]'); if(!b)return;
      var wrap=seg.closest('section');
      seg.querySelectorAll('button').forEach(function(x){ x.setAttribute('aria-pressed', String(x===b)); });
      wrap.querySelectorAll('.view').forEach(function(v){ v.hidden = v.dataset.view!==b.dataset.view; });
    });
  });

  /* ── 강조 단계 (emphasis_steps) ──
     같은 차트, 같은 정렬. highlight 대상 외에는 .dimmed 를 건다.
     ★ 정렬이나 데이터를 바꾸지 않는다. 바꾸면 인지 세금이다 */
  document.querySelectorAll('.seg[data-mode="emph"]').forEach(function(seg){
    var sec = seg.closest('section');
    function apply(step){
      var spec = JSON.parse(seg.dataset.steps || '{}')[step] || [];
      var any = spec.length > 0;
      sec.querySelectorAll('.chartwrap [data-key],.chartwrap [data-series]').forEach(function(el){
        if(!any){ el.classList.remove('dimmed'); return; }
        var hit = spec.some(function(h){
          return (h.series && el.dataset.series === h.series)
              || (h.key    && el.dataset.key    === h.key);
        });
        el.classList.toggle('dimmed', !hit);
      });
      sec.querySelectorAll('.eread').forEach(function(p){ p.hidden = p.dataset.step !== step; });
    }
    seg.addEventListener('click', function(e){
      var b = e.target.closest('button[data-step]'); if(!b) return;
      seg.querySelectorAll('button').forEach(function(x){ x.setAttribute('aria-pressed', String(x===b)); });
      apply(b.dataset.step);
    });
    var init = seg.querySelector('button[aria-pressed="true"]');
    if(init) apply(init.dataset.step);
  });

  /* ── 드릴다운 ── */
  document.querySelectorAll('[data-drill]').forEach(function(el){
    if(el.tagName!=='BUTTON') return;
    el.addEventListener('click',function(){
      var k=el.dataset.drill, panel=document.querySelector('.drill[data-drill="'+k+'"]');
      var open=!panel.classList.contains('open');
      // 형제 패널은 닫는다
      var sec=el.closest('section');
      sec.querySelectorAll('.drill').forEach(function(p){ p.classList.remove('open'); });
      sec.querySelectorAll('button[data-drill]').forEach(function(b){ b.setAttribute('aria-expanded','false'); });
      if(open){ panel.classList.add('open'); el.setAttribute('aria-expanded','true'); }
    });
  });

  /* ── 지도 ↔ 표 연동 (선택) ── */
  document.querySelectorAll('.kmap path[data-key]').forEach(function(p){
    p.addEventListener('click',function(){
      var k=p.dataset.key;
      document.querySelectorAll('.kmap path').forEach(function(q){ q.classList.toggle('sel', q===p); });
      var row=document.querySelector('tr[data-key="'+k+'"]');
      if(row){ row.scrollIntoView({block:'nearest',behavior:'smooth'});
               document.querySelectorAll('tr[data-key]').forEach(function(r){ r.classList.toggle('hl', r===row); }); }
    });
  });

  /* ══════════════════════════════════════════════════════════════
     단락 · 배치 · 편집
     - 본문은 단락(.pg) 단위로 쓴다. 단락 하나 = 목차 한 줄 = 순서를 옮기는 단위
     - 배치: main[data-layout] = one(한 페이지) | side(사이드바) | menu(메뉴)
     - 편집: 작성자가 화면에서 글·순서·숨김·배치를 고치고 저장한다.
       원본은 그대로 두고, 고친 것만 <script id="rm-edits">에 적는다
     ══════════════════════════════════════════════════════════════ */
  var main=document.querySelector('main.wrap');
  var edNode=document.getElementById('rm-edits');
  if(!main) return;
  var pgs=[].slice.call(main.children).filter(function(n){return n.classList.contains('pg');});
  if(!pgs.length) return;   /* 단락으로 나누지 않은 본문은 예전처럼 한 페이지로 둔다 */

  var EDITS={};
  try{ EDITS=JSON.parse((edNode&&edNode.textContent)||'{}')||{}; }catch(_){ EDITS={}; }
  var LOCAL_KEY='rm-edits:'+location.pathname+'|'+document.title;
  var isFile=location.protocol==='file:';
  if(isFile){ try{ var ld=localStorage.getItem(LOCAL_KEY); if(ld){ EDITS=JSON.parse(ld); } }catch(_){} }
  EDITS.text=EDITS.text||{}; EDITS.order=EDITS.order||null; EDITS.hidden=EDITS.hidden||[];

  /* 단락 번호와 편집 대상 번호는 원본 순서로 매긴다 — 옮겨도 번호는 따라간다 */
  var ED_SEL='h1,h2,h3,h4,p,li,td,th,dd,dt';
  pgs.forEach(function(pg,i){
    pg.dataset.pid=String(i);
    var k=0;
    [].forEach.call(pg.querySelectorAll(ED_SEL),function(el){
      if(el.closest('svg,.chartwrap,.seg,.mask,[data-gen],.legend')) return;
      if(el.querySelector(ED_SEL+',button,svg,select,input')) return;
      var id='p'+i+'e'+(k++); el.dataset.eid=id;
      if(EDITS.text[id]!=null) el.innerHTML=EDITS.text[id];
    });
  });
  var ORIG={}; /* 원본 글 — 무엇을 고쳤는지 가리는 기준 */
  (function(){
    var box=document.createElement('div'); box.innerHTML=PRISTINE.body;
    var m=box.querySelector('main.wrap'); if(!m) return;
    [].filter.call(m.children,function(n){return n.classList.contains('pg');}).forEach(function(pg,i){
      var k=0;
      [].forEach.call(pg.querySelectorAll(ED_SEL),function(el){
        if(el.closest('svg,.chartwrap,.seg,.mask,[data-gen],.legend')) return;
        if(el.querySelector(ED_SEL+',button,svg,select,input')) return;
        ORIG['p'+i+'e'+(k++)]=clean(el);
      });
    });
  })();

  /* 틀: 목차(.pnav) + 본문(.pbody) + 메뉴 배치의 이전/다음 */
  var nav=document.createElement('nav'); nav.className='pnav'; nav.setAttribute('aria-label','목차');
  var body=document.createElement('div'); body.className='pbody';
  while(main.firstChild) body.appendChild(main.firstChild);
  main.appendChild(nav); main.appendChild(body);
  var pager=document.createElement('div'); pager.className='pager';
  pager.innerHTML='<button type="button" class="pgbtn" data-pg="-1">← 이전</button><button type="button" class="pgbtn" data-pg="1">다음 →</button>';
  body.insertBefore(pager, body.querySelector(':scope>.foot'));   /* 각주보다 위 */

  /* 저장된 순서·숨김을 적용한다 */
  if(EDITS.order&&EDITS.order.length){
    var byId={}; pgs.forEach(function(p){byId[p.dataset.pid]=p;});
    var seq=EDITS.order.map(function(id){return byId[id];}).filter(Boolean);
    pgs.forEach(function(p){ if(seq.indexOf(p)<0) seq.push(p); });
    var first=pgs[0], parent=first.parentNode, marker=document.createComment('pg');
    parent.insertBefore(marker,first);
    seq.forEach(function(p){ parent.insertBefore(p,marker); });
    parent.removeChild(marker);
  }
  EDITS.hidden.forEach(function(id){ var p=body.querySelector('.pg[data-pid="'+id+'"]'); if(p) p.classList.add('pg-off'); });

  function order(){ return [].slice.call(body.querySelectorAll(':scope>.pg')); }
  function shown(){ return order().filter(function(p){ return !p.classList.contains('pg-off')||document.body.classList.contains('editing'); }); }
  function label(p){
    if(p.dataset.nav) return p.dataset.nav;
    var h=p.querySelector('h2,h1,h3'); return h?h.textContent.trim():'단락';
  }
  var cur=null;
  function layout(){ return main.dataset.layout||'one'; }
  function setLayout(v){
    main.dataset.layout=v; render();
    var sw=document.querySelectorAll('.edbar [data-lay]');
    [].forEach.call(sw,function(b){ b.setAttribute('aria-pressed', String(b.dataset.lay===v)); });
  }
  function render(){
    var list=shown();
    if(!cur||list.indexOf(cur)<0) cur=list[0];
    nav.innerHTML='';
    list.forEach(function(p){
      var b=document.createElement('button'); b.type='button'; b.textContent=label(p);
      b.setAttribute('aria-current', String(p===cur));
      b.addEventListener('click',function(){
        if(layout()==='menu'){ go(p); window.scrollTo(0,0); }
        else { p.scrollIntoView({behavior:'smooth',block:'start'}); }
      });
      nav.appendChild(b);
    });
    order().forEach(function(p){ p.classList.toggle('cur', p===cur); });
    var i=list.indexOf(cur);
    pager.querySelector('[data-pg="-1"]').disabled=i<=0;
    pager.querySelector('[data-pg="1"]').disabled=i>=list.length-1;
    var mast=document.querySelector('.mast');
    document.documentElement.style.setProperty('--mastH',(mast?mast.getBoundingClientRect().height:0)+'px');
  }
  function go(p){ cur=p; render(); }
  pager.addEventListener('click',function(e){
    var b=e.target.closest('[data-pg]'); if(!b) return;
    var list=shown(), i=list.indexOf(cur)+(+b.dataset.pg);
    if(list[i]){ go(list[i]); main.scrollIntoView({block:'start'}); }
  });
  /* 사이드바 배치: 지금 읽는 단락을 목차에 표시한다 */
  window.addEventListener('scroll',function(){
    if(layout()!=='side') return;
    var top=(parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--mastH'))||0)+48;
    var list=shown(), c=list[0];
    list.forEach(function(p){ if(p.getBoundingClientRect().top<=top) c=p; });
    if(c!==cur){ cur=c; [].forEach.call(nav.children,function(b,i){ b.setAttribute('aria-current', String(list[i]===cur)); }); }
  },{passive:true});
  if(EDITS.layout) main.dataset.layout=EDITS.layout;
  render();

  /* ── 편집 ── */
  if(main.dataset.editable==='false') return;
  var bar=document.createElement('div'); bar.className='edbar';
  bar.innerHTML=
    '<span class="edmsg" role="status"></span>'+
    '<span class="edonly edlay" role="group" aria-label="배치">'+
      '<button type="button" data-lay="one">한 페이지</button><button type="button" data-lay="side">사이드바</button><button type="button" data-lay="menu">메뉴</button></span>'+
    '<button type="button" class="edonly" data-act="reset">원본으로</button>'+
    '<button type="button" class="edonly pri" data-act="save" disabled>저장</button>'+
    '<button type="button" data-act="toggle" aria-pressed="false">편집</button>';
  document.body.appendChild(bar);
  var msg=bar.querySelector('.edmsg'), saveBtn=bar.querySelector('[data-act="save"]');
  var dirty=false, cap=null;
  if(window.claude&&window.claude.use){ window.claude.use('artifact').then(function(a){cap=a;},function(){}); }
  if(isFile&&localStorage&&(function(){try{return localStorage.getItem(LOCAL_KEY);}catch(_){return null;}})()){
    msg.textContent='이 브라우저에 임시 저장된 수정이 적용돼 있습니다';
  }
  function mark(){ dirty=true; saveBtn.disabled=false; msg.textContent='저장하지 않은 수정이 있습니다'; }

  /* 단락마다 위로·아래로·숨기기 */
  order().forEach(function(p){
    var c=document.createElement('div'); c.className='pgctl';
    c.innerHTML='<button type="button" data-mv="-1">↑ 위로</button><button type="button" data-mv="1">↓ 아래로</button><button type="button" data-hide>숨기기</button>';
    p.insertBefore(c,p.firstChild);
    c.querySelector('[data-hide]').textContent=p.classList.contains('pg-off')?'보이기':'숨기기';
  });
  body.addEventListener('click',function(e){
    var b=e.target.closest('.pgctl button'); if(!b) return;
    var p=b.closest('.pg');
    if(b.dataset.mv){
      var all=order(), i=all.indexOf(p), to=all[i+(+b.dataset.mv)];
      if(to){ if(+b.dataset.mv<0) to.parentNode.insertBefore(p,to); else to.parentNode.insertBefore(p,to.nextSibling); mark(); render(); }
    } else if(b.hasAttribute('data-hide')){
      p.classList.toggle('pg-off'); b.textContent=p.classList.contains('pg-off')?'보이기':'숨기기'; mark(); render();
    }
  });
  function setEditing(on){
    document.body.classList.toggle('editing',on);
    var t=bar.querySelector('[data-act="toggle"]'); t.textContent=on?'편집 끝내기':'편집'; t.setAttribute('aria-pressed',String(on));
    [].forEach.call(document.querySelectorAll('[data-eid]'),function(el){
      if(on) el.setAttribute('contenteditable','true'); else el.removeAttribute('contenteditable');
    });
    setLayout(layout());
    if(!on&&dirty) msg.textContent='저장하지 않은 수정이 있습니다 · 편집을 다시 켜서 저장하세요';
  }
  document.addEventListener('input',function(e){ if(e.target.closest&&e.target.closest('[data-eid]')) mark(); });
  document.addEventListener('paste',function(e){
    var t=e.target.closest&&e.target.closest('[contenteditable="true"]'); if(!t) return;
    e.preventDefault(); var s=(e.clipboardData||window.clipboardData).getData('text/plain');
    document.execCommand('insertText',false,s);
  });
  bar.addEventListener('click',function(e){
    var b=e.target.closest('button'); if(!b) return;
    if(b.dataset.lay){ setLayout(b.dataset.lay); mark(); return; }
    var a=b.dataset.act;
    if(a==='toggle') setEditing(!document.body.classList.contains('editing'));
    if(a==='save') save(collect());
    if(a==='reset'){
      if(b.dataset.armed){ save({}, true); }
      else { b.dataset.armed='1'; b.textContent='한 번 더 누르면 원본으로'; setTimeout(function(){ delete b.dataset.armed; b.textContent='원본으로'; },4000); }
    }
  });

  /* 고친 글은 굵게·기울임·줄바꿈·용어 표시만 남기고 나머지 태그를 벗긴다 */
  function clean(node){
    var out=document.createElement('div');
    (function walk(src,dst){
      [].forEach.call(src.childNodes,function(n){
        if(n.nodeType===3){ dst.appendChild(document.createTextNode(n.nodeValue)); return; }
        if(n.nodeType!==1) return;
        var tg=n.tagName;
        if(tg==='BR'){ dst.appendChild(document.createElement('br')); return; }
        if(tg==='B'||tg==='STRONG'||tg==='I'||tg==='EM'){
          var e=document.createElement(tg==='STRONG'?'b':tg==='EM'?'i':tg.toLowerCase()); dst.appendChild(e); walk(n,e); return; }
        if(tg==='ABBR'&&n.getAttribute('data-term')){
          var a=document.createElement('abbr'); a.className='term'; a.setAttribute('data-term',n.getAttribute('data-term'));
          a.tabIndex=0; dst.appendChild(a); walk(n,a); return; }
        if(tg==='SPAN'&&/\b(tag|vd|stat)\b/.test(n.className)){
          var s=document.createElement('span'); s.className=n.className.replace(/[^\w\s-]/g,''); dst.appendChild(s); walk(n,s); return; }
        walk(n,dst);
      });
    })(node,out);
    return out.innerHTML;
  }
  function collect(){
    var st={text:{},hidden:[],layout:layout()};
    [].forEach.call(document.querySelectorAll('[data-eid]'),function(el){
      var h=clean(el); if(h!==ORIG[el.dataset.eid]) st.text[el.dataset.eid]=h;
    });
    var ids=order().map(function(p){return p.dataset.pid;});
    if(ids.join()!==ids.slice().sort(function(a,b){return a-b;}).join()) st.order=ids;
    order().forEach(function(p){ if(p.classList.contains('pg-off')) st.hidden.push(p.dataset.pid); });
    if(st.layout===PRISTINE_LAYOUT) delete st.layout;   /* 원래 배치 그대로면 적지 않는다 */
    return st;
  }
  var PRISTINE_LAYOUT=(function(){ var m=/<main[^>]*data-layout="(\w+)"/.exec(PRISTINE.body); return m?m[1]:'one'; })();
  var RESET=':root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#faf9f5;color:#141413}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}';
  function buildDoc(st){
    var json=JSON.stringify(st).replace(/</g,'\\u003c');
    var b=PRISTINE.body.replace(/(<script type="application\/json" id="rm-edits">)[\s\S]*?(<\/script>)/, function(_,a,z){ return a+json+z; });
    return '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>'+RESET+'</style></head><body>'+
      '<title>'+PRISTINE.title.replace(/</g,'&lt;')+'</title>'+
      PRISTINE.styles.map(function(s){return '<style>'+s+'</style>';}).join('')+b+'</body></html>';
  }
  /* 저장 순서 (AGENTS.md 2장 폴백):
     ① claude.ai 게시본 — 페이지가 스스로 새 버전으로 저장
     ② 그 기능이 없으면 — 이 브라우저에 임시 보관 + 고친 파일 내려받기
     ③ 둘 다 안 되면 — 저장할 수 없다고 알린다 */
  function save(st, reset){
    saveBtn.disabled=true; msg.textContent='저장 중…';
    if(cap){
      cap.publish(buildDoc(st)).then(function(){ dirty=false; msg.textContent='저장했습니다'; },
        function(err){
          var c=err&&err.code;
          msg.textContent = c==='conflict' ? '다른 곳에서 먼저 저장해 새 버전으로 바뀝니다'
            : (c==='not_granted'||c==='not_writer') ? '이 화면에서는 저장 권한이 없습니다'
            : '저장하지 못했습니다. 다시 눌러 주세요';
          saveBtn.disabled=false;
        });
      return;
    }
    var kept=false;
    try{ if(reset) localStorage.removeItem(LOCAL_KEY); else localStorage.setItem(LOCAL_KEY, JSON.stringify(st)); kept=true; }catch(_){}
    var dl=false;
    try{
      var blob=new Blob([buildDoc(st)],{type:'text/html'}), a=document.createElement('a');
      a.href=URL.createObjectURL(blob); a.download=(document.title||'report').replace(/[\\/:*?"<>|]/g,'_')+'.html';
      document.body.appendChild(a); a.click(); a.remove(); dl=true;
    }catch(_){}
    dirty=false;
    msg.textContent = kept&&dl ? '이 브라우저에 임시 보관하고, 고친 파일을 내려받았습니다'
      : kept ? '이 브라우저에만 임시 보관했습니다'
      : dl ? '고친 파일을 내려받았습니다'
      : '이 환경에서는 저장할 수 없습니다';
    if(reset&&kept) location.reload();
  }
})();
