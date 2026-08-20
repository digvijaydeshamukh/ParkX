document.addEventListener("DOMContentLoaded", function () {
  console.log("Dashboard JS loaded");

  const toggleButton = document.getElementById("dashboardMenuToggle");

  const dashboardLayout = document.querySelector(".dashboard-layout");

  console.log("Toggle button:", toggleButton);

  console.log("Dashboard layout:", dashboardLayout);

  if (!toggleButton) {
    console.error("dashboardMenuToggle not found");

    return;
  }

  if (!dashboardLayout) {
    console.error(".dashboard-layout not found");

    return;
  }

  toggleButton.addEventListener("click", function () {
    console.log("Dashboard toggle clicked");

    dashboardLayout.classList.toggle("sidebar-collapsed");

    console.log(
      "Sidebar collapsed:",
      dashboardLayout.classList.contains("sidebar-collapsed"),
    );
  });
});
