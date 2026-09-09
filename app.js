/* =========================================
   ESPERAR A QUE CARGUE EL DOCUMENTO
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {


        /* =====================================
           BUSCAR ELEMENTO DE FECHA
        ===================================== */

        const fecha =
            document.getElementById("fecha");


        /* =====================================
           SI EXISTE EL ELEMENTO
        ===================================== */

        if (fecha) {


            /* Obtener fecha actual */

            const hoy = new Date();


            /* Formato argentino */

            const fechaFormateada =
                new Intl.DateTimeFormat(
                    "es-AR",
                    {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric"
                    }
                ).format(hoy);


            /* Mostrar fecha */

            fecha.textContent =
                fechaFormateada;

        }

    }
);