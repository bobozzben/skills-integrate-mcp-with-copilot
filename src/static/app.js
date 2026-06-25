document.addEventListener("DOMContentLoaded", () => {
  const authPanel = document.getElementById("auth-panel");
  const authStatus = document.getElementById("auth-status");
  const signupForm = document.getElementById("signup-form");
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const messageDiv = document.getElementById("message");
  const rolePanel = document.getElementById("role-panel");
  const roleSummary = document.getElementById("role-summary");
  const loginTab = document.getElementById("login-tab");
  const registerTab = document.getElementById("register-tab");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const authMessage = document.getElementById("auth-message");

  let currentUser = null;

  function setMessage(element, text, type = "success") {
    element.textContent = text;
    element.className = `message ${type}`;
  }

  function clearMessage(element) {
    element.textContent = "";
    element.className = "message";
  }

  async function fetchCurrentUser() {
    try {
      const response = await fetch("/api/auth/me");
      if (!response.ok) {
        currentUser = null;
        return null;
      }
      currentUser = await response.json();
      return currentUser;
    } catch (error) {
      currentUser = null;
      return null;
    }
  }

  function renderAuthPanel(user) {
    if (!authPanel) {
      return;
    }

    if (!user) {
      authPanel.innerHTML = '<a class="pill" href="/static/login.html">Sign in</a>';
      return;
    }

    authPanel.innerHTML = `
      <span class="pill">${user.role.replace("_", " ")}</span>
      <span class="pill">${user.email}</span>
      <button id="logout-button" type="button">Log out</button>
    `;

    const logoutButton = document.getElementById("logout-button");
    logoutButton?.addEventListener("click", async () => {
      await fetch("/api/auth/logout", { method: "POST" });
      window.location.reload();
    });
  }

  async function renderRolePanel(user) {
    if (!rolePanel || !roleSummary) {
      return;
    }

    if (!user) {
      rolePanel.classList.add("hidden");
      return;
    }

    rolePanel.classList.remove("hidden");
    const roleText =
      user.role === "student"
        ? "Students can browse activities and join clubs."
        : user.role === "club_admin"
        ? "Club admins can review activity participation and manage their club view."
        : "Super admins can oversee the entire extracurricular platform.";

    roleSummary.innerHTML = `
      <p><strong>Current role:</strong> ${user.role.replace("_", " ")}</p>
      <p>${roleText}</p>
    `;
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
                <h5>Participants:</h5>
                <ul class="participants-list">
                  ${details.participants
                    .map(
                      (email) =>
                        `<li><span class="participant-email">${email}</span>${currentUser ? '<button class="delete-btn" data-activity="' + name + '" data-email="' + email + '">❌</button>' : ""}</li>`
                    )
                    .join("")}
                </ul>
              </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();
      if (response.ok) {
        setMessage(messageDiv, result.message, "success");
        await fetchActivities();
      } else {
        setMessage(messageDiv, result.detail || "An error occurred", "error");
      }
      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      setMessage(messageDiv, "Failed to unregister. Please try again.", "error");
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  async function initializeApp() {
    const user = await fetchCurrentUser();
    renderAuthPanel(user);
    renderRolePanel(user);

    if (!user) {
      if (authStatus) {
        authStatus.textContent = "Please sign in to register for activities.";
        authStatus.className = "info";
      }
      signupForm?.classList.add("hidden");
      return;
    }

    if (authStatus) {
      authStatus.textContent = `Signed in as ${user.email} (${user.role.replace("_", " ")}).`;
      authStatus.className = "info";
    }
    signupForm?.classList.remove("hidden");
    await fetchActivities();
  }

  signupForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!currentUser) {
      setMessage(messageDiv, "Please sign in first.", "error");
      messageDiv.classList.remove("hidden");
      return;
    }

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();
      if (response.ok) {
        setMessage(messageDiv, result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        setMessage(messageDiv, result.detail || "An error occurred", "error");
      }

      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      setMessage(messageDiv, "Failed to sign up. Please try again.", "error");
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  if (loginTab && registerTab && loginForm && registerForm) {
    loginTab.addEventListener("click", () => {
      loginTab.classList.add("active");
      registerTab.classList.remove("active");
      loginForm.classList.add("active");
      registerForm.classList.remove("active");
      clearMessage(authMessage);
    });

    registerTab.addEventListener("click", () => {
      registerTab.classList.add("active");
      loginTab.classList.remove("active");
      registerForm.classList.add("active");
      loginForm.classList.remove("active");
      clearMessage(authMessage);
    });

    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = {
        email: document.getElementById("login-email").value,
        password: document.getElementById("login-password").value,
      };

      try {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.ok) {
          setMessage(authMessage, "Signed in successfully. Redirecting...", "success");
          window.location.href = "/static/index.html";
        } else {
          setMessage(authMessage, result.detail || "Unable to sign in", "error");
        }
      } catch (error) {
        setMessage(authMessage, "Unable to sign in right now.", "error");
      }
    });

    registerForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = {
        name: document.getElementById("register-name").value,
        email: document.getElementById("register-email").value,
        password: document.getElementById("register-password").value,
      };

      try {
        const response = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.ok) {
          setMessage(authMessage, "Account created. Redirecting...", "success");
          window.location.href = "/static/index.html";
        } else {
          setMessage(authMessage, result.detail || "Unable to create account", "error");
        }
      } catch (error) {
        setMessage(authMessage, "Unable to create account right now.", "error");
      }
    });
  }

  initializeApp();
});
