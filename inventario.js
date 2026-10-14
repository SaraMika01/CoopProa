document.addEventListener("DOMContentLoaded", () => {
    const buscador = document.getElementById("buscador");
    const listaProductos = document.getElementById("listaProductos");
    const categorias = document.querySelectorAll(".category");
    if (!buscador || !listaProductos) return;

    let categoriaSeleccionada = "Todos";

    function filtrarProductos() {
        const texto = buscador.value.trim().toLocaleLowerCase("es");
        listaProductos.querySelectorAll(".inventory-card").forEach((producto) => {
            const nombre = (producto.dataset.name || "").toLocaleLowerCase("es");
            const categoria = producto.dataset.category || "";
            const coincideTexto = nombre.includes(texto);
            const coincideCategoria = categoriaSeleccionada === "Todos"
                || categoria === categoriaSeleccionada;
            producto.classList.toggle("d-none", !(coincideTexto && coincideCategoria));
        });
    }

    buscador.addEventListener("input", filtrarProductos);
    categorias.forEach((boton) => {
        boton.addEventListener("click", () => {
            categorias.forEach((elemento) => elemento.classList.remove("active"));
            boton.classList.add("active");
            categoriaSeleccionada = boton.dataset.category;
            filtrarProductos();
        });
    });
});
