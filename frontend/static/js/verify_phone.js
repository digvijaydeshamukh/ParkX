document.addEventListener("DOMContentLoaded", () => {

    console.log("=================================");
    console.log("VERIFY PHONE JS LOADED");
    console.log("=================================");


    // =====================================================
    // ELEMENTS
    // =====================================================

    const verifyPhoneForm =
        document.getElementById("verifyPhoneForm");

    const otpInput =
        document.getElementById("otp");

    const verifyOtpBtn =
        document.getElementById("verifyOtpBtn");

    const resendOtpBtn =
        document.getElementById("resendOtpBtn");

    const message =
        document.getElementById("verifyPhoneMessage");


    console.log("Form:", verifyPhoneForm);
    console.log("OTP input:", otpInput);
    console.log("Verify button:", verifyOtpBtn);
    console.log("Resend button:", resendOtpBtn);
    console.log("Message:", message);


    // =====================================================
    // ACCESS TOKEN
    // =====================================================

    function getAccessToken() {

        return localStorage.getItem("access_token");

    }


    // =====================================================
    // SHOW MESSAGE
    // =====================================================

    function showMessage(text, type = "error") {

        if (!message) {
            console.log(text);
            return;
        }

        message.textContent = text;

        message.className =
            `verify-phone-message ${type}`;

    }


    // =====================================================
    // SEND OTP
    // =====================================================

    async function sendOTP() {

        console.log(
            "Sending phone verification OTP..."
        );


        const accessToken =
            getAccessToken();


        if (!accessToken) {

            console.error(
                "Access token not found."
            );

            window.location.href =
                "/login/";

            return;

        }


        try {

            const response =
                await fetch(
                    "/api/accounts/phone/send-otp/",
                    {
                        method: "POST",

                        headers: {
                            "Authorization":
                                `Bearer ${accessToken}`,

                            "Content-Type":
                                "application/json"
                        }
                    }
                );


            console.log(
                "Send OTP status:",
                response.status
            );


            const data =
                await response.json();


            console.log(
                "Send OTP response:",
                data
            );


            if (!response.ok) {

                console.error(
                    "Send OTP API error:",
                    data
                );


                showMessage(
                    data.detail ||
                    data.message ||
                    "Unable to send OTP.",
                    "error"
                );

                return;

            }


            console.log(
                "OTP sent successfully."
            );


            showMessage(
                "OTP sent to your phone number.",
                "success"
            );


            // Automatically focus OTP field

            if (otpInput) {

                otpInput.focus();

            }


        } catch (error) {

            console.error(
                "Send OTP error:",
                error
            );


            showMessage(
                "Something went wrong while sending OTP.",
                "error"
            );

        }

    }


    // =====================================================
    // VERIFY OTP
    // =====================================================

    async function verifyOTP() {

        console.log(
            "Verifying OTP..."
        );


        const otp =
            otpInput
                ? otpInput.value.trim()
                : "";


        // =================================================
        // VALIDATE OTP
        // =================================================

        if (!otp) {

            showMessage(
                "Please enter the OTP.",
                "error"
            );

            return;

        }


        if (!/^\d{6}$/.test(otp)) {

            showMessage(
                "Please enter a valid 6-digit OTP.",
                "error"
            );

            return;

        }


        const accessToken =
            getAccessToken();


        if (!accessToken) {

            console.error(
                "Access token not found."
            );

            window.location.href =
                "/login/";

            return;

        }


        // =================================================
        // DISABLE BUTTON
        // =================================================

        if (verifyOtpBtn) {

            verifyOtpBtn.disabled =
                true;

            verifyOtpBtn.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Verifying...';

        }


        try {

            const response =
                await fetch(
                    "/api/accounts/phone/verify-otp/",
                    {
                        method: "POST",

                        headers: {
                            "Authorization":
                                `Bearer ${accessToken}`,

                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            otp: otp
                        })
                    }
                );


            console.log(
                "Verify OTP status:",
                response.status
            );


            const data =
                await response.json();


            console.log(
                "Verify OTP response:",
                data
            );


            // =================================================
            // VERIFY FAILED
            // =================================================

            if (!response.ok) {

                console.error(
                    "Verify OTP failed:",
                    data
                );


                showMessage(
                    data.detail ||
                    data.message ||
                    "Invalid or expired OTP.",
                    "error"
                );


                if (verifyOtpBtn) {

                    verifyOtpBtn.disabled =
                        false;

                    verifyOtpBtn.innerHTML =
                        '<i class="fa-solid fa-circle-check"></i> Verify OTP';

                }

                return;

            }


            // =================================================
            // SUCCESS
            // =================================================

            console.log(
                "Phone verified successfully!"
            );


            showMessage(
                "Phone number verified successfully!",
                "success"
            );


            // Redirect to profile

            setTimeout(() => {

                window.location.href =
                    "/profile/";

            }, 800);


        } catch (error) {

            console.error(
                "Verify OTP error:",
                error
            );


            showMessage(
                "Something went wrong while verifying OTP.",
                "error"
            );


            if (verifyOtpBtn) {

                verifyOtpBtn.disabled =
                    false;

                verifyOtpBtn.innerHTML =
                    '<i class="fa-solid fa-circle-check"></i> Verify OTP';

            }

        }

    }


    // =====================================================
    // RESEND OTP
    // =====================================================

    async function resendOTP() {

        console.log(
            "Resending OTP..."
        );


        const accessToken =
            getAccessToken();


        if (!accessToken) {

            console.error(
                "Access token not found."
            );

            window.location.href =
                "/login/";

            return;

        }


        if (resendOtpBtn) {

            resendOtpBtn.disabled =
                true;

            resendOtpBtn.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';

        }


        try {

            const response =
                await fetch(
                    "/api/accounts/phone/resend-otp/",
                    {
                        method: "POST",

                        headers: {
                            "Authorization":
                                `Bearer ${accessToken}`,

                            "Content-Type":
                                "application/json"
                        }
                    }
                );


            console.log(
                "Resend OTP status:",
                response.status
            );


            const data =
                await response.json();


            console.log(
                "Resend OTP response:",
                data
            );


            if (!response.ok) {

                console.error(
                    "Resend OTP failed:",
                    data
                );


                showMessage(
                    data.detail ||
                    data.message ||
                    "Unable to resend OTP.",
                    "error"
                );


                return;

            }


            console.log(
                "OTP resent successfully."
            );


            showMessage(
                "A new OTP has been sent to your phone.",
                "success"
            );


            if (otpInput) {

                otpInput.value = "";

                otpInput.focus();

            }


        } catch (error) {

            console.error(
                "Resend OTP error:",
                error
            );


            showMessage(
                "Something went wrong while resending OTP.",
                "error"
            );


        } finally {

            if (resendOtpBtn) {

                resendOtpBtn.disabled =
                    false;

                resendOtpBtn.innerHTML =
                    '<i class="fa-solid fa-rotate"></i> Resend OTP';

            }

        }

    }


    // =====================================================
    // FORM SUBMIT
    // =====================================================

    if (verifyPhoneForm) {

        verifyPhoneForm.addEventListener(
            "submit",
            (event) => {

                event.preventDefault();

                verifyOTP();

            }
        );

    }


    // =====================================================
    // RESEND BUTTON
    // =====================================================

    if (resendOtpBtn) {

        resendOtpBtn.addEventListener(
            "click",
            resendOTP
        );

    }


    // =====================================================
    // OTP INPUT - ONLY NUMBERS
    // =====================================================

    if (otpInput) {

        otpInput.addEventListener(
            "input",
            () => {

                otpInput.value =
                    otpInput.value
                        .replace(/\D/g, "")
                        .slice(0, 6);

            }
        );

    }


    // =====================================================
    // AUTOMATICALLY SEND OTP
    // =====================================================

    sendOTP();

});