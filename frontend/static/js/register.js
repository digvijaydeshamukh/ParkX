const registerForm = document.getElementById("registerForm");
const sendOtpBtn = document.getElementById("sendOtpBtn");

const otpSection = document.getElementById("otpSection");
const verifyOtpBtn = document.getElementById("verifyOtpBtn");


// ===============================
// SEND OTP
// ===============================

registerForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    clearErrors();

    const password = document.getElementById("password").value;
    const confirmPassword =
        document.getElementById("confirm_password").value;

    // Frontend password confirmation
    if (password !== confirmPassword) {

        showError(
            "confirm_password",
            "Passwords do not match."
        );

        return;
    }

    const data = {
        first_name: document.getElementById("first_name").value.trim(),
        last_name: document.getElementById("last_name").value.trim(),
        email: document.getElementById("email").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        password: password,
        confirm_password: confirmPassword
    };

    try {

        sendOtpBtn.disabled = true;
        sendOtpBtn.textContent = "Sending OTP...";

        const response = await fetch(
            "/api/accounts/register/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );

        const result = await response.json();

        if (!response.ok) {

            displayErrors(result);

            sendOtpBtn.disabled = false;
            sendOtpBtn.textContent = "Send OTP";

            return;
        }

        // OTP successfully sent
        alert(result.message);

        otpSection.style.display = "block";

        sendOtpBtn.textContent = "OTP Sent";
        sendOtpBtn.disabled = true;

        // Prevent changing registration details
        disableRegistrationFields();

    } catch (error) {

        console.error("Registration error:", error);

        alert(
            "Unable to connect to the server. Please try again."
        );

        sendOtpBtn.disabled = false;
        sendOtpBtn.textContent = "Send OTP";
    }
});


// ===============================
// VERIFY OTP
// ===============================

verifyOtpBtn.addEventListener("click", async function () {

    clearErrors();

    const email =
        document.getElementById("email").value.trim();

    const otp =
        document.getElementById("otp").value.trim();

    if (!otp) {

        showError(
            "otp",
            "Please enter the OTP."
        );

        return;
    }

    const data = {
        email: email,
        otp: otp
    };

    try {

        verifyOtpBtn.disabled = true;
        verifyOtpBtn.textContent = "Verifying...";

        const response = await fetch(
            "/api/accounts/verify-otp/",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );

        const result = await response.json();

        if (!response.ok) {

            displayErrors(result);

            verifyOtpBtn.disabled = false;
            verifyOtpBtn.textContent = "Verify & Register";

            return;
        }

        alert(result.message);

        // Later we can redirect to login
        // window.location.href = "/login/";

    } catch (error) {

        console.error("OTP verification error:", error);

        alert(
            "Unable to connect to the server. Please try again."
        );

        verifyOtpBtn.disabled = false;
        verifyOtpBtn.textContent = "Verify & Register";
    }
});


// ===============================
// DISPLAY API ERRORS
// ===============================

function displayErrors(errors) {

    for (const field in errors) {

        if (Array.isArray(errors[field])) {

            showError(
                field,
                errors[field][0]
            );

        } else {

            showError(
                field,
                errors[field]
            );
        }
    }
}


// ===============================
// SHOW FIELD ERROR
// ===============================

function showError(field, message) {

    const errorElement =
        document.getElementById(`${field}_error`);

    if (errorElement) {
        errorElement.textContent = message;
    }
}


// ===============================
// CLEAR ERRORS
// ===============================

function clearErrors() {

    const errors =
        document.querySelectorAll(".error");

    errors.forEach(function (error) {
        error.textContent = "";
    });
}


// ===============================
// DISABLE REGISTRATION FIELDS
// ===============================

function disableRegistrationFields() {

    const fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "password",
        "confirm_password"
    ];

    fields.forEach(function (field) {

        document.getElementById(field).disabled = true;

    });
}