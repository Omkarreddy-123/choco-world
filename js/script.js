// Define the images to switch to
const images = [
    "../images/CrispyCarrie_sq_bar_wBite_1000_ffe5650b-6e98-4e42-9a65-05b1c371a882.png",
    "../images/tabel10.png", // Replace with your next image path
    "../images/another-image-2.png"  // Replace with your next image path
];
let currentImageIndex = 0;

document.getElementById("arrow").addEventListener("click", function() {
    // Update the image to the next one in the array
    currentImageIndex = (currentImageIndex + 1) % images.length;
    document.getElementById("collection2").src = images[currentImageIndex];
});