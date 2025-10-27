document.addEventListener("DOMContentLoaded", () => {
    const gearIcon = document.querySelector(".gear-icon");
    const menu = document.querySelector(".context-menu");
    // Show context menu at click position
    function showMenu(x, y) {
        // Make visible to get dimensions
        menu.style.display = "flex";
        menu.style.position = "fixed";
        menu.style.opacity = "0";
        menu.classList.add("show");

        // Wait one frame so DOM updates before measuring
        requestAnimationFrame(() => {
            const rect = menu.getBoundingClientRect();
            let newX = x + 5;
            let newY = y + 5;

            // Keep inside viewport
            if (newX + rect.width > window.innerWidth) {
                newX = window.innerWidth - rect.width - 10;
            }
            if (newY + rect.height > window.innerHeight) {
                newY = window.innerHeight - rect.height - 10;
            }

            menu.style.left = `${newX}px`;
            menu.style.top = `${newY}px`;
            menu.style.opacity = "1";
        });
    }

    // Left-click on gear icon
    gearIcon.addEventListener("click", (event) => {
        event.stopPropagation();
        loadMenuContent();
        const isVisible = menu.classList.contains("show");
        document.querySelectorAll(".context-menu.show").forEach((m) => m.classList.remove("show"));

        if (!isVisible) showMenu(event.clientX, event.clientY);
    });

    // Right-click anywhere
    document.addEventListener("contextmenu", (event) => {
        event.preventDefault();
        showMenu(event.clientX, event.clientY);
    });

    // Click outside closes menu
    document.addEventListener("click", (event) => {
        if (!menu.contains(event.target) && !gearIcon.contains(event.target)) {
            menu.classList.remove("show");
            menu.style.display = "none";
        }
    });
});
