const ctx2 = document.getElementById('donutChart');

const data = {
    labels: wishlistGenres,
    datasets: [{
        label: 'No of Books',
        data: wishlistCounts,
        backgroundColor: [
            'rgba(255, 99, 132, 0.2)',
            'rgba(255, 159, 64, 0.2)',
            'rgba(255, 205, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(201, 203, 207, 0.2)'
          ],
          borderColor: [
            'rgb(255, 99, 132)',
            'rgb(255, 159, 64)',
            'rgb(255, 205, 86)',
            'rgb(75, 192, 192)',
            'rgb(54, 162, 235)',
            'rgb(153, 102, 255)',
            'rgb(201, 203, 207)'
          ],
          borderWidth: 1,
        hoverOffset: 10
    }],
};

const configDonut = {
    type: 'doughnut',
    data: data,
    options: {
        maintainAspectRatio: false, // Allows more control over chart size and spacing
        aspectRatio: 1.05, 
        layout: {
            padding: 20 // Adds padding around the entire chart area
        },
        plugins: {
            legend: {
                position: 'right',
                align: 'center', // Aligns the legend vertically in the middle
                labels: {
                    padding: 20, // Adds padding between legend items and the chart
                    usePointStyle: true, // Use point style instead of rectangle for legend indicators
                    pointStyle: 'circle', // Set the legend indicator style to circles
                }
            }
        }
    }
};

new Chart(ctx2, configDonut)