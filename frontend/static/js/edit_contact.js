document.addEventListener("DOMContentLoaded", () => {

    console.log("EDIT CONTACT JS FILE LOADED");
    console.log("ParkX Edit Contact JS DOM LOADED");


    // =====================================================
    // API ENDPOINTS
    // =====================================================

    const API = {

        profile:
            "/api/accounts/profile/",

        contactChange:
            "/api/accounts/contact/change/",

        verifyContactOtp:
            "/api/accounts/contact/change/verify-otp/",

        resendContactOtp:
            "/api/accounts/contact/change/resend-otp/"

    };


    // =====================================================
    // ELEMENTS
    // =====================================================

    const oldEmail =
        document.getElementById("oldEmail");

    const newEmail =
        document.getElementById("newEmail");

    const sendEmailOtpBtn =
        document.getElementById("sendEmailOtpBtn");

    const emailOtpSection =
        document.getElementById("emailOtpSection");

    const emailOtp =
        document.getElementById("emailOtp");

    const verifyEmailOtpBtn =
        document.getElementById("verifyEmailOtpBtn");

    const resendEmailOtpBtn =
        document.getElementById("resendEmailOtpBtn");


    const oldPhone =
        document.getElementById("oldPhone");

    const newPhone =
        document.getElementById("newPhone");

    const sendMobileOtpBtn =
        document.getElementById("sendMobileOtpBtn");

    const mobileOtpSection =
        document.getElementById("mobileOtpSection");

    const mobileOtp =
        document.getElementById("mobileOtp");

    const verifyMobileOtpBtn =
        document.getElementById("verifyMobileOtpBtn");

    const resendMobileOtpBtn =
        document.getElementById("resendMobileOtpBtn");


    const contactMessage =
        document.getElementById("contactMessage");


    // =====================================================
    // DEBUG
    // =====================================================

    console.log("Old email:", oldEmail);
    console.log("New email:", newEmail);
    console.log("Send email OTP:", sendEmailOtpBtn);
    console.log("Email OTP:", emailOtp);
    console.log("Verify email OTP:", verifyEmailOtpBtn);
    console.log("Resend email OTP:", resendEmailOtpBtn);

    console.log("Old phone:", oldPhone);
    console.log("New phone:", newPhone);
    console.log("Send mobile OTP:", sendMobileOtpBtn);
    console.log("Mobile OTP:", mobileOtp);
    console.log("Verify mobile OTP:", verifyMobileOtpBtn);
    console.log("Resend mobile OTP:", resendMobileOtpBtn);


    // =====================================================
    // ACCESS TOKEN
    // =====================================================

    function getAccessToken() {

        return localStorage.getItem("access_token");

    }


    // =====================================================
    // SHOW MESSAGE
    // =====================================================

    function showMessage(message, type = "error") {

        if (!contactMessage) {
            return;
        }

        contactMessage.textContent = message;

        contactMessage.className =
            `contact-message ${type}`;

    }


    // =====================================================
    // CLEAR MESSAGE
    // =====================================================

    function clearMessage() {

        if (!contactMessage) {
            return;
        }

        contactMessage.textContent = "";

        contactMessage.className =
            "contact-message";

    }


    // =====================================================
    // API REQUEST
    // =====================================================

    async function apiRequest(
        url,
        method = "GET",
        body = null
    ) {

        const accessToken =
            getAccessToken();


        if (!accessToken) {

            showMessage(
                "Your session has expired. Please login again.",
                "error"
            );

            return null;

        }


        const options = {

            method: method,

            headers: {

                "Authorization":
                    `Bearer ${accessToken}`,

                "Accept":
                    "application/json"

            }

        };


        // =================================================
        // ADD JSON BODY ONLY FOR POST
        // =================================================

        if (
            method !== "GET" &&
            method !== "HEAD" &&
            body !== null
        ) {

            options.headers["Content-Type"] =
                "application/json";

            options.body =
                JSON.stringify(body);

        }


        try {

            console.log(
                "Sending API request:",
                method,
                url,
                body
            );


            const response =
                await fetch(
                    url,
                    options
                );


            const responseText =
                await response.text();


            let data = {};

            try {

                data =
                    responseText
                        ? JSON.parse(responseText)
                        : {};

            } catch {

                data = {
                    raw_response:
                        responseText
                };

            }


            console.log(
                "API RESPONSE:",
                url
            );

            console.log(
                "STATUS:",
                response.status
            );

            console.log(
                "DATA:",
                data
            );


            // =================================================
            // UNAUTHORIZED
            // =================================================

            if (response.status === 401) {

                localStorage.removeItem(
                    "access_token"
                );

                localStorage.removeItem(
                    "refresh_token"
                );

                localStorage.removeItem(
                    "user"
                );

                window.location.href =
                    "/login/";

                return null;

            }


            return {

                response: response,

                data: data

            };


        } catch (error) {

            console.error(
                "API REQUEST ERROR:",
                error
            );

            showMessage(
                "Unable to connect to the server.",
                "error"
            );

            return null;

        }

    }


    // =====================================================
    // LOAD PROFILE
    // =====================================================

    async function loadProfile() {

        console.log(
            "Loading current contact information..."
        );


        const result =
            await apiRequest(
                API.profile,
                "GET"
            );


        if (!result) {
            return;
        }


        const {
            response,
            data
        } = result;


        if (!response.ok) {

            console.error(
                "Profile API error:",
                data
            );

            showMessage(
                data.detail ||
                data.message ||
                data.error ||
                "Unable to load profile information."
            );

            return;

        }


        const userData =
            data.user || data;


        console.log(
            "Current user:",
            userData
        );


        if (oldEmail) {

            oldEmail.value =
                userData.email || "";

        }


        if (oldPhone) {

            oldPhone.value =
                userData.phone || "";

        }

    }


    // =====================================================
    // EMAIL VALIDATION
    // =====================================================

    function isValidEmail(email) {

        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            .test(email);

    }


    // =====================================================
    // PHONE VALIDATION
    // =====================================================

    function isValidPhone(phone) {

        const cleaned =
            phone.replace(/\D/g, "");

        return cleaned.length >= 10;

    }


    // =====================================================
    // SEND EMAIL OTP
    // =====================================================

    async function sendEmailOtp() {

        clearMessage();


        if (!newEmail) {
            return;
        }


        const email =
            newEmail.value.trim();


        if (!email) {

            showMessage(
                "Please enter your new email address."
            );

            newEmail.focus();

            return;

        }


        if (!isValidEmail(email)) {

            showMessage(
                "Please enter a valid email address."
            );

            newEmail.focus();

            return;

        }


        if (
            oldEmail &&
            email.toLowerCase() ===
            oldEmail.value
                .trim()
                .toLowerCase()
        ) {

            showMessage(
                "New email must be different from your old email."
            );

            return;

        }


        if (sendEmailOtpBtn) {

            sendEmailOtpBtn.disabled = true;

            sendEmailOtpBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Sending...
            `;

        }


        /*
         * IMPORTANT
         *
         * Common ContactChangeView API
         *
         * contact_type = email
         * new_contact = new email
         */

        const result =
            await apiRequest(
                API.contactChange,
                "POST",
                {
                    contact_type: "email",
                    new_contact: email
                }
            );


        if (sendEmailOtpBtn) {

            sendEmailOtpBtn.disabled = false;

            sendEmailOtpBtn.innerHTML = `
                <i class="fa-solid fa-paper-plane"></i>
                Send Email OTP
            `;

        }


        if (!result) {
            return;
        }


        const {
            response,
            data
        } = result;


        if (!response.ok) {

            console.error(
                "SEND EMAIL OTP FAILED:",
                data
            );

            showMessage(
                data.detail ||
                data.message ||
                data.error ||
                "Unable to send email OTP."
            );

            return;

        }


        showMessage(
            data.message ||
            "Email OTP sent successfully.",
            "success"
        );


        if (emailOtpSection) {

            emailOtpSection.style.display =
                "block";

        }


        if (emailOtp) {

            emailOtp.value = "";

            emailOtp.focus();

        }

    }


    // =====================================================
    // VERIFY EMAIL OTP
    // =====================================================

    async function verifyEmailOtp() {

        clearMessage();


        if (!newEmail || !emailOtp) {
            return;
        }


        const email =
            newEmail.value.trim();

        const otp =
            emailOtp.value.trim();


        if (!email) {

            showMessage(
                "Please enter your new email address."
            );

            return;

        }


        if (!otp) {

            showMessage(
                "Please enter the email OTP."
            );

            emailOtp.focus();

            return;

        }


        if (otp.length !== 6) {

            showMessage(
                "Please enter a valid 6-digit OTP."
            );

            emailOtp.focus();

            return;

        }


        if (verifyEmailOtpBtn) {

            verifyEmailOtpBtn.disabled = true;

            verifyEmailOtpBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Verifying...
            `;

        }


        /*
         * IMPORTANT
         *
         * Same verification endpoint for email/mobile.
         *
         * contact_type = email
         * new_contact = email
         * otp = entered OTP
         */

        const result =
            await apiRequest(
                API.verifyContactOtp,
                "POST",
                {
                    contact_type: "email",
                    new_contact: email,
                    otp: otp
                }
            );


        if (verifyEmailOtpBtn) {

            verifyEmailOtpBtn.disabled = false;

            verifyEmailOtpBtn.innerHTML = `
                <i class="fa-solid fa-circle-check"></i>
                Verify Email OTP
            `;

        }


        if (!result) {
            return;
        }


        const {
            response,
            data
        } = result;


        if (!response.ok) {

            console.error(
                "VERIFY EMAIL OTP FAILED:",
                data
            );

            showMessage(
                data.detail ||
                data.message ||
                data.error ||
                "Invalid email OTP."
            );

            return;

        }


        showMessage(
            data.message ||
            "Email updated successfully.",
            "success"
        );


        setTimeout(
            () => {

                window.location.href =
                    "/profile/";

            },
            1000
        );

    }


    // =====================================================
    // RESEND EMAIL OTP
    // =====================================================

    async function resendEmailOtp() {

        clearMessage();


        if (!newEmail) {
            return;
        }


        const email =
            newEmail.value.trim();


        if (!email) {

            showMessage(
                "Please enter your new email address."
            );

            return;

        }


        if (resendEmailOtpBtn) {

            resendEmailOtpBtn.disabled = true;

            resendEmailOtpBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Resending...
            `;

        }


        /*
         * IMPORTANT:
         *
         * Use the dedicated resend endpoint.
         */

        const result =
            await apiRequest(
                API.resendContactOtp,
                "POST",
                {
                    contact_type: "email",
                    new_contact: email
                }
            );


        if (resendEmailOtpBtn) {

            resendEmailOtpBtn.disabled = false;

            resendEmailOtpBtn.innerHTML = `
                <i class="fa-solid fa-rotate-right"></i>
                Resend Email OTP
            `;

        }


        if (!result) {
            return;
        }


        const {
            response,
            data
        } = result;


        if (!response.ok) {

            console.error(
                "RESEND EMAIL OTP FAILED:",
                data
            );

            showMessage(
                data.detail ||
                data.message ||
                data.error ||
                "Unable to resend email OTP."
            );

            return;

        }


        showMessage(
            data.message ||
            "Email OTP resent successfully.",
            "success"
        );


        if (emailOtp) {

            emailOtp.value = "";

            emailOtp.focus();

        }

    }


    // =====================================================
// SEND MOBILE OTP
// =====================================================

async function sendMobileOtp() {

    clearMessage();

    if (!newPhone) {
        console.error("New phone input not found.");
        return;
    }

    const phone = newPhone.value.trim();


    // =================================================
    // VALIDATE MOBILE NUMBER
    // =================================================

    if (!phone) {

        showMessage(
            "Please enter your new mobile number."
        );

        newPhone.focus();

        return;
    }


    if (!isValidPhone(phone)) {

        showMessage(
            "Please enter a valid mobile number."
        );

        newPhone.focus();

        return;
    }


    // =================================================
    // CHECK SAME MOBILE NUMBER
    // =================================================

    if (
        oldPhone &&
        phone === oldPhone.value.trim()
    ) {

        showMessage(
            "New mobile number must be different from your old number."
        );

        newPhone.focus();

        return;
    }


    // =================================================
    // DISABLE SEND BUTTON
    // =================================================

    if (sendMobileOtpBtn) {

        sendMobileOtpBtn.disabled = true;

        sendMobileOtpBtn.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Sending...
        `;
    }


    // =================================================
    // SEND MOBILE OTP
    // =================================================
const requestData = {
    contact_type: "phone",
    new_contact: phone
};

console.log("MOBILE OTP REQUEST DATA:", requestData);

const result = await apiRequest(
    API.contactChange,
    "POST",
    requestData
);

    // const result = await apiRequest(
    //     API.contactChange,
    //     "POST",
    //     {
    //         contact_type: "phone",
    //         new_contact: phone
    //     }
    // );


    // =================================================
    // RESTORE BUTTON
    // =================================================

    if (sendMobileOtpBtn) {

        sendMobileOtpBtn.disabled = false;

        sendMobileOtpBtn.innerHTML = `
            <i class="fa-solid fa-paper-plane"></i>
            Send Mobile OTP
        `;
    }


    // =================================================
    // REQUEST FAILED
    // =================================================

    if (!result) {
        return;
    }


    const {
        response,
        data
    } = result;


    if (!response.ok) {

        console.error(
            "SEND MOBILE OTP FAILED:",
            data
        );

        showMessage(
            data.detail ||
            data.message ||
            data.error ||
            "Unable to send mobile OTP."
        );

        return;
    }


    // =================================================
    // SUCCESS
    // =================================================

    showMessage(
        data.message ||
        "Mobile OTP sent successfully.",
        "success"
    );


    // =================================================
    // SHOW OTP SECTION
    // =================================================

    if (mobileOtpSection) {

        mobileOtpSection.style.display = "block";
    }


    // =================================================
    // CLEAR OTP
    // =================================================

    if (mobileOtp) {

        mobileOtp.value = "";

        mobileOtp.focus();
    }

}


// =====================================================
// VERIFY MOBILE OTP
// =====================================================

async function verifyMobileOtp() {

    clearMessage();


    if (!newPhone || !mobileOtp) {

        console.error(
            "Mobile input or OTP input not found."
        );

        return;
    }


    const phone =
        newPhone.value.trim();

    const otp =
        mobileOtp.value.trim();


    // =================================================
    // VALIDATE MOBILE
    // =================================================

    if (!phone) {

        showMessage(
            "Please enter your new mobile number."
        );

        newPhone.focus();

        return;
    }


    // =================================================
    // VALIDATE OTP
    // =================================================

    if (!otp) {

        showMessage(
            "Please enter the mobile OTP."
        );

        mobileOtp.focus();

        return;
    }


    if (otp.length !== 6) {

        showMessage(
            "Please enter a valid 6-digit OTP."
        );

        mobileOtp.focus();

        return;
    }


    // =================================================
    // DISABLE VERIFY BUTTON
    // =================================================

    if (verifyMobileOtpBtn) {

        verifyMobileOtpBtn.disabled = true;

        verifyMobileOtpBtn.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Verifying...
        `;
    }


    // =================================================
    // VERIFY MOBILE OTP
    // =================================================

    const result = await apiRequest(
        API.verifyContactOtp,
        "POST",
        {
            contact_type: "phone",
            new_contact: phone,
            otp: otp
        }
    );


    // =================================================
    // RESTORE BUTTON
    // =================================================

    if (verifyMobileOtpBtn) {

        verifyMobileOtpBtn.disabled = false;

        verifyMobileOtpBtn.innerHTML = `
            <i class="fa-solid fa-circle-check"></i>
            Verify Mobile OTP
        `;
    }


    // =================================================
    // REQUEST FAILED
    // =================================================

    if (!result) {
        return;
    }


    const {
        response,
        data
    } = result;


    if (!response.ok) {

        console.error(
            "VERIFY MOBILE OTP FAILED:",
            data
        );

        showMessage(
            data.detail ||
            data.message ||
            data.error ||
            "Invalid mobile OTP."
        );

        return;
    }


    // =================================================
    // SUCCESS
    // =================================================

    showMessage(
        data.message ||
        "Mobile number updated successfully.",
        "success"
    );


    // =================================================
    // REDIRECT TO PROFILE
    // =================================================

    setTimeout(
        () => {

            window.location.href =
                "/profile/";

        },
        1000
    );

}


// =====================================================
// RESEND MOBILE OTP
// =====================================================

async function resendMobileOtp() {

    clearMessage();


    if (!newPhone) {

        console.error(
            "New phone input not found."
        );

        return;
    }


    const phone =
        newPhone.value.trim();


    // =================================================
    // VALIDATE MOBILE
    // =================================================

    if (!phone) {

        showMessage(
            "Please enter your new mobile number."
        );

        newPhone.focus();

        return;
    }


    if (!isValidPhone(phone)) {

        showMessage(
            "Please enter a valid mobile number."
        );

        newPhone.focus();

        return;
    }


    // =================================================
    // DISABLE RESEND BUTTON
    // =================================================

    if (resendMobileOtpBtn) {

        resendMobileOtpBtn.disabled = true;

        resendMobileOtpBtn.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Resending...
        `;
    }


    // =================================================
    // RESEND MOBILE OTP
    // =================================================

    const result = await apiRequest(
        API.resendContactOtp,
        "POST",
        {
            contact_type: "phone",
            new_contact: phone
        }
    );


    // =================================================
    // RESTORE BUTTON
    // =================================================

    if (resendMobileOtpBtn) {

        resendMobileOtpBtn.disabled = false;

        resendMobileOtpBtn.innerHTML = `
            <i class="fa-solid fa-rotate-right"></i>
            Resend Mobile OTP
        `;
    }


    // =================================================
    // REQUEST FAILED
    // =================================================

    if (!result) {
        return;
    }


    const {
        response,
        data
    } = result;


    if (!response.ok) {

        console.error(
            "RESEND MOBILE OTP FAILED:",
            data
        );

        showMessage(
            data.detail ||
            data.message ||
            data.error ||
            "Unable to resend mobile OTP."
        );

        return;
    }


    // =================================================
    // SUCCESS
    // =================================================

    showMessage(
        data.message ||
        "Mobile OTP resent successfully.",
        "success"
    );


    // =================================================
    // CLEAR OTP
    // =================================================

    if (mobileOtp) {

        mobileOtp.value = "";

        mobileOtp.focus();
    }

}

    // =====================================================
    // EMAIL EVENTS
    // =====================================================

    if (sendEmailOtpBtn) {

        sendEmailOtpBtn.addEventListener(
            "click",
            sendEmailOtp
        );

    }


    if (verifyEmailOtpBtn) {

        verifyEmailOtpBtn.addEventListener(
            "click",
            verifyEmailOtp
        );

    }


    if (resendEmailOtpBtn) {

        resendEmailOtpBtn.addEventListener(
            "click",
            resendEmailOtp
        );

    }


    // =====================================================
    // MOBILE EVENTS
    // =====================================================

    if (sendMobileOtpBtn) {

        sendMobileOtpBtn.addEventListener(
            "click",
            sendMobileOtp
        );

    }


    if (verifyMobileOtpBtn) {

        verifyMobileOtpBtn.addEventListener(
            "click",
            verifyMobileOtp
        );

    }


    if (resendMobileOtpBtn) {

        resendMobileOtpBtn.addEventListener(
            "click",
            resendMobileOtp
        );

    }


    // =====================================================
    // EMAIL OTP - ONLY NUMBERS
    // =====================================================

    if (emailOtp) {

        emailOtp.addEventListener(
            "input",
            () => {

                emailOtp.value =
                    emailOtp.value
                        .replace(/\D/g, "")
                        .slice(0, 6);

            }
        );

    }


    // =====================================================
    // MOBILE OTP - ONLY NUMBERS
    // =====================================================

    if (mobileOtp) {

        mobileOtp.addEventListener(
            "input",
            () => {

                mobileOtp.value =
                    mobileOtp.value
                        .replace(/\D/g, "")
                        .slice(0, 6);

            }
        );

    }


    // =====================================================
    // PHONE - ONLY NUMBERS
    // =====================================================

    if (newPhone) {

        newPhone.addEventListener(
            "input",
            () => {

                newPhone.value =
                    newPhone.value
                        .replace(/\D/g, "")
                        .slice(0, 15);

            }
        );

    }


    // =====================================================
    // ENTER - EMAIL OTP
    // =====================================================

    if (emailOtp) {

        emailOtp.addEventListener(
            "keydown",
            (event) => {

                if (event.key === "Enter") {

                    event.preventDefault();

                    verifyEmailOtp();

                }

            }
        );

    }


    // =====================================================
    // ENTER - MOBILE OTP
    // =====================================================

    if (mobileOtp) {

        mobileOtp.addEventListener(
            "keydown",
            (event) => {

                if (event.key === "Enter") {

                    event.preventDefault();

                    verifyMobileOtp();

                }

            }
        );

    }


    // =====================================================
    // INITIAL LOAD
    // =====================================================

    loadProfile();

});