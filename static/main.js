const jobSearchInput = document.getElementById('job-search');
const suggestionsList = document.getElementById('suggestions');
const searchBtn = document.getElementById('search-btn');

// Sample job titles for suggestions and validation
const jobTitles = [
    'Software Engineer',
    'Data Analyst',
    'Product Manager',
    'Graphic Designer',
    'Web Developer',
    'UI/UX Designer',
    'Database Administrator',
    'Network Engineer',
    'Systems Analyst',
    'Marketing Specialist',
    'Python Developer'
];

// Function to display suggestions based on input
function showSuggestions(value) {
    // Clear previous suggestions
    suggestionsList.innerHTML = '';

    if (value.length > 0) {
        // Filter job titles that match the input value
        const filteredJobs = jobTitles.filter(job => 
            job.toLowerCase().includes(value.toLowerCase())
        );

        // Display filtered job titles as suggestions
        filteredJobs.forEach(job => {
            const li = document.createElement('li');
            li.textContent = job;
            li.addEventListener('click', function() {
                jobSearchInput.value = job; // Set clicked suggestion in input field
                suggestionsList.innerHTML = ''; // Clear suggestions after selection
            });
            suggestionsList.appendChild(li);
        });
    }
}

// Listen for input changes to provide suggestions
jobSearchInput.addEventListener('input', function() {
    const searchValue = this.value;
    showSuggestions(searchValue);
});

// Search button click event
searchBtn.addEventListener('click', function() {
    const searchValue = jobSearchInput.value.trim().toLowerCase();

    // Check if the entered search value matches any job title
    const isJobFound = jobTitles.some(job => job.toLowerCase() === searchValue);

    // Get login status from localStorage
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

    if (isJobFound) {
        if (isLoggedIn) {
            // Redirect to job.html if logged in and a matching job is found
            window.location.href = '/job';
        } else {
            // Redirect to browser.html with a login prompt if not logged in
            alert('Please log in to view all new job details. Showing previous job description.');
            window.location.href = '/browser';
        }
    } else {
        // No matching job found
        alert('No matching job found. Please try again later.');
        // Redirect based on login status
        window.location.href = isLoggedIn ? '/job' : '/browser';
    }
});


const track = document.querySelector('.carousel-track');
const items = Array.from(track.children);
const nextButton = document.querySelector('.right-arrow');
const prevButton = document.querySelector('.left-arrow');
const visibleItems = 3; // Adjust this value if you want more/less visible items
const itemWidth = items[0].getBoundingClientRect().width + 10; // Include margin-right

let currentIndex = 0;
const totalItems = items.length;
const maxIndex = totalItems - visibleItems;

// Move the carousel track to show the current items
const moveToItem = (index) => {
    track.style.transform = 'translateX(-' + (index * itemWidth) + 'px)';
};

// Click Right Arrow - Move to Next Items
nextButton.addEventListener('click', () => {
    if (currentIndex === maxIndex) {
        currentIndex = 0; // Loop back to the start
    } else {
        currentIndex++;
    }
    moveToItem(currentIndex);
});

// Click Left Arrow - Move to Previous Items
prevButton.addEventListener('click', () => {
    if (currentIndex === 0) {
        currentIndex = maxIndex; // Loop back to the end
    } else {
        currentIndex--;
    }
    moveToItem(currentIndex);
});

const viewAllBtn = document.getElementById("view-all-btn");
const hiddenCards = document.querySelectorAll(".explore__card.hidden");

viewAllBtn.addEventListener("click", () => {
    hiddenCards.forEach(card => card.classList.toggle("hidden"));

// Change button text based on visibility
if (viewAllBtn.innerText === "View All Categories") {
    viewAllBtn.innerText = "Show Less Categories";
} else {
    viewAllBtn.innerText = "View All Categories";
}
});
const viewjobButton = document.getElementById('view-job-btn');

viewjobButton.addEventListener('click', function() {
    const isLoggedIn = localStorage.getItem('isLoggedIn'); // Check if user is logged in

    if (isLoggedIn === 'true') {
        window.location.href = '/job'; // Redirect if logged in
    } else {
        alert('Please log in to view all jobs.');
        window.location.href = '/login'; // Redirect to login page if not logged in
    }
});
