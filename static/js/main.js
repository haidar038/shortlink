function copyToClipboard() {
    document.getElementById("shortened-url").select(), document.execCommand("copy");
    var o = document.getElementById("copy-toast");
    o.classList.add("show"),
        setTimeout(function () {
            o.classList.remove("show");
        }, 3e3);
}
function onScroll(o) {
    (lastScrollY = window.scrollY), scheduledAnimationFrame || ((scheduledAnimationFrame = !0), requestAnimationFrame(readAndUpdatePage));
}
window.addEventListener("scroll", onScroll);
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]'),
    tooltipList = [...tooltipTriggerList].map((o) => new bootstrap.Tooltip(o));