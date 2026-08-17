document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const loginBtn = document.getElementById("loginBtn");

  if (!loginForm) {
    return;
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = loginForm.querySelector('input[name="email"]').value.trim();
    const password = loginForm.querySelector('input[name="password"]').value;

    if (!email || !password) {
      showLoginError("Please enter your email and password.");
      return;
    }

    loginBtn.disabled = true;
    loginBtn.innerHTML = "Logging in...";

    try {
      const response = await fetch("/api/accounts/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        showLoginError(data.detail || "Invalid email or password.");
        return;
      }

      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));

      console.log("LOGIN RESPONSE:", data);
    console.log("USER:", data.user);
    console.log("ROLE:", data.user?.role);
    console.log("REDIRECTING TO DASHBOARD...");

      // Login successful
      window.location.href = "/dashboard/";
    } catch (error) {
      console.error("Login error:", error);
      showLoginError("Unable to connect to the server. Please try again.");
    } finally {
      loginBtn.disabled = false;
      loginBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> Login';
    }
  });
});

function showLoginError(message) {
  let errorElement = document.getElementById("loginError");

  if (!errorElement) {
    errorElement = document.createElement("div");
    errorElement.id = "loginError";
    errorElement.className = "login-error";

    const form = document.getElementById("loginForm");
    form.insertBefore(errorElement, form.firstChild);
  }

  errorElement.textContent = message;
}

function togglePassword() {
  const passwordInput = document.getElementById("password");
  const passwordIcon = document.getElementById("passwordIcon");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    passwordIcon.classList.remove("fa-eye");
    passwordIcon.classList.add("fa-eye-slash");
  } else {
    passwordInput.type = "password";
    passwordIcon.classList.remove("fa-eye-slash");
    passwordIcon.classList.add("fa-eye");
  }
}
