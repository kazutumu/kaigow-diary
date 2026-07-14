const input = document.querySelector('#search-input');
const clearButton = document.querySelector('#search-clear');
const status = document.querySelector('#search-status');
const results = document.querySelector('#search-results');
const dataElement = document.querySelector('#search-data');

if (input && clearButton && status && results && dataElement) {
  const posts = JSON.parse(dataElement.textContent);

  const escapeHtml = (value) => value.replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));

  const render = () => {
    const query = input.value.trim().toLocaleLowerCase('ja');
    clearButton.classList.toggle('is-visible', query.length > 0);

    if (!query) {
      status.textContent = '検索語を入力してください。';
      results.innerHTML = '';
      return;
    }

    const matches = posts.filter((post) =>
      `${post.title} ${post.categories} ${post.text}`.toLocaleLowerCase('ja').includes(query)
    );

    const visibleMatches = matches.slice(0, 100);
    status.textContent = matches.length > 100
      ? `${matches.length}件の日記が見つかりました。新しいものから100件を表示します。`
      : `${matches.length}件の日記が見つかりました。`;
    results.innerHTML = visibleMatches.map((post) => `
      <article class="search-result">
        <p>${escapeHtml(post.date)}　${escapeHtml(post.categories)}</p>
        <h2><a href="${post.url}">${escapeHtml(post.title)}</a></h2>
      </article>
    `).join('');
  };

  input.addEventListener('input', render);
  clearButton.addEventListener('click', () => {
    input.value = '';
    input.focus();
    render();
  });
}
