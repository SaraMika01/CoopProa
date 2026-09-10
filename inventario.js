document.addEventListener(
    "DOMContentLoaded",
    function () {


        const buscador =
            document.getElementById("buscador");


        const listaProductos =
            document.getElementById("listaProductos");


        const categorias =
            document.querySelectorAll(".category");


        const formulario =
            document.getElementById("formProducto");

        let categoriaSeleccionada =
            "Todos";

        function filtrarProductos() {

            const texto =
                buscador.value
                    .trim()
                    .toLowerCase();

            const productos =
                listaProductos.querySelectorAll(
                    ".inventory-card"
                );

            productos.forEach(
                function (producto) {

                    const nombre =
                        producto.dataset.name
                            .toLowerCase();

                    const categoria =
                        producto.dataset.category;

                    const coincideTexto =
                        nombre.includes(texto);

                    const coincideCategoria =
                        categoriaSeleccionada ===
                            "Todos"
                        ||
                        categoria ===
                            categoriaSeleccionada;

                    if (
                        coincideTexto &&
                        coincideCategoria
                    ) {

                        producto.classList.remove(
                            "d-none"
                        );

                    } else {

                        producto.classList.add(
                            "d-none"
                        );

                    }

                }
            );

        }

        if (buscador) {

            buscador.addEventListener(
                "input",
                filtrarProductos
            );

        }

        categorias.forEach(
            function (boton) {


                boton.addEventListener(
                    "click",
                    function () {

                        categorias.forEach(
                            function (elemento) {

                                elemento.classList.remove(
                                    "active"
                                );

                            }
                        );

                        boton.classList.add(
                            "active"
                        );

                        categoriaSeleccionada =
                            boton.dataset.category;

                        filtrarProductos();

                    }
                );

            }
        );


        if (listaProductos) {


            listaProductos.addEventListener(
                "click",
                function (evento) {


                    /* Buscar botón */

                    const boton =
                        evento.target.closest(
                            ".qty-btn"
                        );


                    /* Si no es botón */

                    if (!boton) {

                        return;

                    }


                    /* Buscar tarjeta */

                    const tarjeta =
                        boton.closest(
                            ".inventory-card"
                        );


                    /* Buscar cantidad */

                    const cantidadTexto =
                        tarjeta.querySelector(
                            ".qty-value"
                        );


                    const cantidadReal =
                        tarjeta.querySelector(
                            ".quantity"
                        );


                    /* Convertir a número */

                    let cantidad =
                        Number(
                            cantidadTexto.textContent
                        );


                    /* SUMAR */

                    if (
                        boton.classList.contains(
                            "plus"
                        )
                    ) {

                        cantidad++;

                    }


                    /* RESTAR */

                    if (
                        boton.classList.contains(
                            "minus"
                        )
                    ) {

                        cantidad =
                            Math.max(
                                0,
                                cantidad - 1
                            );

                    }


                    /* Actualizar pantalla */

                    cantidadTexto.textContent =
                        cantidad;


                    cantidadReal.textContent =
                        cantidad;

                }
            );

        }



        /* =====================================
           AGREGAR PRODUCTO
        ===================================== */

        if (formulario) {


            formulario.addEventListener(
                "submit",
                function (evento) {


                    /* Evitar recargar página */

                    evento.preventDefault();


                    /* Obtener datos */

                    const nombre =
                        document.getElementById(
                            "nombreProducto"
                        ).value.trim();


                    const categoria =
                        document.getElementById(
                            "categoriaProducto"
                        ).value;


                    const precio =
                        Number(
                            document.getElementById(
                                "precioProducto"
                            ).value
                        );


                    /* Crear tarjeta */

                    const producto =
                        document.createElement(
                            "article"
                        );


                    producto.className =
                        "inventory-card";


                    /* Guardar datos */

                    producto.dataset.name =
                        nombre;


                    producto.dataset.category =
                        categoria;


                    /* Crear contenido */

                    producto.innerHTML = `

                        <div class="product-icon sandwich">
                            📦
                        </div>

                        <div class="product-info">

                            <div class="product-heading">

                                <h2>
                                    ${nombre}
                                </h2>

                            </div>

                            <p>
                                ${categoria}
                                •
                                $${precio.toLocaleString("es-AR")}
                            </p>

                            <hr>

                            <span>
                                Cantidad:

                                <strong class="quantity">
                                    0
                                </strong>

                            </span>

                        </div>

                        <div class="quantity-control">

                            <button
                                class="qty-btn minus">

                                −

                            </button>

                            <span class="qty-value">
                                0
                            </span>

                            <button
                                class="qty-btn plus">

                                +

                            </button>

                        </div>

                    `;


                    /* Agregar producto */

                    listaProductos.appendChild(
                        producto
                    );


                    /* Limpiar formulario */

                    formulario.reset();


                    /* Cerrar modal */

                    const modal =
                        document.getElementById(
                            "productoModal"
                        );


                    if (modal) {

                        const instancia =
                            bootstrap.Modal
                                .getInstance(modal);


                        if (instancia) {

                            instancia.hide();

                        }

                    }


                    /* Aplicar filtros */

                    filtrarProductos();

                }
            );

        }

    }
);