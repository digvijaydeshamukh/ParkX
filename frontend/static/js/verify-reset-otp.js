document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".verify-otp-form");
    const inputs = document.querySelectorAll(".otp-input");
    const fullOtp = document.getElementById("fullOtp");
    const verifyButton = document.querySelector(".verify-otp-btn");

    const resendButton = document.getElementById("resendOtpBtn");
    const resendMessage = document.getElementById("resendMessage");

    const emailElement =
        document.querySelector(".verify-email span");


    if (
        !form ||
        inputs.length !== 6 ||
        !fullOtp ||
        !verifyButton
    ) {
        return;
    }


    // Get email saved during forgot-password step.
    const email = sessionStorage.getItem(
        "password_reset_email"
    );


    if (!email) {

        alert(
            "Password reset session not found. Please request a new OTP."
        );

        window.location.href = "/forgot-password/";

        return;
    }


    // Display email on OTP page.
    if (emailElement) {
        emailElement.textContent = email;
    }


    /*
     * OTP INPUT HANDLING
     */

    inputs.forEach(function (input, index) {

        input.addEventListener("input", function () {

            input.value = input.value.replace(/\D/g, "");

            if (
                input.value &&
                index < inputs.length - 1
            ) {
                inputs[index + 1].focus();
            }

            updateOtp();
        });


        input.addEventListener("keydown", function (event) {

            if (
                event.key === "Backspace" &&
                input.value === "" &&
                index > 0
            ) {
                inputs[index - 1].focus();
            }

        });

    });


    function updateOtp() {

        let otp = "";

        inputs.forEach(function (input) {
            otp += input.value;
        });

        fullOtp.value = otp;
    }


    /*
     * VERIFY OTP
     */

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        updateOtp();

        const otp = fullOtp.value.trim();


        if (otp.length !== 6) {

            alert(
                "Please enter the complete 6-digit OTP."
            );

            return;
        }


        verifyButton.disabled = true;

        verifyButton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Verifying...';


        try {

            const response = await fetch(
                "/api/accounts/verify-reset-otp/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        otp: otp
                    })
                }
            );


            const data = await response.json();


            if (!response.ok) {
                throw new Error(
                    getErrorMessage(data)
                );
            }


            if (!data.reset_token) {

                throw new Error(
                    "Reset token was not received."
                );
            }


            sessionStorage.setItem(
                "password_reset_token",
                data.reset_token
            );


            window.location.href =
                "/forgot-reset/";


        } catch (error) {

            console.error(error);

            alert(
                error.message ||
                "Invalid or expired OTP."
            );


            verifyButton.disabled = false;

            verifyButton.innerHTML =
                '<i class="fa-solid fa-circle-check"></i> Verify OTP';
        }

    });


    /*
     * RESEND OTP
     */

    if (resendButton) {

        resendButton.addEventListener(
            "click",
            async function () {

                if (resendButton.disabled) {
                    return;
                }


                resendButton.disabled = true;

                resendButton.textContent =
                    "Sending...";


                if (resendMessage) {
                    resendMessage.textContent = "";
                }


                try {

                    const response = await fetch(
                        "/api/accounts/resend-reset-otp/",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                email: email
                            })
                        }
                    );


                    const data =
                        await response.json();


                    /*
                     * 429 means cooldown is active.
                     */

                    if (response.status === 429) {

                        const retryAfter =
                            Number(
                                data.retry_after
                            ) || 60;


                        startResendCooldown(
                            retryAfter
                        );

                        if (resendMessage) {

                            resendMessage.textContent =
                                data.detail ||
                                "Please wait before requesting another OTP.";
                        }

                        return;
                    }


                    if (!response.ok) {

                        throw new Error(
                            getErrorMessage(data)
                        );
                    }


                    /*
                     * Successful resend
                     */

                    if (resendMessage) {

                        resendMessage.textContent =
                            data.message ||
                            "A new OTP has been sent.";
                    }


                    /*
                     * Start 60-second cooldown.
                     */

                    startResendCooldown(60);


                    /*
                     * Clear old OTP inputs.
                     */

                    inputs.forEach(function (input) {
                        input.value = "";
                    });

                    fullOtp.value = "";


                    inputs[0].focus();


                } catch (error) {

                    console.error(error);


                    if (resendMessage) {

                        resendMessage.textContent =
                            error.message ||
                            "Unable to resend OTP.";
                    }


                    resendButton.disabled = false;

                    resendButton.textContent =
                        "Resend OTP";
                }

            }
        );

    }


    /*
     * RESEND COUNTDOWN
     */

    function startResendCooldown(seconds) {

        let remaining = seconds;

        resendButton.disabled = true;

        resendButton.textContent =
            "Resend OTP (" + remaining + "s)";


        const interval =
            setInterval(function () {

                remaining--;


                if (remaining <= 0) {

                    clearInterval(interval);

                    resendButton.disabled = false;

                    resendButton.textContent =
                        "Resend OTP";

                    return;
                }


                resendButton.textContent =
                    "Resend OTP (" +
                    remaining +
                    "s)";

            }, 1000);

    }

});


/*
 * API ERROR HANDLER
 */

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