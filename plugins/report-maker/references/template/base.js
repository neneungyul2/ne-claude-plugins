(function(){
  /* ── 용어 사전. spec 의 glossary 를 그대로 넣는다 ── */
  /* d 에는 뜻만 적지 않는다. 그 말이 오해받는 지점까지 적는다
     (예: 외부 기준 지표라면 "사내 기준과 합산하지 않는다"까지) */
  var GLOSSARY = {
    "{{TERM_ID}}": {t:"{{용어}} ({{원어}})", d:"{{뜻}}. {{이 말이 오해받는 지점}}."}
  };

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
})();
