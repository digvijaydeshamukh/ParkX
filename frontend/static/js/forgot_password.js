
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".forgot-password-form");
    const emailInput = document.getElementById("email");
    const button = document.querySelector(".forgot-send-btn");

    if (!form || !emailInput || !button) {
        return;
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = emailInput.value.trim();

        if (!email) {
            alert("Please enter your email address.");
            return;
        }

        button.disabled = true;
        button.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';

        try {
            const response = await fetch(
                "/api/accounts/forgot-password/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: email
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(getErrorMessage(data));
            }

            sessionStorage.setItem(
                "password_reset_email",
                email
            );

            alert(
                data.message ||
                "If an account exists with this email, a password reset OTP has been sent."
            );

            window.location.href = "/verify-otp/";

        } catch (error) {
            console.error(error);

            alert(
                error.message ||
                "Something went wrong. Please try again."
            );

            button.disabled = false;

            button.innerHTML =
                '<i class="fa-solid fa-paper-plane"></i> Send OTP';
        }
    });
});


function getErrorMessage(data) {
    if (!data) {
        return "Something went wrong.";
    }

    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data.non_field_errors)) {
        return data.non_field_errors.join(" ");
    }

    for (const key in data) {
        if (Array.isArray(data[key])) {
            return data[key].join(" ");
        }

        if (typeof data[key] === "string") {
            return data[key];
        }
    }

    return "Something went wrong.";
}

