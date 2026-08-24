console.log("FORGOT RESET PASSWORD JS LOADED");
document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("resetPasswordForm");
    const newPassword = document.getElementById("new_password");
    const confirmPassword = document.getElementById("confirm_password");
    const resetButton = document.getElementById("resetPasswordBtn");
    const messageBox = document.getElementById("resetPasswordMessage");

    const toggleButtons = document.querySelectorAll(
        ".reset-password-toggle"
    );


    /* =====================================================
       CHECK ELEMENTS
    ===================================================== */

    if (
        !form ||
        !newPassword ||
        !confirmPassword ||
        !resetButton ||
        !messageBox
    ) {
        console.error("Reset password elements not found.");
        return;
    }


    /* =====================================================
       GET RESET TOKEN
    ===================================================== */

    const resetToken = sessionStorage.getItem(
        "password_reset_token"
    );


    console.log("Reset token:", resetToken);


    if (!resetToken) {

        showMessage(
            "Password reset session expired. Please request a new OTP.",
            "error"
        );

        resetButton.disabled = true;

        return;
    }


    /* =====================================================
       PASSWORD SHOW / HIDE
    ===================================================== */

    toggleButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId =
                button.getAttribute("data-target");

            const input =
                document.getElementById(targetId);

            const icon =
                button.querySelector("i");


            if (!input || !icon) {
                return;
            }


            if (input.type === "password") {

                input.type = "text";

                icon.classList.remove("fa-eye");

                icon.classList.add("fa-eye-slash");

                button.setAttribute(
                    "aria-label",
                    "Hide password"
                );

            } else {

                input.type = "password";

                icon.classList.remove("fa-eye-slash");

                icon.classList.add("fa-eye");

                button.setAttribute(
                    "aria-label",
                    "Show password"
                );

            }

        });

    });


    /* =====================================================
       RESET PASSWORD
    ===================================================== */

    form.addEventListener("submit", async function (event) {

        event.preventDefault();


        const password =
            newPassword.value.trim();

        const confirmPasswordValue =
            confirmPassword.value.trim();


        /* =================================================
           VALIDATION
        ================================================= */

        if (!password) {

            showMessage(
                "Please enter a new password.",
                "error"
            );

            return;
        }


        if (password.length < 8) {

            showMessage(
                "Password must be at least 8 characters.",
                "error"
            );

            return;
        }


        if (!confirmPasswordValue) {

            showMessage(
                "Please confirm your new password.",
                "error"
            );

            return;
        }


        if (password !== confirmPasswordValue) {

            showMessage(
                "Passwords do not match.",
                "error"
            );

            return;
        }


        /* =================================================
           DISABLE BUTTON
        ================================================= */

        resetButton.disabled = true;

        resetButton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Resetting...';

        clearMessage();


        /* =================================================
           API REQUEST
        ================================================= */

        try {

            const requestBody = {

                reset_token: resetToken,

                password: password,

                confirm_password: confirmPasswordValue

            };


            console.log(
                "Reset password request:",
                {
                    reset_token: resetToken ? "TOKEN PRESENT" : "TOKEN MISSING",
                    password: "********",
                    confirm_password: "********"
                }
            );


            const response = await fetch(
                "/api/accounts/reset-password/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },

                    body: JSON.stringify(requestBody)
                }
            );


            /* =================================================
               READ RESPONSE SAFELY
            ================================================= */

            let data = {};

            try {

                data = await response.json();

            } catch (jsonError) {

                console.error(
                    "Could not read API response:",
                    jsonError
                );

            }


            console.log(
                "Reset password API status:",
                response.status
            );

            console.log(
                "Reset password API response:",
                data
            );


            /* =================================================
               API ERROR
            ================================================= */

            if (!response.ok) {

                throw new Error(
                    getErrorMessage(data)
                );
            }


            /* =================================================
               SUCCESS
            ================================================= */

            showMessage(
                data.message ||
                "Password reset successfully.",
                "success"
            );


            /*
             * Disable form after successful reset.
             */

            newPassword.disabled = true;

            confirmPassword.disabled = true;

            resetButton.disabled = true;


            /*
             * Remove reset session.
             */

            sessionStorage.removeItem(
                "password_reset_token"
            );

            sessionStorage.removeItem(
                "password_reset_email"
            );


            /*
             * Redirect to login.
             */

            setTimeout(function () {

                window.location.href =
                    "/login/";

            }, 1500);


        } catch (error) {

            console.error(
                "Reset password error:",
                error
            );


            showMessage(
                error.message ||
                "Unable to reset password.",
                "error"
            );


            /*
             * Enable button again.
             */

            resetButton.disabled = false;

            resetButton.innerHTML =
                '<i class="fa-solid fa-key"></i> Reset Password';

        }

    });


    /* =====================================================
       SHOW MESSAGE
    ===================================================== */

    function showMessage(message, type) {

        messageBox.textContent = message;

        messageBox.className = "";

        messageBox.classList.add(type);

        messageBox.style.display = "block";

    }


    /* =====================================================
       CLEAR MESSAGE
    ===================================================== */

    function clearMessage() {

        messageBox.textContent = "";

        messageBox.className = "";

        messageBox.style.display = "none";

    }

});


/* =========================================================
   API ERROR HANDLER
========================================================= */

function getErrorMessage(data) {

    if (!data) {

        return "Something went wrong.";

    }


    if (typeof data.detail === "string") {

        return data.detail;

    }


    if (typeof data.message === "string") {

        return data.message;

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