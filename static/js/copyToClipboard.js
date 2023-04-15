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
