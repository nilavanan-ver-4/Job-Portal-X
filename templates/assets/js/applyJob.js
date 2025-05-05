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

            modalContent.innerHTML = `
            <span style="position: absolute; top: 10px; right: 20px; font-size: 24px; cursor: pointer; color: #333; font-weight: bold;">×</span>
            <h2 style="text-align: center; color: #007BFF; margin-bottom: 20px;">Job Application Form for ${categoryName}</h2>
            <form id="jobApplicationForm" method="POST" action="{{ url_for('apply') }}" style="background-color: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
                <!-- Other form fields -->
                <input type="hidden" id="category_id" name="category_id" value="${category.id}">
                <!-- Rest of the form -->
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
