const navButton = document.querySelector('.nav-toggle');
const siteNav = document.querySelector('.site-nav');

if (navButton && siteNav) {
  navButton.addEventListener('click', () => {
    const isOpen = navButton.getAttribute('aria-expanded') === 'true';
    navButton.setAttribute('aria-expanded', String(!isOpen));
    navButton.setAttribute('aria-label', isOpen ? 'メニューを開く' : 'メニューを閉じる');
    siteNav.classList.toggle('is-open', !isOpen);
  });
}

const disclosureGroups = [...document.querySelectorAll('.year-group, .topic-group')];

const openYearFromHash = () => {
  if (!window.location.hash) return;
  const target = document.querySelector(window.location.hash);
  if (!(target instanceof HTMLDetailsElement)) return;
  disclosureGroups.forEach((group) => {
    group.open = group === target;
  });
};

openYearFromHash();

disclosureGroups.forEach((group) => {
  group.addEventListener('toggle', () => {
    if (!group.open) return;
    disclosureGroups.forEach((otherGroup) => {
      if (otherGroup !== group) otherGroup.open = false;
    });
  });
});

window.addEventListener('hashchange', openYearFromHash);

const visitorCounter = (() => {
  const namespace = 'kaigow-diary-mori-20260714-7f3c9a';
  const endpoint = `https://api.counterapi.dev/v1/${namespace}`;
  const isPublicSite = window.location.hostname === 'kazutumu.github.io';

  const japanDateKey = (date = new Date()) => {
    const parts = new Intl.DateTimeFormat('en', {
      timeZone: 'Asia/Tokyo',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).formatToParts(date);
    const value = (type) => parts.find((part) => part.type === type)?.value;
    return `${value('year')}-${value('month')}-${value('day')}`;
  };

  const request = async (name, action = '') => {
    const suffix = action ? `/${action}` : '/';
    const response = await fetch(`${endpoint}/${name}${suffix}`, {
      cache: 'no-store',
      referrerPolicy: 'no-referrer'
    });
    if (!response.ok) {
      if (!action && response.status === 400) return 0;
      throw new Error(`Counter request failed: ${response.status}`);
    }
    const data = await response.json();
    return Number(data.count ?? data.value ?? data.data?.up_count ?? 0);
  };

  const storageValue = (key) => {
    try {
      return window.localStorage.getItem(key);
    } catch (_) {
      return window.sessionStorage.getItem(key);
    }
  };

  const saveStorageValue = (key, value) => {
    try {
      window.localStorage.setItem(key, value);
    } catch (_) {
      window.sessionStorage.setItem(key, value);
    }
  };

  const countVisit = async () => {
    if (!isPublicSite) return;
    const today = japanDateKey();
    const counters = [
      { name: 'total', storageKey: 'mori-visitor-total-counted' },
      { name: `day-${today}`, storageKey: 'mori-visitor-day-counted' }
    ];

    await Promise.all(counters.map(async ({ name, storageKey }) => {
      if (storageValue(storageKey) === today) return;
      await request(name, 'up');
      saveStorageValue(storageKey, today);
    }));
  };

  const showDashboard = async () => {
    const dashboard = document.querySelector('[data-visitor-dashboard]');
    if (!dashboard) return;

    const today = japanDateKey();
    const yesterday = japanDateKey(new Date(Date.now() - 86400000));
    const fields = {
      today: `day-${today}`,
      yesterday: `day-${yesterday}`,
      total: 'total'
    };

    try {
      const entries = await Promise.all(Object.entries(fields).map(async ([key, name]) => {
        const value = await request(name);
        return [key, value];
      }));
      entries.forEach(([key, value]) => {
        const output = dashboard.querySelector(`[data-visitor-count="${key}"]`);
        if (output) output.textContent = value.toLocaleString('ja-JP');
      });
      dashboard.dataset.state = 'ready';
    } catch (_) {
      dashboard.dataset.state = 'error';
      const status = dashboard.querySelector('[data-visitor-status]');
      if (status) status.textContent = '霧が濃く、ただいま観測できません。';
    }
  };

  return { countVisit, showDashboard };
})();

visitorCounter.countVisit().finally(visitorCounter.showDashboard);
