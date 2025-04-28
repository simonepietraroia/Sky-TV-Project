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


document.addEventListener("DOMContentLoaded", function() {
    let clearCheckbox = document.querySelector('.clearable-file-input');
    if (clearCheckbox) {
        clearCheckbox.style.display = "none";
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const deptSelect = document.getElementById('departmentSelect');
    const teamSelect = document.getElementById('teamSelect');
  
    function filterTeams() {
      const chosen = deptSelect.value;
      Array.from(teamSelect.options).forEach(opt => {
        if (!opt.value) return;         // skip the “Choose…” placeholder
        // show only if data-dept matches
        opt.style.display = opt.dataset.dept === chosen ? '' : 'none';
      });
      // if the current team is now hidden, reset it
      if (teamSelect.selectedIndex > 0 &&
          teamSelect.options[teamSelect.selectedIndex].style.display === 'none') {
        teamSelect.value = '';
      }
    }
  
    deptSelect.addEventListener('change', filterTeams);
    // run once on load in case of a pre-selected department
    filterTeams();
  });

document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('input[name="health_cards"]');
    const previewArea = document.getElementById('preview-area');
  
    function updatePreview() {
      previewArea.innerHTML = ''; // Clear previous preview
  
      checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
          const cardDiv = checkbox.closest('.card');
          const cardName = cardDiv.querySelector('h5').textContent;
          const cardDesc = cardDiv.querySelector('p').textContent;
  
          const previewCard = document.createElement('div');
          previewCard.className = 'col-md-6';
          previewCard.innerHTML = `
            <div class="card border border-info shadow-sm p-4 h-100">
              <h5 class="text-info">${cardName}</h5>
              <p class="text-muted small">${cardDesc}</p>
              <div class="d-flex justify-content-between my-2">
                <button class="btn btn-danger btn-sm" disabled>🔴 Red</button>
                <button class="btn btn-warning btn-sm" disabled>🟡 Yellow</button>
                <button class="btn btn-success btn-sm" disabled>🟢 Green</button>
              </div>
              <div class="mt-2">
                <select class="form-select form-select-sm" disabled>
                  <option selected>Trend</option>
                  <option>⬆️ Improving</option>
                  <option>⬇️ Declining</option>
                </select>
              </div>
              <textarea class="form-control mt-2" rows="2" placeholder="Comment..." disabled></textarea>
            </div>
          `;
          previewArea.appendChild(previewCard);
        }
      });
    }
  
    checkboxes.forEach(cb => cb.addEventListener('change', updatePreview));
});

document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('input[name="health_cards"]');
    const previewArea = document.getElementById('preview-area');
  
    function updatePreview() {
      previewArea.innerHTML = ''; // Clear previous preview
  
      checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
          const cardDiv = checkbox.closest('.card');
          const cardName = cardDiv.querySelector('h5').textContent;
          const cardDesc = cardDiv.querySelector('p').textContent;
  
          // 👉 Always use default descriptions
          const desc = {
            red: "Serious issue needs urgent attention.",
            yellow: "Some concerns, manageable.",
            green: "Everything is on track."
          };
  
          const previewCard = document.createElement('div');
          previewCard.className = 'col-md-6';
          previewCard.innerHTML = `
            <div class="card border border-info shadow-sm p-4 h-100">
              <h5 class="text-info">${cardName}</h5>
              <p class="text-muted small">${cardDesc}</p>
              <div class="d-flex justify-content-between my-2">
                <button class="btn btn-danger btn-sm" disabled>🔴 Red</button>
                <button class="btn btn-warning btn-sm" disabled>🟡 Yellow</button>
                <button class="btn btn-success btn-sm" disabled>🟢 Green</button>
              </div>
              <ul class="list-unstyled mb-2 small">
                <li><strong class="text-danger">🔴 Red:</strong> ${desc.red}</li>
                <li><strong class="text-warning">🟡 Yellow:</strong> ${desc.yellow}</li>
                <li><strong class="text-success">🟢 Green:</strong> ${desc.green}</li>
              </ul>
              <div class="mt-2">
                <select class="form-select form-select-sm" disabled>
                  <option selected>Trend</option>
                  <option>⬆️ Improving</option>
                  <option>⬇️ Declining</option>
                </select>
              </div>
              <textarea class="form-control mt-2" rows="2" placeholder="Comment..." disabled></textarea>
            </div>
          `;
          previewArea.appendChild(previewCard);
        }
      });
    }
  
    checkboxes.forEach(cb => cb.addEventListener('change', updatePreview));
});
  