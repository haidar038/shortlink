function copyToClipboard() {
    // Select the shortened URL field
    var shortenedUrlField = document.getElementById("shortened-url");
    shortenedUrlField.select();

    // Copy the selected text to the clipboard
    document.execCommand("copy");

    // Show a toast message indicating the URL has been copied
    var toast = document.getElementById("copy-toast");
    toast.classList.add("show");
    setTimeout(function () {
        toast.classList.remove("show");
    }, 3000);
}

function onScroll(evt) {
    // Store the scroll value for laterz.
    lastScrollY = window.scrollY;

    // Prevent multiple rAF callbacks.
    if (scheduledAnimationFrame) return;

    scheduledAnimationFrame = true;
    requestAnimationFrame(readAndUpdatePage);
}

window.addEventListener("scroll", onScroll);

// Tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
