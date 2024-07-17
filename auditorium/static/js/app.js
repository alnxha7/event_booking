document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to the booking form submission
    var bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

            // Get the URL from the form action attribute
            var url = bookingForm.getAttribute('action');
            
            // Redirect to the calendar page for booking
            window.location.href = url;
        });
    }
});