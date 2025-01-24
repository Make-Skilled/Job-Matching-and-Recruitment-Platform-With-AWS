// Function to filter companies by name
function filterCompanies() {
  const filter = document.getElementById("filter").value.toLowerCase();
  const companiesList = document.getElementById("companies-list");
  const rows = companiesList.getElementsByTagName("tr");

  for (let i = 0; i < rows.length; i++) {
    const companyName = rows[i].getElementsByTagName("td")[1].textContent.toLowerCase();
    if (companyName.includes(filter)) {
      rows[i].style.display = "";
    } else {
      rows[i].style.display = "none";
    }
  }
}

// Function to add a new company (example, you can modify to add dynamic functionality)
function addCompany() {
  const companiesList = document.getElementById("companies-list");

  const newRow = document.createElement("tr");

  newRow.innerHTML = `
    <td><img src="https://upload.wikimedia.org/wikipedia/commons/e/e9/Amazon_logo.svg" alt="Amazon Logo" class="company-logo"></td>
    <td>Amazon</td>
    <td>2024-07-01</td>
    <td><button class="btn-options">...</button></td>
  `;

  companiesList.appendChild(newRow);
}
