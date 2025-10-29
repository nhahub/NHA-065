// Zypher AI - ChatGPT-Style Interface JavaScript

// State
let currentSettings = {
    use_lora: false,
    num_steps: 4,
    width: 1024,
    height: 1024,
    use_ip_adapter: false,
    ip_adapter_scale: 0.5,
    reference_image: null,
};

let conversationHistory = [];

// Return Authorization headers if an auth token is available
function getAuthHeaders() {
    const token = localStorage.getItem("authToken");
    if (token) {
        return { Authorization: "Bearer " + token };
    }
    return {};
}

// Initialize
let userProfile = null;
document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
    loadUserProfile();
    focusInput();
});

// Focus input on load
function focusInput() {
    document.getElementById("promptInput").focus();
}

// Auto-resize textarea
function autoResize(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = textarea.scrollHeight + "px";
}

// Handle key press
function handleKeyPress(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// Use example prompt
function usePrompt(button) {
  const promptText = button.querySelector(".prompt-text").textContent;
  document.getElementById("promptInput").value = promptText;
  document.getElementById("welcomeScreen").style.display = "none";
  focusInput();
}

// New chat
function newChat() {
  conversationHistory = [];
  document.getElementById("messages").innerHTML = "";
  document.getElementById("welcomeScreen").style.display = "flex";
  document.getElementById("promptInput").value = "";
  focusInput();
}

// Send message
async function sendMessage() {
  const input = document.getElementById("promptInput");
  const prompt = input.value.trim();

  if (!prompt) return;

  // Hide welcome screen
  document.getElementById("welcomeScreen").style.display = "none";

  // Add user message
  addMessage("user", prompt);

  // Clear input
  input.value = "";
  input.style.height = "auto";

  // Disable send button
  const sendBtn = document.getElementById("sendBtn");
  sendBtn.disabled = true;

  // Show loading
  showLoading();

  try {
    // Prepare request data
    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("use_lora", currentSettings.use_lora);
    formData.append("num_steps", currentSettings.num_steps);
    formData.append("width", currentSettings.width);
    formData.append("height", currentSettings.height);
    formData.append("use_ip_adapter", currentSettings.use_ip_adapter);
    formData.append("ip_adapter_scale", currentSettings.ip_adapter_scale);

    // Add reference image if provided
    if (currentSettings.use_ip_adapter && currentSettings.reference_image) {
      formData.append("reference_image", currentSettings.reference_image);
    }

    // Send request
    const authHeaders = getAuthHeaders();
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: authHeaders,
      body: formData,
    });

    const data = await response.json();

    if (data.success) {
      // Add assistant message with image
      addMessage("assistant", "", data.image, data.metadata, data.filename);

      // Add to conversation history
      conversationHistory.push({
        user: prompt,
        assistant: data.filename,
        timestamp: new Date().toISOString(),
      });

      // Update history list
      updateHistoryList();
    } else {
      addErrorMessage(data.error || "Generation failed");
    }
  } catch (error) {
    console.error("Error:", error);
    addErrorMessage(
      "Network error. Please check your connection and try again."
    );
  } finally {
    hideLoading();
    sendBtn.disabled = false;
    focusInput();
  }
}

