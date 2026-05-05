document.addEventListener("DOMContentLoaded", () => {
  const widgets = document.querySelectorAll("[data-product-id]");
  widgets.forEach((widget) => {
    widget.setAttribute("data-enhanced", "true");
  });
});
