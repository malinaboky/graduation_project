$('.open-eye-btn').on('click', function () {
    $(this).toggleClass('close-eye-btn');
    let x = document.getElementById("password");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
})

async function sendData() {
    let formData = new FormData(form)
    try {
        const response = await fetch(`/auth/login`, {
            method: "POST",
            body: formData,
        });
        if (response.ok)
            window.location.replace("/pipelines");
        else
            $('#validation-error-msg').show();
    } catch (e) {
    }
}

const form = document.querySelector("#login");

form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendData();
});
