(() => {
  const input = document.getElementById("search-input");
  const box = document.getElementById("search-suggest");
  if (!input || !box) return;
  let timer = null;
  let controller = null;
  const hide = () => { box.style.display = "none"; box.innerHTML = ""; };
  const render = (items) => {
    if (!items.length) return hide();
    box.innerHTML = items.map(i =>
      `<a href="${i.url}" class="list-group-item list-group-item-action">${i.title}</a>`
    ).join("");
    box.style.display = "block";
  };
  input.addEventListener("input", () => {
    const q = input.value.trim();
    clearTimeout(timer);
    if (q.length < 2) return hide();
    timer = setTimeout(async () => {
      if (controller) controller.abort();
      controller = new AbortController();
      try {
        const res = await fetch(`/api/search/suggest/?q=${encodeURIComponent(q)}`, {
          signal: controller.signal,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!res.ok) return hide();
        const data = await res.json();
        render(data.items || []);
      } catch (e) {
        if (e.name !== "AbortError") hide();
      }
    }, 350);
  });
  document.addEventListener("click", (e) => {
    if (!box.contains(e.target) && e.target !== input) hide();
  });
})();