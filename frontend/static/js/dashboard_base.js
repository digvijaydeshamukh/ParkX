// =====================================================
// LOAD SIDEBAR PROFILE
// =====================================================

async function loadSidebarProfile() {

    const accessToken =
        localStorage.getItem("access_token");

    if (!accessToken) {
        return;
    }

    try {

        const response = await fetch(
            "/api/accounts/profile/",
            {
                method: "GET",

                headers: {
                    "Authorization":
                        `Bearer ${accessToken}`,

                    "Content-Type":
                        "application/json"
                }
            }
        );


        if (!response.ok) {

            console.error(
                "Sidebar profile API failed:",
                response.status
            );

            return;
        }


        const data =
            await response.json();


        console.log(
            "Sidebar profile:",
            data
        );


        const sidebarImage =
            document.querySelector(
                ".sidebar-profile-image"
            );

        const sidebarUserName =
        document.getElementById("sidebarUserName");

        if (sidebarUserName) {

            sidebarUserName.textContent =
                data.first_name ||
                data.username ||
                "";
        }

        if (!sidebarImage) {

            console.error(
                "Sidebar profile image container not found."
            );

            return;
        }


        // =================================================
        // SHOW PROFILE IMAGE
        // =================================================

        if (data.profile_image) {

            sidebarImage.innerHTML = `
                <img
                    src="${data.profile_image}"
                    alt="Profile Image"
                >
            `;

        }

        // =================================================
        // SHOW DEFAULT ICON
        // =================================================

        else {

            sidebarImage.innerHTML = `
                <i class="fa-solid fa-user"></i>
            `;

        }

    } catch (error) {

        console.error(
            "Error loading sidebar profile:",
            error
        );

    }

}


// =====================================================
// DOM LOADED
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "Dashboard Base JS loaded"
        );


        // =================================================
        // AUTHENTICATION CHECK
        // =================================================

        const accessToken =
            localStorage.getItem(
                "access_token"
            );


        const logoutButton =
            document.getElementById(
                "logoutButton"
            );


        const loginURL =
            logoutButton?.dataset.loginUrl;


        if (!accessToken) {

            console.log(
                "No access token. Redirecting to login."
            );


            if (loginURL) {

                window.location.replace(
                    loginURL
                );

            } else {

                console.error(
                    "Login URL not found."
                );

            }


            return;
        }


        // =================================================
        // SIDEBAR TOGGLE
        // =================================================

        const toggleButton =
            document.getElementById(
                "dashboardMenuToggle"
            );


        const dashboardLayout =
            document.querySelector(
                ".dashboard-layout"
            );


        if (
            toggleButton &&
            dashboardLayout
        ) {

            toggleButton.addEventListener(
                "click",
                function () {

                    console.log(
                        "Dashboard toggle clicked"
                    );


                    dashboardLayout.classList.toggle(
                        "sidebar-collapsed"
                    );

                }
            );

        }


        // =================================================
        // LOGOUT
        // =================================================

        if (logoutButton) {

            logoutButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    const confirmed =
                        confirm(
                            "Are you sure you want to logout?"
                        );


                    if (!confirmed) {

                        return;

                    }


                    // =====================================
                    // REMOVE JWT DATA
                    // =====================================

                    localStorage.removeItem(
                        "access_token"
                    );

                    localStorage.removeItem(
                        "refresh_token"
                    );

                    localStorage.removeItem(
                        "user"
                    );


                    console.log(
                        "User logged out."
                    );


                    // =====================================
                    // REDIRECT TO LOGIN
                    // =====================================

                    if (loginURL) {

                        window.location.replace(
                            loginURL
                        );

                    }

                }
            );

        }


        // =================================================
        // LOAD SIDEBAR PROFILE
        // =================================================

        loadSidebarProfile();

    }
);