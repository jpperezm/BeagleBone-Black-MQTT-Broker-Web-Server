var socket = io.connect('http://' + document.domain + ':' + location.port);

document.getElementById('autonomousToggle').addEventListener('change', function() {
    var message = this.checked ? 'ON' : 'OFF';
    socket.emit('send_mqtt_toggle', { topic: 'esp32/sleep', message: message });
});

document.getElementById('sendUpButton').addEventListener('click', function() {
    socket.emit('send_mqtt_message', { topic: 'esp32/autoshutter', message: 'UP' });
});

document.getElementById('sendDownButton').addEventListener('click', function() {
    socket.emit('send_mqtt_message', { topic: 'esp32/autoshutter', message: 'DOWN' });
});

document.getElementById('sendStopButton').addEventListener('click', function() {
    socket.emit('send_mqtt_message', { topic: 'esp32/autoshutter', message: 'STOP' });
});

var ctx = document.getElementById('mqttChart').getContext('2d');

var darkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
var chartBackgroundColor, chartBorderColor;

if (darkMode) {
    chartBackgroundColor = 'rgba(255, 255, 255, 0.2)';
    chartBorderColor = '#297681';
} else {
    chartBackgroundColor = 'rgba(0, 123, 255, 0.2)';
    chartBorderColor = '#074a54';
}

var mqttChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Light Value',
            backgroundColor: chartBackgroundColor,
            borderColor: chartBorderColor,
            data: []
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                display: true,
                text: 'Tiempo'
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Nivel de luz (%)'
                }
            }
        }
    }
});

socket.on('mqtt_update', function(data) {
    // Añadir la hora actual al eje X
    mqttChart.data.labels.push(new Date().toLocaleTimeString()); 

    // Añadir el valor del mensaje MQTT al eje Y
    mqttChart.data.datasets.forEach((dataset) => {
        dataset.data.push(data.message);
    });

    var screenWidth = window.innerWidth;
    var maxPoints = 20;

    if (screenWidth >= 600) {
        maxPoints = 20;
    } else {
        maxPoints = 7; // cambiar
    }

    // Mantener un número limitado de puntos en el gráfico
    if (mqttChart.data.labels.length >= maxPoints) {
        mqttChart.data.labels.shift();
        mqttChart.data.datasets.forEach((dataset) => {
            dataset.data.shift();
        });
    }

    mqttChart.update();
});