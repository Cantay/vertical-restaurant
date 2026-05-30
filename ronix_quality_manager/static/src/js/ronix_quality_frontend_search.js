/** @odoo-module **/

const initSearch = () => {
    document.querySelectorAll("[data-ham-search-input]").forEach((input) => {
        const key = input.dataset.hamSearchInput;
        const items = [...document.querySelectorAll(`[data-ham-search-item="${key}"]`)];
        input.addEventListener("input", () => {
            const needle = input.value.trim().toLocaleLowerCase("tr-TR");
            items.forEach((item) => {
                const text = item.textContent.toLocaleLowerCase("tr-TR");
                item.hidden = Boolean(needle && !text.includes(needle));
            });
        });
    });
};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSearch);
} else {
    initSearch();
}
