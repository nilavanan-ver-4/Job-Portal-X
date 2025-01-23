document.addEventListener("DOMContentLoaded", () => {
    // Select all job category cards
    const jobCards = document.querySelectorAll(".category-card");

    // Create a modal container
    const modal = document.createElement("div");
    modal.style.display = "none"; // Initially hidden
    modal.style.position = "fixed";
    modal.style.top = "0";
    modal.style.left = "0";
    modal.style.width = "100%";
    modal.style.height = "100%";
    modal.style.backgroundColor = "rgba(0, 0, 0, 0.6)";
    modal.style.zIndex = "1000";
    modal.style.overflowY = "auto";
    document.body.appendChild(modal);

    const modalContent = document.createElement("div");
    modalContent.style.maxWidth = "600px";
    modalContent.style.margin = "50px auto";
    modalContent.style.backgroundColor = "#ffffff";
    modalContent.style.borderRadius = "8px";
    modalContent.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
    modalContent.style.padding = "20px";
    modalContent.style.position = "relative";
    modal.appendChild(modalContent);

    // Add close button
    const closeButton = document.createElement("span");
    closeButton.innerHTML = "&times;";
    closeButton.style.position = "absolute";
    closeButton.style.top = "10px";
    closeButton.style.right = "20px";
    closeButton.style.fontSize = "24px";
    closeButton.style.cursor = "pointer";
    modalContent.appendChild(closeButton);

    closeButton.addEventListener("click", () => {
        modal.style.display = "none"; // Close the modal
    });

    // Add event listener to each card
    jobCards.forEach((card) => {
        card.addEventListener("click", () => {
            // Get the category name from the card
            const categoryName = card.querySelector("h3").innerText;

            // Update modal content dynamically
            modalContent.innerHTML = `
                <span style="position: absolute; top: 10px; right: 20px; font-size: 24px; cursor: pointer; color: #333; font-weight: bold;">&times;</span>
<h2 style="text-align: center; color: #007BFF; margin-bottom: 20px;">Job Application Form for ${categoryName}</h2>
<form id="jobApplicationForm" method=("GET","POST") enctype="multipart/form-data" action="{{ url_for('apply') }}" style="background-color: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="name" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Full Name</label>
        <input type="text" id="name" name="name" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;">
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="email" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Email</label>
        <input type="email" id="email" name="email" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;">
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="phone" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Phone</label>
        <input type="text" id="phone" name="phone" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;">
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="age" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Age</label>
        <input type="number" id="age" name="age" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;">
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="sex" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Sex</label>
        <select id="sex" name="sex" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;">
            <option value="M">Male</option>
            <option value="F">Female</option>
            <option value="O">Other</option>
        </select>
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="address" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Address</label>
        <textarea id="address" name="address" rows="3" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;"></textarea>
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="highest_qualification" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Highest Qualification</label>
        <input type="text" id="highest_qualification" name="highest_qualification" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;">
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="experience" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Experience (years)</label>
        <input type="number" id="experience" name="experience" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;">
    </div>
    <div class="form-group" style="margin-bottom: 15px;">
        <label for="skills" style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">Skills</label>
        <textarea id="skills" name="skills" rows="3" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; transition: border-color 0.3s ease;"></textarea>
    </div>

    <!-- Hidden field for categoryName -->
    <input type="hidden" id="categoryName" name="categoryName" value="${categoryName}">
    
    <button type="submit" style="display: block; width: 100%; padding: 12px 0; font-size: 1.1em; color: #fff; background-color: #007BFF; border: none; border-radius: 8px; cursor: pointer; transition: background-color 0.3s ease; text-transform: uppercase;">Submit Application</button>
</form>
            `;

            // Re-add close button event listener
            const modalCloseButton = modalContent.querySelector("span");
            modalCloseButton.addEventListener("click", () => {
                modal.style.display = "none"; // Close the modal
            });

            // Display the modal
            modal.style.display = "block";

            // Add an event listener for form submission
            const form = document.getElementById("jobApplicationForm");
            form.addEventListener("submit", (event) => {
                event.preventDefault(); // Prevent default form submission

                // Use fetch API or AJAX to send data to the server without refreshing
                fetch("/apply", {
                    method: "POST",
                    body: new FormData(form),
                })
                    .then(response => console.log(response.json()))
                // .then(data => {
                //     if (data.success) {
                //         alert("Application submitted successfully!");
                //         modal.style.display = "none"; // Hide the modal after submission
                //         form.reset(); // Reset the form fields
                //         window.location.href = "/thank_you";
                //     } else {
                //         alert("Error submitting application: " + data.message);
                //     }
                // })
                // .catch(error => {

                //     alert("Application submitted successfully!",error);
                //     window.location.href = "/thank_you";
                // });
            });
        });
    });
});
