document.addEventListener(
    "DOMContentLoaded",
    function () {

        const fecha =
            document.getElementById("fecha");

        if (fecha) {

            const hoy = new Date();

            const fechaFormateada =
                new Intl.DateTimeFormat(
                    "es-AR",
                    {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric"
                    }
                ).format(hoy);

            fecha.textContent =
                fechaFormateada;

        }

    }
);