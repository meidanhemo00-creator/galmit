/* חמו גלמית · landing page interactions (no dependencies) */
(() => {
  'use strict';

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const mobileMQ = matchMedia('(max-width: 759px)');
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');

  /* ---------- Category data (verified against galmit.co.il) ---------- */
  const CATEGORIES = {
    bulk: {
      name: 'שקי ענק', tag: 'FIBC · BULK BAG', cta: 'שקי ענק',
      desc: 'שקי ענק (באלות, ביג בג) לאריזת חומרים בכמויות גדולות. עשויים פוליפרופילן ארוג ולא ממוחזר עם UV.',
      opts: ['מגוון מידות במלאי השוטף', 'פוליפרופילן ארוג ולא ממוחזר, עם UV', 'הדפסה עד 4 צבעים']
    },
    pp: {
      name: 'שקי פוליפרופילן', tag: 'PP WOVEN SACK', cta: 'שקי פוליפרופילן',
      desc: 'שקים קטנים עשויים פוליפרופילן ארוג, לאריזה ולשינוע של חומרים בכמויות קטנות יותר.',
      opts: ['מגוון מידות לפי צורכי הלקוח', 'מגוון משקלים', 'בד פוליפרופילן ארוג']
    },
    paper: {
      name: 'שקיות נייר', tag: 'KRAFT · 1 KG', cta: 'שקיות נייר',
      desc: 'שקיות נייר 1 ק״ג למילוי קמח, סוכר, מלח ועוד.',
      opts: ['ייצור מקומי (כחול-לבן) ו/או ייבוא', 'עיצוב גרפיקה בליווי צמוד לפי דרישה', 'אספקה: 7 ימי עסקים מיום אישור הגלופות']
    },
    coal: {
      name: 'שקי פחם', tag: 'CHARCOAL BAG', cta: 'שקי פחם',
      desc: 'שקי פחם במגוון מידות, למשקלים שונים, זמינים במלאי השוטף.',
      opts: ['ידית אחיזה בשקים עד 4 ק״ג', 'גרפיקה בעיצוב אישי', 'מגוון מידות במלאי']
    },
    special: {
      name: 'שקים מיוחדים ועזרים', tag: 'VALVE · THREAD', cta: 'שקים מיוחדים ועזרים',
      desc: 'שקי פייה (VALVE) מבד פוליפרופילן ארוג לא ממוחזר, עם פיית מילוי ותחתית מרובעת. לצדם, חוטי פוליאתילן לתפירת שקים.',
      opts: ['פיית מילוי ותחתית מרובעת', 'חוטי תפירה במגוון משקלים, למכונות ידניות ואוטומטיות', 'חוטים בצבעים שונים לפי הזמנה']
    }
  };
  const ORDER = Object.keys(CATEGORIES);

  /* ---------- Header ---------- */
  const header = $('[data-header]');
  const menuBtn = $('[data-menu-toggle]');
  const menu = $('[data-mobile-menu]');

  const setMenu = (open) => {
    menuBtn.setAttribute('aria-expanded', String(open));
    menu.hidden = !open;
    document.documentElement.style.overflow = open ? 'hidden' : '';
    if (open) menu.querySelector('a')?.focus();
  };
  menuBtn.addEventListener('click', () => setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menuBtn.getAttribute('aria-expanded') === 'true') { setMenu(false); menuBtn.focus(); }
  });
  mobileMQ.addEventListener?.('change', () => setMenu(false));

  // Active nav link
  const navLinks = $$('.nav__list a');
  const navTargets = navLinks.map((a) => $(a.getAttribute('href'))).filter(Boolean);
  const navIO = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      navLinks.forEach((a) => a.setAttribute('aria-current', String(a.getAttribute('href') === '#' + en.target.id)));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  navTargets.forEach((t) => navIO.observe(t));

  /* ---------- Hero ---------- */
  const hero = $('[data-hero]');
  const heroArt = $('.hero__media', hero);
  const ready = () => { hero.classList.add('is-ready'); heroArt?.classList.add('is-drawn'); };
  requestAnimationFrame(() => requestAnimationFrame(ready));
  $$('[data-reveal]', hero).forEach((el) => el.classList.add('is-in'));

  // Technical layer follows the mobile crop of the image

  // Gentle pointer depth
  const layers = $$('[data-depth]', hero);
  let raf = 0;
  hero.addEventListener('pointermove', (e) => {
    if (reduceMotion.matches || !finePointer.matches) return;
    const r = hero.getBoundingClientRect();
    const dx = (e.clientX - r.left) / r.width - .5;
    const dy = (e.clientY - r.top) / r.height - .5;
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => {
      layers.forEach((l) => {
        const d = parseFloat(l.dataset.depth);
        l.style.transform = `translate3d(${(-dx * 14 * d).toFixed(2)}px, ${(-dy * 10 * d).toFixed(2)}px, 0)`;
      });
    });
  });
  hero.addEventListener('pointerleave', () => layers.forEach((l) => { l.style.transform = ''; }));

  // Hotspots
  const hotspotBtns = $$('[data-hotspot]');
  const closeHotspots = (except) => hotspotBtns.forEach((b) => {
    if (b === except) return;
    b.setAttribute('aria-expanded', 'false');
    $('#' + b.getAttribute('aria-controls')).hidden = true;
  });
  hotspotBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const card = $('#' + btn.getAttribute('aria-controls'));
      const open = btn.getAttribute('aria-expanded') !== 'true';
      closeHotspots(btn);
      btn.setAttribute('aria-expanded', String(open));
      card.hidden = !open;
      if (open) {
        const spot = btn.parentElement;
        spot.classList.remove('hotspot--flip');
        const rr = card.getBoundingClientRect();
        if (rr.right > window.innerWidth - 12) spot.classList.add('hotspot--flip');
      }
    });
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('.hotspot')) closeHotspots(); });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const open = hotspotBtns.find((b) => b.getAttribute('aria-expanded') === 'true');
    if (open) { closeHotspots(); open.focus(); }
  });

  /* ---------- Scroll reveals ---------- */
  const revealEls = $$('.section-head, .about__text, .about__figure, .explorer, .finder__head, .finder__grid, .mtile, .config, .step, .faq__head, .accordion, .contact__intro, .contact__form');
  revealEls.forEach((el) => el.classList.add('reveal'));
  const revealIO = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('is-in'); revealIO.unobserve(en.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: .06 });
  revealEls.forEach((el) => revealIO.observe(el));

  /* ---------- Illustrations draw in once when they enter the viewport ---------- */
  const ilIO = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('is-drawn'); ilIO.unobserve(en.target); }
    });
  }, { threshold: .25 });
  $$('.il-anim').forEach((el) => { if (!el.closest('[data-explorer]')) ilIO.observe(el); });
  const exIO = new IntersectionObserver((entries) => {
    if (entries.some((en) => en.isIntersecting)) {
      $('[data-explorer] .pv.is-active')?.classList.add('is-drawn');
      exIO.disconnect();
    }
  }, { threshold: .3 });
  exIO.observe($('[data-explorer] .explorer__visual'));

  /* ---------- Contact form references (used by explorer + finder) ---------- */
  const form = $('[data-contact-form]');
  const fCategory = $('#f-category');
  const fNeed = $('#f-need');
  const setCategory = (name) => { if (name) fCategory.value = name; };

  /* ---------- Product explorer ---------- */
  const explorer = $('[data-explorer]');
  const tabs = $$('[role="tab"]', explorer);
  const panel = $('[data-panel]', explorer);
  const info = $('.explorer__info', explorer);
  const counter = $('[data-counter]', explorer);
  let current = 'bulk';
  let swapTimer = 0;

  const renderInfo = (key) => {
    const c = CATEGORIES[key];
    $('[data-field="tag"]', info).textContent = c.tag;
    $('[data-field="name"]', info).textContent = c.name;
    $('[data-field="desc"]', info).textContent = c.desc;
    $('[data-field="cta"]', info).textContent = c.cta;
    const ul = $('[data-field="opts"]', info);
    ul.replaceChildren(...c.opts.map((t) => Object.assign(document.createElement('li'), { textContent: t })));
  };

  const selectCategory = (key, { focus = false } = {}) => {
    if (!CATEGORIES[key]) return;
    tabs.forEach((t) => {
      const on = t.dataset.cat === key;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus();
    });
    panel.setAttribute('aria-labelledby', 'tab-' + key);
    if (key === current) return;
    current = key;
    $$('[data-visual-for]', explorer).forEach((v) => {
      const on = v.dataset.visualFor === key;
      v.classList.toggle('is-active', on);
      v.classList.remove('is-drawn');
      if (on) requestAnimationFrame(() => requestAnimationFrame(() => v.classList.add('is-drawn')));
    });
    counter.textContent = String(ORDER.indexOf(key) + 1).padStart(2, '0');
    clearTimeout(swapTimer);
    if (reduceMotion.matches) { renderInfo(key); return; }
    info.classList.add('is-swapping');
    swapTimer = setTimeout(() => { renderInfo(key); info.classList.remove('is-swapping'); }, 220);
  };

  tabs.forEach((t) => t.addEventListener('click', () => selectCategory(t.dataset.cat)));
  explorer.querySelector('[role="tablist"]').addEventListener('keydown', (e) => {
    const i = ORDER.indexOf(current);
    const map = { ArrowDown: 1, ArrowUp: -1, ArrowLeft: 1, ArrowRight: -1 }; // RTL: left moves forward
    let next = null;
    if (e.key in map) next = ORDER[(i + map[e.key] + ORDER.length) % ORDER.length];
    if (e.key === 'Home') next = ORDER[0];
    if (e.key === 'End') next = ORDER[ORDER.length - 1];
    if (next) { e.preventDefault(); selectCategory(next, { focus: true }); }
  });

  $('[data-inquire]', explorer).addEventListener('click', () => {
    const name = CATEGORIES[current].name;
    setCategory(name);
    if (!fNeed.value.trim()) fNeed.value = `פנייה בנושא ${name}.\n`;
  });

  // Links elsewhere that point at a category
  $$('[data-select-category]').forEach((a) => a.addEventListener('click', () => {
    const key = a.dataset.selectCategory;
    selectCategory(key);
    if (a.getAttribute('href') === '#contact') setCategory(CATEGORIES[key].name);
  }));

  /* ---------- Finder ---------- */
  const finder = $('[data-finder]');
  const fForm = $('[data-finder-form]', finder);
  const steps = $$('.finder__step', finder);
  const summary = $('.finder__summary', finder);
  const progress = $$('[data-progress]', finder);
  const backBtn = $('[data-finder-back]', finder);
  const nav = $('[data-finder-nav]', finder);
  const status = $('[data-finder-status]', finder);
  const numEl = $('[data-finder-num]', finder);
  const view = $('[data-stage-view]', finder);
  const stageName = $('[data-stage-name]', finder);
  const tag = $('[data-tag]', finder);
  const KEY = { 'שקי ענק': 'bulk', 'שקי פוליפרופילן': 'pp', 'שקיות נייר': 'paper', 'שקי פחם': 'coal' };
  const answers = {};
  let stepIdx = 0;
  let advanceTimer = 0;

  const suggest = () => {
    const m = answers.material || '', n = answers.need || '', ind = answers.industry || '';
    if (m === 'פחם') return 'שקי פחם';
    if (n === 'אריזה בכמויות גדולות' || m.startsWith('חול')) return 'שקי ענק';
    if (m.startsWith('קמח') && ind === 'מזון') return 'שקיות נייר';
    if (m.startsWith('קמח') || m.startsWith('גרגרים')) return 'שקי פוליפרופילן';
    return '';
  };

  const showStep = (i) => {
    stepIdx = i;
    steps.forEach((s, k) => { s.hidden = k !== i; s.classList.toggle('is-active', k === i); });
    summary.hidden = i < steps.length;
    nav.hidden = i >= steps.length;
    backBtn.hidden = i === 0;
    progress.forEach((p, k) => {
      p.classList.toggle('is-current', k === i);
      p.classList.toggle('is-done', k < i);
    });
    numEl.textContent = String(Math.min(i + 1, 3)).padStart(2, '0');
    tag.classList.toggle('is-ready', i >= steps.length);
    if (i < steps.length) {
      status.textContent = `שלב ${i + 1} מתוך 3`;
    } else {
      const s = suggest();
      const hint = $('[data-sum="hint"]', summary);
      hint.replaceChildren();
      if (s) {
        hint.append('כיוון ראשוני לבדיקה: ', Object.assign(document.createElement('strong'), { textContent: s }), '. את ההתאמה הסופית בודקים יחד עם הצוות.');
      } else {
        hint.textContent = 'הצוות יעזור לכם לבחור את סוג האריזה המתאים, לפי החומר והשימוש.';
      }
      if (answers.need === 'הדפסה על האריזה') hint.append(' כדאי לציין בפנייה כמה צבעים נדרשים ואם יש קובץ גרפי.');
      summary.dataset.suggest = s;
      summary.focus({ preventScroll: true });
    }
  };

  // Live brief: the tag fills and the stage draws the likely packaging as answers come in
  let logoURL = '';
  const renderLive = (changed) => {
    ['industry', 'material', 'need'].forEach((k) => {
      const dd = $(`[data-sum="${k}"]`, tag);
      const v = answers[k] || '—';
      if (dd.textContent !== v) {
        dd.textContent = v;
        const row = dd.parentElement;
        if (k === changed) { row.classList.remove('is-new'); void row.offsetWidth; row.classList.add('is-new'); }
      }
    });
    const s = suggest();
    const key = KEY[s] || (logoURL ? 'bulk' : 'none');
    if (view.dataset.current !== key) {
      view.dataset.current = key;
      $$('[data-art]', view).forEach((a) => {
        a.classList.remove('is-drawn');
        if (a.dataset.art === key) requestAnimationFrame(() => requestAnimationFrame(() => a.classList.add('is-drawn')));
      });
    }
    stageName.textContent = s || (answers.material ? 'נבחר יחד עם הצוות' : 'עוד לא נבחר');
  };

  // Logo try-on: local preview only, nothing is uploaded
  const stage = $('.fstage', finder);
  const logoInput = $('[data-logo-input]', finder);
  const logoClear = $('[data-logo-clear]', finder);
  const logoLabel = $('[data-logo-label]', finder);
  const logoNote = $('[data-logo-note]', finder);
  const setLogo = (url) => {
    if (logoURL) URL.revokeObjectURL(logoURL);
    logoURL = url;
    $$('.il-logo image', stage).forEach((im) => { if (url) im.setAttribute('href', url); else im.removeAttribute('href'); });
    stage.classList.toggle('has-logo', !!url);
    logoClear.hidden = !url;
    logoLabel.textContent = url ? 'החלפת לוגו' : 'העלו לוגו וראו אותו על השק';
    if (url && view.dataset.current === 'none') { view.dataset.current = 'bulk'; $('[data-art="bulk"]', view).classList.add('is-drawn'); stageName.textContent = 'שק ענק, להמחשה'; }
  };
  logoInput.addEventListener('change', () => {
    const file = logoInput.files[0];
    if (!file) return;
    if (!/^image\/(png|jpeg|svg\+xml|webp)$/.test(file.type)) { logoNote.textContent = 'אפשר להעלות PNG, JPG, SVG או WEBP.'; return; }
    if (file.size > 5 * 1024 * 1024) { logoNote.textContent = 'הקובץ גדול מ-5MB. נסו קובץ קטן יותר.'; return; }
    logoNote.textContent = 'הקובץ נשאר אצלכם בדפדפן ולא נשלח. ההדמיה להמחשה בלבד. כשתשלחו את הפנייה, צרפו את הלוגו למייל.';
    setLogo(URL.createObjectURL(file));
  });
  logoClear.addEventListener('click', () => { logoInput.value = ''; setLogo(''); logoInput.focus(); });

  fForm.addEventListener('change', (e) => {
    const input = e.target;
    if (input.type !== 'radio') return;
    answers[input.name] = input.value;
    renderLive(input.name);
    clearTimeout(advanceTimer);
    const go = () => {
      showStep(stepIdx + 1);
      if (stepIdx < steps.length) steps[stepIdx].querySelector('input')?.focus({ preventScroll: true });
    };
    // A short pause lets the selection register visually; keyboard users can keep arrowing.
    advanceTimer = setTimeout(go, reduceMotion.matches ? 0 : 320);
  });
  // Arrow keys inside a radio group fire "change" too; don't auto-advance for those, wait for Enter/Space.
  fForm.addEventListener('keydown', (e) => {
    if (e.target.type !== 'radio') return;
    if (e.key.startsWith('Arrow')) {
      setTimeout(() => clearTimeout(advanceTimer), 0);
    }
    if (e.key === 'Enter') {
      e.preventDefault();
      answers[e.target.name] = e.target.value;
      e.target.checked = true;
      renderLive(e.target.name);
      showStep(stepIdx + 1);
      if (stepIdx < steps.length) steps[stepIdx].querySelector('input')?.focus({ preventScroll: true });
    }
  });
  fForm.addEventListener('submit', (e) => e.preventDefault());
  backBtn.addEventListener('click', () => {
    showStep(Math.max(0, stepIdx - 1));
    steps[stepIdx].querySelector('input:checked, input')?.focus({ preventScroll: true });
  });
  $('[data-finder-restart]', finder).addEventListener('click', () => {
    fForm.reset();
    Object.keys(answers).forEach((k) => delete answers[k]);
    renderLive();
    showStep(0);
    steps[0].querySelector('input')?.focus({ preventScroll: true });
  });
  $('[data-finder-send]', finder).addEventListener('click', () => {
    const s = summary.dataset.suggest;
    if (s) setCategory(s);
    const lines = [
      `תחום: ${answers.industry}`,
      `חומר לאריזה: ${answers.material}`,
      `דרישה עיקרית: ${answers.need}`,
      '',
      ...(logoURL ? ['לוגו: אצרף את קובץ הלוגו למייל.'] : []),
      'פרטים נוספים (כמויות, מידות, הדפסה):',
      ''
    ].join('\n');
    const prev = fNeed.value.trim();
    fNeed.value = prev && !prev.startsWith('תחום:') ? `${lines}\n${prev}` : lines;
    setTimeout(() => $('#f-name').focus({ preventScroll: true }), 650);
  });
  status.textContent = 'בחרו תשובה כדי להמשיך';

  /* ---------- Materials: one card open at a time ---------- */
  const mcards = $$('[data-mcard]');
  mcards.forEach((card) => {
    const btn = $('[data-mtoggle]', card);
    btn.addEventListener('click', () => {
      const willOpen = btn.getAttribute('aria-expanded') !== 'true';
      mcards.forEach((c) => {
        const on = c === card && willOpen;
        c.classList.toggle('is-open', on);
        $('[data-mtoggle]', c).setAttribute('aria-expanded', String(on));
        if (on) $('.il-anim', c)?.classList.add('is-drawn');
      });
    });
  });

  /* ---------- Process: scroll-linked line ---------- */
  const stepsList = $('.steps');
  const stepItems = $$('.step', stepsList);
  let ticking = false;
  const updateProcess = () => {
    ticking = false;
    const vh = window.innerHeight;
    const r = stepsList.getBoundingClientRect();
    if (r.bottom < -200 || r.top > vh + 200) return;
    const vertical = mobileMQ.matches;
    const line = vh * .72;
    const p = vertical
      ? Math.min(1, Math.max(0, (line - r.top) / r.height))
      : Math.min(1, Math.max(0, (vh * .85 - r.top) / (vh * .5)));
    stepsList.style.setProperty('--p', p.toFixed(3));
    stepItems.forEach((s, i) => {
      const lit = vertical ? s.getBoundingClientRect().top < line : p >= i / stepItems.length + .02;
      s.classList.toggle('is-lit', lit);
    });
  };

  /* ---------- Header + action bar on scroll ---------- */
  const actionBar = $('[data-action-bar]');
  const contact = $('#contact');
  const onScroll = () => {
    const y = window.scrollY;
    header.classList.toggle('is-compact', y > 40);
    const heroBottom = hero.getBoundingClientRect().bottom;
    const contactTop = contact.getBoundingClientRect().top;
    actionBar.classList.toggle('is-visible', heroBottom < 0 && contactTop > window.innerHeight * .6);
    if (!ticking) { ticking = true; requestAnimationFrame(updateProcess); }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();

  /* ---------- FAQ accordion ---------- */
  $$('[data-accordion] .acc button').forEach((btn) => btn.addEventListener('click', () => {
    const open = btn.getAttribute('aria-expanded') !== 'true';
    btn.setAttribute('aria-expanded', String(open));
    btn.closest('.acc').classList.toggle('is-open', open);
  }));

  /* ---------- Contact form: validation + email composition ---------- */
  const formStatus = $('[data-form-status]', form);
  const MAILTO = 'bags@pashutyarok.co.il';
  const fields = {
    name: $('#f-name'), company: $('#f-company'), phone: $('#f-phone'), email: $('#f-email'), need: fNeed
  };
  let attempted = false;

  const setErr = (key, msg) => {
    const el = fields[key];
    const err = $(`[data-err-for="${key}"]`, form);
    if (err) err.textContent = msg || '';
    el.setAttribute('aria-invalid', msg ? 'true' : 'false');
  };

  const validate = () => {
    const v = (k) => fields[k].value.trim();
    const errors = {};
    if (v('name').length < 2) errors.name = 'נא למלא שם מלא.';
    const digits = v('phone').replace(/\D/g, '');
    const hasPhone = digits.length > 0;
    const hasEmail = v('email').length > 0;
    if (hasPhone && (digits.length < 9 || digits.length > 12)) errors.phone = 'מספר הטלפון נראה חסר. נא לבדוק.';
    if (hasEmail && (fields.email.validity.typeMismatch || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('email')))) errors.email = 'כתובת האימייל לא תקינה.';
    if (!hasPhone && !hasEmail) { errors.phone = 'נא להשאיר טלפון או אימייל.'; }
    if (v('need').length < 5) errors.need = 'ספרו לנו בכמה מילים מה אתם צריכים.';
    ['name', 'phone', 'email', 'need'].forEach((k) => setErr(k, errors[k]));
    return errors;
  };

  Object.values(fields).forEach((el) => el.addEventListener('input', () => { if (attempted) validate(); }));

  const composeBody = () => {
    const v = (k) => fields[k].value.trim();
    const lines = [`שם מלא: ${v('name')}`];
    if (v('company')) lines.push(`חברה: ${v('company')}`);
    if (v('phone')) lines.push(`טלפון: ${v('phone')}`);
    if (v('email')) lines.push(`אימייל: ${v('email')}`);
    if (fCategory.value) lines.push(`סוג אריזה: ${fCategory.value}`);
    lines.push('', 'תיאור הצורך:', v('need'));
    return lines.join('\n');
  };
  const subject = () => `פנייה מהאתר${fCategory.value ? `: ${fCategory.value}` : ''}${fields.company.value.trim() ? ` · ${fields.company.value.trim()}` : ''}`;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    attempted = true;
    const errors = validate();
    const first = ['name', 'phone', 'email', 'need'].find((k) => errors[k]);
    if (first) {
      formStatus.textContent = 'יש כמה פרטים להשלים לפני שממשיכים.';
      fields[first].focus();
      return;
    }
    const href = `mailto:${MAILTO}?subject=${encodeURIComponent(subject())}&body=${encodeURIComponent(composeBody())}`;
    window.location.href = href;
    formStatus.textContent = 'ביקשנו מתוכנת הדואר שלכם לפתוח טיוטה מוכנה. הפנייה תישלח רק אחרי שתלחצו "שלח" שם. לא נפתח כלום? העתיקו את הפרטים או התקשרו 1-700-700-029.';
  });

  $('[data-copy]', form).addEventListener('click', async () => {
    const text = `${subject()}\n\n${composeBody()}`;
    try {
      await navigator.clipboard.writeText(text);
      formStatus.textContent = `הפרטים הועתקו. אפשר להדביק אותם במייל ל-${MAILTO}.`;
    } catch {
      formStatus.textContent = `לא הצלחנו להעתיק אוטומטית. אפשר לכתוב ישירות ל-${MAILTO}.`;
    }
  });
})();
