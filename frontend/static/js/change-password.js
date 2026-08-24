document.addEventListener("DOMContentLoaded", function () {
  console.log("CHANGE PASSWORD JS LOADED");

  // =====================================================
  // API ENDPOINTS
  // =====================================================

  const API = {
    profile: "/api/accounts/profile/",

    changePassword: "/api/accounts/change-password/",
  };

  // =====================================================
  // ELEMENTS
  // =====================================================

  const form = document.getElementById("changePasswordForm");

  const firstNameInput = document.getElementById("first_name");

  const currentUserName = document.getElementById("currentUserName");

  const currentUserEmail = document.getElementById("currentUserEmail");

  const currentPassword = document.getElementById("current_password");

  const newPassword = document.getElementById("new_password");

  const confirmPassword = document.getElementById("confirm_password");

  const changePasswordBtn = document.getElementById("changePasswordBtn");

  const messageBox = document.getElementById("changePasswordMessage");
  const profileImage = document.getElementById("currentUserProfileImage");

  const defaultProfileIcon = document.getElementById("defaultProfileIcon");

  // =====================================================
  // GET ACCESS TOKEN
  // =====================================================

  function getAccessToken() {
    return (
      localStorage.getItem("access") ||
      localStorage.getItem("access_token") ||
      localStorage.getItem("accessToken")
    );
  }

  // =====================================================
  // SHOW MESSAGE
  // =====================================================

  function showMessage(message, type = "error") {
    if (!messageBox) {
      return;
    }

    messageBox.textContent = message;

    messageBox.style.display = "block";

    messageBox.classList.remove("success", "error");

    messageBox.classList.add(type);
  }

  // =====================================================
  // CLEAR MESSAGE
  // =====================================================

  function clearMessage() {
    if (!messageBox) {
      return;
    }

    messageBox.textContent = "";

    messageBox.style.display = "none";

    messageBox.classList.remove("success", "error");
  }

  // =====================================================
  // LOAD CURRENT USER
  // =====================================================

  async function loadCurrentUser() {
    const accessToken = getAccessToken();

    console.log("ACCESS TOKEN EXISTS:", !!accessToken);

    if (!accessToken) {
      console.error("ACCESS TOKEN NOT FOUND");

      if (usernameInput) {
        usernameInput.value = "Not logged in";
      }

      if (currentUserName) {
        currentUserName.textContent = "Not logged in";
      }

      if (currentUserEmail) {
        currentUserEmail.textContent = "";
      }

      return;
    }

    try {
      console.log("Loading current user...");

      const response = await fetch(API.profile, {
        method: "GET",

        headers: {
          Authorization: `Bearer ${accessToken}`,

          Accept: "application/json",
        },
      });

      console.log("PROFILE STATUS:", response.status);

      const data = await response.json();

      console.log("PROFILE DATA:", data);

      if (!response.ok) {
        showMessage(
          data.detail || data.message || "Unable to load user profile.",
        );

        return;
      }

      // =================================================
      // USERNAME
      // =================================================

      const username = data.username || data.user?.username || "";

      // =================================================
      // FIRST NAME
      // =================================================

      const firstName = data.first_name || data.user?.first_name || "";

      // =================================================
      // EMAIL
      // =================================================

      const email = data.email || data.user?.email || "";

      // =================================================
      // Profile image
      // =================================================

      const profileImageUrl =
        data.profile_image ||
        data.profile_image_url ||
        data.user?.profile_image ||
        data.user?.profile_image_url ||
        "";

      console.log("FIRST NAME:", firstName);

      // =================================================
      // SET USERNAME INPUT
      // =================================================

      if (firstNameInput) {
        firstNameInput.value = firstName || "First name not available";
      }

      // =================================================
      // SET PROFILE NAME
      // =================================================

      if (currentUserName) {
        currentUserName.textContent = firstName || "ParkX User";
      }

      // =================================================
      // SET EMAIL
      // =================================================

      if (currentUserEmail) {
        currentUserEmail.textContent = email || "Email not available";
      }

      if (profileImage && profileImageUrl) {
        profileImage.src = profileImageUrl;

        profileImage.style.display = "block";

        if (defaultProfileIcon) {
          defaultProfileIcon.style.display = "none";
        }
      } else {
        if (profileImage) {
          profileImage.style.display = "none";
        }

        if (defaultProfileIcon) {
          defaultProfileIcon.style.display = "block";
        }
      }
    } catch (error) {
      console.error("PROFILE REQUEST ERROR:", error);

      showMessage("Unable to load your account information.");
    }
  }

  // =====================================================
  // PASSWORD TOGGLE
  // =====================================================

  const toggleButtons = document.querySelectorAll(".password-toggle");

  toggleButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const targetId = button.getAttribute("data-target");

      const input = document.getElementById(targetId);

      const icon = button.querySelector("i");

      if (!input || !icon) {
        return;
      }

      if (input.type === "password") {
        input.type = "text";

        icon.classList.remove("fa-eye");

        icon.classList.add("fa-eye-slash");

        button.setAttribute("aria-label", "Hide password");
      } else {
        input.type = "password";

        icon.classList.remove("fa-eye-slash");

        icon.classList.add("fa-eye");

        button.setAttribute("aria-label", "Show password");
      }
    });
  });

  // =====================================================
  // CHANGE PASSWORD
  // =====================================================

  async function changePassword(event) {
    event.preventDefault();

    clearMessage();

    if (!currentPassword || !newPassword || !confirmPassword) {
      showMessage("Password fields are missing.");

      return;
    }

    const currentPasswordValue = currentPassword.value.trim();

    const newPasswordValue = newPassword.value;

    const confirmPasswordValue = confirmPassword.value;

    // =================================================
    // VALIDATION
    // =================================================

    if (!currentPasswordValue) {
      showMessage("Please enter your current password.");

      currentPassword.focus();

      return;
    }

    if (!newPasswordValue) {
      showMessage("Please enter your new password.");

      newPassword.focus();

      return;
    }

    if (newPasswordValue.length < 8) {
      showMessage("New password must be at least 8 characters.");

      newPassword.focus();

      return;
    }

    if (!confirmPasswordValue) {
      showMessage("Please confirm your new password.");

      confirmPassword.focus();

      return;
    }

    if (newPasswordValue !== confirmPasswordValue) {
      showMessage("New password and confirm password do not match.");

      confirmPassword.focus();

      return;
    }

    if (currentPasswordValue === newPasswordValue) {
      showMessage("New password must be different from your current password.");

      newPassword.focus();

      return;
    }

    // =================================================
    // TOKEN
    // =================================================

    const accessToken = getAccessToken();

    if (!accessToken) {
      showMessage("Your session has expired. Please login again.");

      return;
    }

    // =================================================
    // DISABLE BUTTON
    // =================================================

    if (changePasswordBtn) {
      changePasswordBtn.disabled = true;

      changePasswordBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Updating...
            `;
    }

    // =================================================
    // REQUEST DATA
    // =================================================

    const requestData = {
      current_password: currentPasswordValue,

      new_password: newPasswordValue,

      confirm_password: confirmPasswordValue,
    };

    console.log("CHANGE PASSWORD REQUEST:", {
      current_password: "***",

      new_password: "***",

      confirm_password: "***",
    });

    try {
      const response = await fetch(API.changePassword, {
        method: "POST",

        headers: {
          Authorization: `Bearer ${accessToken}`,

          "Content-Type": "application/json",

          Accept: "application/json",
        },

        body: JSON.stringify(requestData),
      });

      const responseText = await response.text();

      let data = {};

      try {
        data = responseText ? JSON.parse(responseText) : {};
      } catch {
        data = {
          raw_response: responseText,
        };
      }

      console.log("CHANGE PASSWORD STATUS:", response.status);

      console.log("CHANGE PASSWORD RESPONSE:", data);

      // =================================================
      // UNAUTHORIZED
      // =================================================

      if (response.status === 401) {
        showMessage(
          data.detail ||
            data.message ||
            "Your session has expired. Please login again.",
        );

        return;
      }

      // =================================================
      // VALIDATION / API ERROR
      // =================================================

      if (!response.ok) {
        let errorMessage = "Unable to change password.";

        if (data.detail) {
          errorMessage = data.detail;
        } else if (data.message) {
          errorMessage = data.message;
        } else if (data.current_password) {
          errorMessage = Array.isArray(data.current_password)
            ? data.current_password[0]
            : data.current_password;
        } else if (data.new_password) {
          errorMessage = Array.isArray(data.new_password)
            ? data.new_password[0]
            : data.new_password;
        } else if (data.confirm_password) {
          errorMessage = Array.isArray(data.confirm_password)
            ? data.confirm_password[0]
            : data.confirm_password;
        }

        showMessage(errorMessage, "error");

        return;
      }

      // =================================================
      // SUCCESS
      // =================================================

      showMessage(data.message || "Password changed successfully.", "success");

      // Clear password fields

      currentPassword.value = "";

      newPassword.value = "";

      confirmPassword.value = "";

      // =================================================
      // RESTORE BUTTON
      // =================================================

      if (changePasswordBtn) {
        changePasswordBtn.disabled = false;

        changePasswordBtn.innerHTML = `
                    <i class="fa-solid fa-key"></i>
                    Update Password
                `;
      }

      // Redirect to profile after 1 second

      setTimeout(function () {
        window.location.href = "/profile/";
      }, 1000);
    } catch (error) {
      console.error("CHANGE PASSWORD ERROR:", error);

      showMessage("Unable to connect to the server.");
    } finally {
      if (changePasswordBtn) {
        changePasswordBtn.disabled = false;

        changePasswordBtn.innerHTML = `
                    <i class="fa-solid fa-key"></i>
                    Update Password
                `;
      }
    }
  }

  // =====================================================
  // FORM SUBMIT
  // =====================================================

  if (form) {
    form.addEventListener("submit", changePassword);
  } else {
    console.error("Change password form not found.");
  }

  // =====================================================
  // LOAD USER DATA
  // =====================================================

  loadCurrentUser();
});
