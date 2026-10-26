(() => {

    const root =
        document.querySelector(
            "[data-temperature-chart]"
        );

    if (!root) {
        return;
    }


    const canvas =
        root.querySelector(
            "[data-temperature-canvas]"
        );

    if (
        !canvas
        || typeof Chart === "undefined"
    ) {
        return;
    }


    const endpoint =
        root.dataset.temperatureEndpoint;

    const labelCpuTemp =
        root.dataset.labelCpuTemp
        || "CPU";

    const labelEcholink =
        root.dataset.labelEcholink
        || "EchoLink";

    const labelReflector =
        root.dataset.labelReflector
        || "Reflector";

    let chart = null;
    let currentRangeHours = 24;


    function buildChart(
        samples
    ) {

        const labels =
            samples.map(
                (sample) => sample.timestamp
            );

        const cpuTempData =
            samples.map(
                (sample) => sample.cpu_temp
            );

        const echolinkData =
            samples.map(
                (sample) =>
                    sample.echolink_connection_count
            );

        const reflectorData =
            samples.map(
                (sample) =>
                    sample.reflector_connection_count
            );

        const datasets = [
            {
                label: labelCpuTemp,
                data: cpuTempData,
                borderColor: "#e67e22",
                backgroundColor:
                    "rgba(230, 126, 34, 0.15)",
                yAxisID: "temperature",
                tension: 0.2,
                pointRadius: 0,
                borderWidth: 2,
                fill: true,
            },
            {
                label: labelEcholink,
                data: echolinkData,
                borderColor: "#2980b9",
                yAxisID: "activity",
                stepped: true,
                pointRadius: 0,
                borderWidth: 1.5,
            },
            {
                label: labelReflector,
                data: reflectorData,
                borderColor: "#8e44ad",
                yAxisID: "activity",
                stepped: true,
                pointRadius: 0,
                borderWidth: 1.5,
            },
        ];

        if (chart) {
            chart.destroy();
        }

        chart = new Chart(
            canvas,
            {
                type: "line",
                data: {
                    labels,
                    datasets,
                },
                options: {
                    animation: false,
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: "index",
                        intersect: false,
                    },
                    scales: {
                        x: {
                            ticks: {
                                maxTicksLimit: 8,
                            },
                        },
                        temperature: {
                            type: "linear",
                            position: "left",
                            title: {
                                display: true,
                                text: "°C",
                            },
                        },
                        activity: {
                            type: "linear",
                            position: "right",
                            beginAtZero: true,
                            grid: {
                                drawOnChartArea: false,
                            },
                            ticks: {
                                precision: 0,
                            },
                        },
                    },
                },
            }
        );
    }


    async function load(
        hours
    ) {

        try {

            const response =
                await fetch(
                    `${endpoint}?hours=${hours}`,
                    {
                        cache: "no-store",
                        headers: {
                            "Accept":
                                "application/json",
                        },
                    }
                );

            if (!response.ok) {

                throw new Error(
                    `HTTP ${response.status}`
                );
            }

            const data =
                await response.json();

            buildChart(
                data.samples || []
            );

        } catch (error) {

            /*
             * Keep whatever was last rendered. A temporary
             * network failure must not blank the chart.
             */

        }
    }


    root.querySelectorAll(
        "[data-temperature-range]"
    ).forEach(
        (button) => {

            button.addEventListener(
                "click",
                () => {

                    root.querySelectorAll(
                        "[data-temperature-range]"
                    ).forEach(
                        (other) => {

                            other.classList.remove(
                                "active"
                            );
                        }
                    );

                    button.classList.add(
                        "active"
                    );

                    currentRangeHours =
                        Number(
                            button.dataset
                                .temperatureRange
                        ) || 24;

                    load(
                        currentRangeHours
                    );
                }
            );
        }
    );


    load(
        currentRangeHours
    );

})();
