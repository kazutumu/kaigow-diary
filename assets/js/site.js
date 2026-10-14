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

// The retired CounterAPI v1 counter is no longer called. GA4 uses consent-based pageviews.
const oldDashboard = document.querySelector('[data-visitor-dashboard]');
if (oldDashboard) {
  oldDashboard.dataset.state = 'error';
  oldDashboard.querySelectorAll('[data-visitor-count]').forEach((el) => { el.textContent = '未計測'; });
  const status = oldDashboard.querySelector('[data-visitor-status]');
  if (status) status.textContent = '旧カウンターは終了しました。現在のアクセス解析は、許可された閲覧から集計しています。';
}
