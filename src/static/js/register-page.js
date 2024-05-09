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
    let object = {};
    formData.forEach((value, key) => object[key] = value);
    try {
        const response = await fetch(`/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(object),
        });
        if (response.ok)
            window.location.replace("/pipelines");
        if (!response.ok)
            $('#validation-error-msg').show();
        console.log(await response.json());
    } catch (e) {
    }
}

const form = document.querySelector("#login");

form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendData();
});
