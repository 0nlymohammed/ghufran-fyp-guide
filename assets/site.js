(() => {
  const T = JSON.parse(document.getElementById('i18n').textContent);
  const live = document.getElementById('live');
  const fmt = (s, o) => s.replace(/\{(\w)\}/g, (_, k) => o[k]);
  const say = (msg) => { live.textContent = ''; setTimeout(() => { live.textContent = msg; }, 30); };

  // Language choice is remembered so the root page opens in the last language used.
  document.querySelectorAll('[data-setlang]').forEach((a) => a.addEventListener('click', () => {
    try { localStorage.setItem('microseg-lang', a.dataset.setlang); } catch (e) { /* private mode */ }
  }));

  // Theme: follows the system until the reader picks one, then the choice is remembered.
  const root = document.documentElement;
  const themeBtn = document.querySelector('[data-theme-toggle]');
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const paint = () => {
    const dark = root.dataset.theme === 'dark';
    if (themeMeta) themeMeta.content = dark ? '#0f1826' : '#e6ebf1';
    if (themeBtn) {
      themeBtn.textContent = dark ? T.themeLight : T.themeDark;
      themeBtn.setAttribute('aria-label', dark ? T.toLight : T.toDark);
    }
  };
  if (themeBtn) {
    themeBtn.hidden = false;
    themeBtn.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('microseg-theme', root.dataset.theme); } catch (e) { /* private mode */ }
      paint();
    });
  }
  paint();
  window.addEventListener('storage', (e) => {
    if (e.key === 'microseg-theme' && e.newValue) { root.dataset.theme = e.newValue; paint(); }
  });

  // Copy buttons.
  document.querySelectorAll('.copy').forEach((btn) => {
    const original = btn.textContent;
    let timer;
    btn.addEventListener('click', async () => {
      const code = btn.closest('figure').querySelector('pre code');
      const text = code.textContent;
      clearTimeout(timer);
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = T.copied;
        btn.dataset.state = 'done';
        say(T.copied);
      } catch (e) {
        const r = document.createRange();
        r.selectNodeContents(code);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(r);
        btn.textContent = T.copyFail;
        say(T.copyFail);
      }
      timer = setTimeout(() => { btn.textContent = original; delete btn.dataset.state; }, btn.dataset.state ? 2000 : 5000);
    });
  });

  // Code blocks are tab stops only when they scroll, so the keyboard can reach hidden text.
  const scrollables = () => document.querySelectorAll('.code pre').forEach((pre) => {
    if (pre.scrollWidth > pre.clientWidth + 1 || pre.scrollHeight > pre.clientHeight + 1) pre.tabIndex = 0;
    else pre.removeAttribute('tabindex');
  });
  scrollables();
  let rt;
  window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(scrollables, 200); });

  // Side list: always open on wide screens, closed by default on narrow ones.
  const rail = document.querySelector('.rail');
  if (rail) {
    const wide = window.matchMedia('(min-width: 1000px)');
    const sync = () => { rail.open = wide.matches; };
    sync();
    wide.addEventListener('change', sync);
    rail.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => { if (!wide.matches) rail.open = false; }));
  }

  // Step tracker (quick path only).
  const main = document.querySelector('main.quick');
  if (!main) return;
  const KEY = 'microseg-steps-v1';
  const boxes = [...main.querySelectorAll('input[data-step]')];
  const total = boxes.length;
  let done;
  try { done = new Set(JSON.parse(localStorage.getItem(KEY) || '[]')); } catch (e) { done = new Set(); }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify([...done])); } catch (e) { /* private mode */ } };
  const doneOf = main.querySelector('[data-done-of]');
  const next = main.querySelector('[data-next]');
  const bar = main.querySelector('.progress .bar span');
  const reset = main.querySelector('[data-reset]');
  const sumCount = document.querySelector('[data-sum-count]');

  const update = () => {
    let count = 0;
    boxes.forEach((b) => {
      const on = done.has(b.dataset.step);
      b.checked = on;
      b.closest('.step').classList.toggle('done', on);
      if (on) count += 1;
    });
    doneOf.textContent = count === total ? fmt(T.allDone, { t: total }) : fmt(T.doneOf, { d: count, t: total });
    if (sumCount) sumCount.textContent = fmt(T.sumCount, { d: count, t: total });
    bar.style.width = `${(count / total) * 100}%`;
    const first = boxes.find((b) => !b.checked);
    if (first) {
      const step = first.closest('.step');
      next.hidden = false;
      next.href = `#${step.id}`;
      next.textContent = fmt(T.next, { s: step.querySelector('h3').textContent.trim() });
    } else {
      next.hidden = true;
    }
    reset.hidden = count === 0;
    main.querySelectorAll('section.stage').forEach((sec) => {
      const inner = [...sec.querySelectorAll('input[data-step]')];
      const d = inner.filter((b) => b.checked).length;
      const n = sec.dataset.stage;
      const li = document.querySelector(`.route li[data-stage="${n}"]`);
      const c = document.querySelector(`[data-stage-count="${n}"]`);
      if (c) c.textContent = fmt(T.stageCount, { d, t: inner.length });
      if (li) {
        li.classList.toggle('done', inner.length > 0 && d === inner.length);
        li.classList.toggle('partial', d > 0 && d < inner.length);
      }
    });
  };

  boxes.forEach((b) => b.addEventListener('change', () => {
    if (b.checked) done.add(b.dataset.step); else done.delete(b.dataset.step);
    save();
    update();
  }));
  reset.addEventListener('click', () => {
    if (!window.confirm(T.confirm)) return;
    done.clear();
    save();
    update();
    next.focus();
    say(T.cleared);
  });
  window.addEventListener('storage', (e) => {
    if (e.key !== KEY) return;
    try { done = new Set(JSON.parse(e.newValue || '[]')); } catch (err) { done = new Set(); }
    update();
  });
  update();

  // Mark the stage in view in the side list.
  if ('IntersectionObserver' in window) {
    const links = new Map([...document.querySelectorAll('.route a')].map((a) => [a.getAttribute('href').slice(1), a]));
    const seen = new Map();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => seen.set(e.target.id, e.isIntersecting));
      const current = [...links.keys()].find((id) => seen.get(id));
      links.forEach((a, id) => { if (id === current) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
    }, { rootMargin: '0px 0px -60% 0px' });
    links.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
  }
})();
