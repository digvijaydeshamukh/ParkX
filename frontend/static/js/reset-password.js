
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".reset-password-form");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput =
        document.getElementById("confirm_password");
    const button = document.querySelector(".reset-password-btn");


    if (
        !form ||
        !passwordInput ||
        !confirmPasswordInput ||
        !button
    ) {
        return;
    }


    const resetToken = sessionStorage.getItem(
        "password_reset_token"
    );


    if (!resetToken) {
        alert(
            "Password reset session expired. Please request a new OTP."
        );

        window.location.href = "/forgot-password/";
        return;
    }


    form.addEventListener("submit", async function (event) {
        event.preventDefault();


        const password = passwordInput.value;
        const confirmPassword =
            confirmPasswordInput.value;


        if (!password) {
            alert("Please enter a password.");
            return;
        }


        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }


        button.disabled = true;

        button.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Resetting...';


        try {
            const response = await fetch(
                "/api/accounts/reset-password/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        reset_token: resetToken,
                        password: password,
                        confirm_password: confirmPassword
                    })
                }
            );


            const data = await response.json();


            if (!response.ok) {
                throw new Error(getErrorMessage(data));
            }


            // Remove used reset credentials
            sessionStorage.removeItem(
                "password_reset_token"
            );

            sessionStorage.removeItem(
                "password_reset_email"
            );


            alert(
                data.message ||
                "Password reset successfully."
            );


            window.location.href = "/login/";


        } catch (error) {
            console.error(error);

            alert(
                error.message ||
                "Unable to reset password."
            );


            button.disabled = false;

            button.innerHTML =
                '<i class="fa-solid fa-key"></i> Reset Password';
        }
    });
});


function getErrorMessage(data) {
    if (!data) {
        return "Unable to reset password.";
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

    return "Unable to reset password.";
}

