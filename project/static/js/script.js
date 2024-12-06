function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function () {
        const previewContainer = document.getElementById('preview-container');
        previewContainer.innerHTML = `
            <div class="preview-photo-container">
                <p>Preview:</p>
                <img src="${reader.result}">
            </div>
        `;
    };
    reader.readAsDataURL(event.target.files[0]);
}


function clearError() {
    document.getElementById("error").innerText = "";
}