// Add message to chat
function addMessage(
  role,
  text,
  imageUrl = null,
  metadata = null,
  filename = null
) {
  const messages = document.getElementById("messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}`;

  const avatar = role === "user" ? "👤" : "🎨";

  let messageHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
    `;

  if (text) {
    messageHTML += `<div class="message-text">${escapeHtml(text)}</div>`;
  }

  if (imageUrl) {
    messageHTML += `
            <div class="message-image">
                <img src="${imageUrl}" alt="Generated logo">
            </div>
        `;
  }

  if (metadata) {
    messageHTML += `
            <div class="message-metadata">
                <div class="metadata-row">
                    <span class="metadata-label">Model:</span>
                    <span>${metadata.model}</span>
                </div>
                <div class="metadata-row">
                    <span class="metadata-label">Steps:</span>
                    <span>${metadata.steps}</span>
                </div>
                <div class="metadata-row">
                    <span class="metadata-label">Dimensions:</span>
                    <span>${metadata.dimensions}</span>
                </div>
                ${
                  metadata.ip_adapter
                    ? `
                <div class="metadata-row">
                    <span class="metadata-label">IP-Adapter Scale:</span>
                    <span>${(metadata.ip_adapter_scale * 100).toFixed(
                      0
                    )}%</span>
                </div>
                `
                    : ""
                }
                <div class="metadata-row">
                    <span class="metadata-label">Generated:</span>
                    <span>${metadata.timestamp}</span>
                </div>
                ${
                  filename
                    ? `
                <button class="download-btn" onclick="downloadImage('${imageUrl}', '${filename}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download
                </button>
                `
                    : ""
                }
            </div>
        `;
  }

  messageHTML += `</div>`;
  messageDiv.innerHTML = messageHTML;

  messages.appendChild(messageDiv);
  scrollToBottom();
}

// Add error message
function addErrorMessage(errorText) {
  const messages = document.getElementById("messages");
  const errorDiv = document.createElement("div");
  errorDiv.className = "message assistant";
  errorDiv.innerHTML = `
        <div class="message-avatar">⚠️</div>
        <div class="message-content">
            <div class="error-message">
                <strong>Error:</strong> ${escapeHtml(errorText)}
            </div>
        </div>
    `;
  messages.appendChild(errorDiv);
  scrollToBottom();
}

// Download image
function downloadImage(dataUrl, filename) {
  const link = document.createElement("a");
  link.href = dataUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Scroll to bottom
function scrollToBottom() {
  const chatContainer = document.getElementById("chatContainer");
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show/hide loading
function showLoading() {
  document.getElementById("loadingOverlay").style.display = "flex";
}

function hideLoading() {
  document.getElementById("loadingOverlay").style.display = "none";
}

// Toggle sidebar (mobile)
function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("active");
}

// Toggle settings modal
function toggleSettings() {
  const modal = document.getElementById("settingsModal");
  modal.classList.toggle("active");

  // Load current settings
  const useLoraToggle = document.getElementById("useLoraToggle");
  const stepsSlider = document.getElementById("stepsSlider");
  const widthSlider = document.getElementById("widthSlider");
  const heightSlider = document.getElementById("heightSlider");

  if (useLoraToggle) useLoraToggle.checked = currentSettings.use_lora;
  if (stepsSlider) stepsSlider.value = currentSettings.num_steps;
  if (widthSlider) widthSlider.value = currentSettings.width;
  if (heightSlider) heightSlider.value = currentSettings.height;

  updateStepsValue(currentSettings.num_steps);
  updateWidthValue(currentSettings.width);
  updateHeightValue(currentSettings.height);

  // Populate profile fields if available
  const fnameEl = document.getElementById("fnameInput");
  const lnameEl = document.getElementById("lnameInput");
  if (userProfile) {
    if (fnameEl) fnameEl.value = userProfile.fname || "";
    if (lnameEl) lnameEl.value = userProfile.lname || "";
  } else {
    if (fnameEl) fnameEl.value = "";
    if (lnameEl) lnameEl.value = "";
  }
}

// Update setting values
function updateStepsValue(value) {
  document.getElementById("stepsValue").textContent = value;
  currentSettings.num_steps = parseInt(value);
}

function updateWidthValue(value) {
  document.getElementById("widthValue").textContent = value;
  currentSettings.width = parseInt(value);
}

function updateHeightValue(value) {
  document.getElementById("heightValue").textContent = value;
  currentSettings.height = parseInt(value);
}

function updateIpAdapterScale(value) {
  document.getElementById("ipAdapterScaleValueInline").textContent = value;
  currentSettings.ip_adapter_scale = parseFloat(value) / 100;
}

// Toggle IP-Adapter
function toggleIpAdapter(enabled) {
  currentSettings.use_ip_adapter = enabled;
  const referenceContent = document.getElementById("referenceContent");
  referenceContent.style.display = enabled ? "block" : "none";
}

// Handle image upload
function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Validate file type
  if (!file.type.startsWith("image/")) {
    alert("Please upload an image file (JPG, PNG, WEBP)");
    return;
  }

  // Store file
  currentSettings.reference_image = file;

  // Show preview
  const reader = new FileReader();
  reader.onload = function (e) {
    document.getElementById("previewImgInline").src = e.target.result;
    document.getElementById("uploadAreaInline").style.display = "none";
    document.getElementById("imagePreviewInline").style.display = "block";
  };
  reader.readAsDataURL(file);
}

// Remove reference image
function removeReferenceImage(event) {
  if (event) event.stopPropagation();
  currentSettings.reference_image = null;
  document.getElementById("referenceImageInput").value = "";
  document.getElementById("previewImgInline").src = "";
  document.getElementById("uploadAreaInline").style.display = "flex";
  document.getElementById("imagePreviewInline").style.display = "none";
}

// Save settings
document.addEventListener("change", (e) => {
  if (e.target.id === "useLoraToggle") {
    currentSettings.use_lora = e.target.checked;
  }
});

// Load model status
async function loadModelStatus() {
  const statusDiv = document.getElementById("modelStatus");
  statusDiv.style.display = "block";
  statusDiv.innerHTML = "<p>Loading...</p>";

  try {
    const response = await fetch("/api/model/status", {
      headers: getAuthHeaders(),
    });
    const data = await response.json();

    if (data.success) {
      const model = data.model;
      statusDiv.innerHTML = `
                <pre>
Base Model: ${model.base_model_loaded ? "✅ Loaded" : "❌ Not loaded"}
LoRA Model: ${model.lora_loaded ? "✅ Loaded" : "⚠️ Not loaded"}
IP-Adapter: ${model.ip_adapter_loaded ? "✅ Loaded" : "⚠️ Not loaded"}
Device: ${model.device}
Model ID: ${model.model_id || "None"}
Status: ${model.base_model_loaded ? "🟢 Ready" : "🔴 Not ready"}
                </pre>
            `;
    } else {
      statusDiv.innerHTML = `<p class="error-message">${data.error}</p>`;
    }
  } catch (error) {
    statusDiv.innerHTML = `<p class="error-message">Failed to load model status</p>`;
  }
}

// Load history
async function loadHistory() {
  try {
    const response = await fetch("/api/history", { headers: getAuthHeaders() });
    const data = await response.json();

    if (data.success && data.history) {
      conversationHistory = data.history;
      updateHistoryList();
    }
  } catch (error) {
    console.error("Failed to load history:", error);
  }
}

// Load current user's profile (fname/lname)
async function loadUserProfile() {
  try {
    const resp = await fetch("/api/user/profile", {
      headers: getAuthHeaders(),
    });
    const data = await resp.json();
    if (data.success && data.profile) {
      userProfile = data.profile;
      const fname = userProfile.fname || "";
      const lname = userProfile.lname || "";
      const initials =
        ((fname[0] || "") + (lname[0] || "")).toUpperCase() || "AI";
      const defaultName = userProfile.email
        ? userProfile.email.split("@")[0]
        : "User";
      const avatarEl = document.getElementById("userAvatar");
      const nameEl = document.getElementById("userFullName");
      if (avatarEl) avatarEl.textContent = initials;
      if (nameEl)
        nameEl.textContent =
          fname || lname ? `${fname} ${lname}`.trim() : defaultName;
      // Show plan info: free users limited to 5 prompts
      try {
        const planEl = document.getElementById("planInfo");
        if (planEl) {
          const isPro = !!userProfile.is_pro;
          const used = Number(userProfile.prompt_count || 0);
          if (isPro) {
            planEl.textContent = "Pro — Unlimited prompts";
          } else {
            planEl.innerHTML = `Free — max prompts: 5 (used ${used}/5) <a href="/upgrade" style="margin-left:8px; color: var(--accent-color); font-weight:600;">Upgrade</a>`;
          }
        }
      } catch (e) {
        console.warn("Could not render plan info", e);
      }
    }
  } catch (err) {
    console.warn("Could not load user profile", err);
  }
}

// Save current user's profile (fname/lname)
async function saveUserProfile() {
  const fname = (document.getElementById("fnameInput") || {}).value || "";
  const lname = (document.getElementById("lnameInput") || {}).value || "";
  try {
    const resp = await fetch("/api/user/profile", {
      method: "POST",
      headers: Object.assign(
        { "Content-Type": "application/json" },
        getAuthHeaders()
      ),
      body: JSON.stringify({ fname: fname || null, lname: lname || null }),
    });
    const data = await resp.json();
    if (data.success && data.profile) {
      userProfile = data.profile;
      // Update UI
      const avatarEl = document.getElementById("userAvatar");
      const nameEl = document.getElementById("userFullName");
      const initials =
        ((userProfile.fname || "")[0] || "") +
        ((userProfile.lname || "")[0] || "");
      if (avatarEl) avatarEl.textContent = initials.toUpperCase() || "AI";
      const defaultName = userProfile.email
        ? userProfile.email.split("@")[0]
        : "User";
      if (nameEl)
        nameEl.textContent =
          userProfile.fname || userProfile.lname
            ? `${userProfile.fname || ""} ${userProfile.lname || ""}`.trim()
            : defaultName;
      // Close modal
      toggleSettings();
      alert("Profile saved");
    } else {
      alert("Could not save profile: " + (data.error || "Unknown error"));
    }
  } catch (err) {
    console.error("Failed to save profile", err);
    alert("Failed to save profile");
  }
}

// Update history list in sidebar
function updateHistoryList() {
  const historyList = document.getElementById("historyList");

  if (conversationHistory.length === 0) {
    historyList.innerHTML =
      '<p style="color: var(--text-secondary); font-size: 13px; padding: 12px;">No history yet</p>';
    return;
  }

  historyList.innerHTML = conversationHistory
    .slice(-10)
    .reverse()
    .map((item, index) => {
      const text = item.user || item[0] || "Untitled";
      return `<button class="history-item" onclick="viewHistoryItem(${index})">${escapeHtml(
        text.substring(0, 40)
      )}${text.length > 40 ? "..." : ""}</button>`;
    })
    .join("");
}

// View history item
function viewHistoryItem(index) {
  // This would load a previous conversation
  console.log("View history item:", index);
}

// Utility: Escape HTML
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Close modal on outside click
document.getElementById("settingsModal").addEventListener("click", (e) => {
  if (e.target.id === "settingsModal") {
    toggleSettings();
  }
});

// Close sidebar on outside click (mobile)
document.addEventListener("click", (e) => {
  const sidebar = document.getElementById("sidebar");
  const menuBtn = document.querySelector(".menu-btn");

  if (
    window.innerWidth <= 768 &&
    sidebar.classList.contains("active") &&
    !sidebar.contains(e.target) &&
    !menuBtn.contains(e.target)
  ) {
    sidebar.classList.remove("active");
  }
});

/* ========================================
   SUBSCRIPTION MANAGEMENT FUNCTIONS
   ======================================== */

/**
 * Cancel subscription function
 */
async function cancelSubscription() {
  const confirmCancel = confirm(
    "Are you sure you want to cancel your Pro subscription?\n\n" +
      "You will lose access to:\n" +
      "• Unlimited logo generations\n" +
      "• Priority support\n\n" +
      "Your access will continue until the end of your billing period."
  );

  if (!confirmCancel) {
    return;
  }

  try {
    const token = localStorage.getItem("authToken");
    if (!token) {
      showNotification("Please sign in to manage your subscription", "error");
      return;
    }

    const response = await fetch("/api/subscription/cancel", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      showNotification("Subscription cancelled successfully", "success");

      const subscriptionSection = document.getElementById(
        "subscriptionSection"
      );
      if (subscriptionSection) {
        subscriptionSection.style.display = "none";
      }

      await loadUserProfile();

      setTimeout(() => {
        const modal = document.getElementById("settingsModal");
        if (modal) {
          modal.classList.remove("active");
        }
      }, 1500);
    } else {
      showNotification(data.error || "Failed to cancel subscription", "error");
    }
  } catch (error) {
    console.error("Error cancelling subscription:", error);
    showNotification("An error occurred. Please try again.", "error");
  }
}

/**
 * Show subscription section if user is Pro
 */
async function checkAndShowSubscription() {
  try {
    const token = localStorage.getItem("authToken");
    if (!token) return;

    const response = await fetch("/api/user/profile", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    const subscriptionSection = document.getElementById("subscriptionSection");
    if (!subscriptionSection) return;

    if (data.success && data.profile && data.profile.is_pro) {
      subscriptionSection.style.display = "block";
    } else {
      subscriptionSection.style.display = "none";
    }
  } catch (error) {
    console.error("Error checking subscription status:", error);
  }
}

/**
 * Show notification toast
 */
function showNotification(message, type = "info") {
  const existing = document.querySelector(".notification-toast");
  if (existing) {
    existing.remove();
  }

  const notification = document.createElement("div");
  notification.className = `notification-toast notification-${type}`;
  notification.textContent = message;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.classList.add("show");
  }, 10);

  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

// Enhance toggleSettings to check subscription status
if (typeof window.toggleSettings !== "undefined") {
  const originalToggleSettings = window.toggleSettings;
  window.toggleSettings = function () {
    originalToggleSettings();

    const modal = document.getElementById("settingsModal");
    if (modal && modal.classList.contains("active")) {
      checkAndShowSubscription();
    }
  };
} else {
  window.toggleSettings = function () {
    const modal = document.getElementById("settingsModal");
    if (!modal) return;

    modal.classList.toggle("active");

    if (modal.classList.contains("active")) {
      checkAndShowSubscription();
    }
  };
}

let firebaseUser = null;

// Initialize Firebase
async function initFirebase() {
  try {
    const resp = await fetch("/api/firebase-config");
    const data = await resp.json();

    if (data && data.success && data.config && data.config.apiKey) {
      firebase.initializeApp(data.config);

      firebase.auth().onAuthStateChanged((user) => {
        if (user) {
          firebaseUser = user;
          document.getElementById("userEmail").value = user.email;

          // Get email from backend
          user.getIdToken().then((token) => {
            fetch("/get-user-email", {
              headers: { Authorization: "Bearer " + token },
            })
              .then((r) => r.json())
              .then((data) => {
                if (data.success && data.email) {
                  document.getElementById("userEmail").value = data.email;
                }
              })
              .catch((err) => console.error("Error fetching email:", err));
          });
        } else {
          // Not authenticated, redirect to login
          window.location.href = "/login";
        }
      });
    } else {
      console.error("Firebase config not available");
    }
  } catch (error) {
    console.error("Error initializing Firebase:", error);
  }
}

function openMockCheckout() {
  const email = document.getElementById("userEmail").value;

  if (!email || email === "Loading...") {
    alert("Please wait for email to load");
    return;
  }

  if (!firebaseUser) {
    alert("Please sign in first");
    window.location.href = "/login";
    return;
  }

  document.getElementById("checkoutEmail").textContent = email;
  document.getElementById("checkoutModal").classList.add("show");
}

function closeMockCheckout() {
  document.getElementById("checkoutModal").classList.remove("show");
}

async function completeMockPayment() {
  const email = document.getElementById("userEmail").value;
  const upgradeBtn = document.getElementById("upgradeBtn");

  if (!firebaseUser) {
    alert("Not authenticated");
    return;
  }
  // Disable button and show loading
  upgradeBtn.disabled = true;
  upgradeBtn.textContent = "Processing...";
  console.log("Processing mock payment for:", email);
  try {
    const token = await firebaseUser.getIdToken();

    const response = await fetch("/payment/success", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        checkoutId: "mock_" + Date.now(),
        orderId: "order_" + Date.now(),
        email: email,
        mock: true,
      }),
    });
    const result = await response.json();
    if (result.success) {
      closeMockCheckout();

      // Show success message
      alert(
        "🎉 Pro activated successfully!\n\nYou now have unlimited prompts and access to all Pro features."
      );

      // Redirect to home
      setTimeout(() => {
        window.location.href = "/";
      }, 500);
    } else {
      alert("Error: " + (result.error || "Unknown error occurred"));
      upgradeBtn.disabled = false;
      upgradeBtn.innerHTML =
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"></path></svg> Upgrade to Pro';
    }
  } catch (err) {
    console.error("Payment error:", err);
    alert("Error activating Pro. Please check console and try again.");
    upgradeBtn.disabled = false;
    upgradeBtn.innerHTML =
      '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"></path></svg> Upgrade to Pro';
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", initFirebase);
