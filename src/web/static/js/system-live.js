(() => {

    const root =
        document.querySelector(
            "[data-system-live]"
        );

    if (!root) {
        return;
    }


    const endpoint =
        root.dataset.systemEndpoint;

    const notAvailable =
        root.dataset.notAvailable || "N/A";

    const REFRESH_INTERVAL = 5000;

    let refreshTimer = null;


    function numericValue(value) {

        const number =
            Number(value);

        return Number.isFinite(number)
            ? number
            : 0;
    }


    function setValue(
        key,
        value
    ) {

        root.querySelectorAll(
            `[data-system-value="${key}"]`
        ).forEach(
            (element) => {

                element.textContent =
                    value;

            }
        );
    }


    function setProgress(
        key,
        value
    ) {

        const percent =
            Math.max(
                0,
                Math.min(
                    100,
                    numericValue(value)
                )
            );


        root.querySelectorAll(
            `[data-system-progress="${key}"]`
        ).forEach(
            (element) => {

                element.style.width =
                    `${percent}%`;

                element.setAttribute(
                    "aria-valuenow",
                    percent.toFixed(1)
                );


                element.classList.remove(
                    "bg-success",
                    "bg-warning",
                    "bg-danger"
                );


                if (percent >= 90) {

                    element.classList.add(
                        "bg-danger"
                    );

                } else if (percent >= 75) {

                    element.classList.add(
                        "bg-warning"
                    );

                } else {

                    element.classList.add(
                        "bg-success"
                    );

                }

            }
        );
    }


    function render(
        data
    ) {

        if (
            typeof data.hostname === "string"
            && data.hostname
        ) {

            setValue(
                "hostname",
                data.hostname
            );
        }


        if (
            typeof data.uptime === "string"
            && data.uptime
        ) {

            setValue(
                "uptime",
                data.uptime
            );
        }


        const cpuTemp =
            numericValue(
                data.cpu_temp
            );

        setValue(
            "cpu_temp",
            cpuTemp > 0
                ? `${cpuTemp.toFixed(1)} °C`
                : notAvailable
        );


        const metrics = [
            "cpu_usage",
            "ram_usage",
            "disk_usage"
        ];


        metrics.forEach(
            (key) => {

                const value =
                    numericValue(
                        data[key]
                    );

                setValue(
                    key,
                    `${value.toFixed(1)} %`
                );

                setProgress(
                    key,
                    value
                );

            }
        );
    }


    function scheduleNext() {

        clearTimeout(
            refreshTimer
        );

        refreshTimer =
            window.setTimeout(
                refresh,
                REFRESH_INTERVAL
            );
    }


    async function refresh() {

        if (document.hidden) {
            return;
        }


        try {

            const response =
                await fetch(
                    endpoint,
                    {
                        cache: "no-store",
                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            if (!response.ok) {
                throw new Error(
                    `HTTP ${response.status}`
                );
            }


            const data =
                await response.json();

            render(
                data
            );

        } catch (error) {

            /*
             * Keep the last valid values visible.
             * A temporary network/API failure must not
             * blank or disturb the dashboard.
             */

        } finally {

            if (!document.hidden) {
                scheduleNext();
            }

        }
    }


    document.addEventListener(
        "visibilitychange",
        () => {

            clearTimeout(
                refreshTimer
            );


            if (!document.hidden) {

                refresh();

            }

        }
    );


    /*
     * Do not fetch immediately.
     * Initial values are already server-rendered.
     */
    scheduleNext();

})();
