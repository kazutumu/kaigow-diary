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
