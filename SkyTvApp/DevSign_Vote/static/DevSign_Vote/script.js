document.addEventListener("DOMContentLoaded", function () {
    const profileToggle = document.getElementById("profileDropdownToggle");
    const profileDropdown = document.getElementById("profileDropdown");

    
    profileToggle.addEventListener("mouseenter", function () {
        profileDropdown.classList.add("show");
    });

    profileDropdown.addEventListener("mouseenter", function () {
        profileDropdown.classList.add("show");
    });

    
    profileToggle.addEventListener("mouseleave", function () {
        setTimeout(function () {
            if (!profileDropdown.matches(":hover")) {
                profileDropdown.classList.remove("show");
            }
        }, 800); 
    });

    profileDropdown.addEventListener("mouseleave", function () {
        profileDropdown.classList.remove("show");
    });
});
