document.addEventListener("DOMContentLoaded", function() {
    const btn = document.getElementById("myButton");
    btn.addEventListener("click", async () => {
        const response = await fetch("/your-django-endpoint/");
        const data = await response.json();
        console.log(data);
    });
});
