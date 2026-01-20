const button = document.getElementById("btn");
function changecolour() {
    const coulourchange = ["red", "blue", "green", "navy", "white", "black", "gray", "crimson", "turquoise"]
    const randomcolour = Math.floor(Math.random() * coulourchange.length);
    document.documentElement.style.setProperty('--bg-color', coulourchange[randomcolour]);

}

button.addEventListener("click", changecolour);