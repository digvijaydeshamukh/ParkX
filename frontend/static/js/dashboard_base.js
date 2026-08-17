document.addEventListener("DOMContentLoaded", function () {

    const toggleButton = document.getElementById(
        "dashboardMenuToggle"
    );

    const dashboardLayout = document.querySelector(
        ".dashboard-layout"
    );


    if (!toggleButton || !dashboardLayout) {
        return;
    }


    toggleButton.addEventListener("click", function () {

        dashboardLayout.classList.toggle(
            "sidebar-collapsed"
        );

    });

});