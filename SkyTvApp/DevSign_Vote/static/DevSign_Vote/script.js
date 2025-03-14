document.addEventListener("DOMContentLoaded", function () {
    const profileToggle = document.getElementById("profileDropdownToggle");
    const profileDropdown = document.getElementById("profileDropdown");

    // Function to toggle dropdown visibility
    profileToggle.addEventListener("click", function (event) {
        event.preventDefault();
        profileDropdown.classList.toggle("show");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
        if (!profileToggle.contains(event.target) && !profileDropdown.contains(event.target)) {
            profileDropdown.classList.remove("show");
        }
    });
});