const ctx = document.getElementById('barChart');
      
const config =  {
  type: 'bar',
  data: {
    labels: libGenres,
    datasets: [{
      label: 'No of Books',
      data: libCounts,
      fill: false,
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
      borderRadius: {
        topLeft: 10,
        topRight: 10,
        bottomLeft: 10,
        bottomRight: 10,
      },
      borderSkipped: false, // Ensures that no borders are skipped
      barThickness: 50,
    }]
  },
  options: {
    // indexAxis: 'y',
    responsive: true,
    scales: {
        x: {
            border: {
                display: false
            },
            grid: {
                display: false
            }
        },
        y: {
            border: {
                display: true
            },
            grid: {
                display: false
            },
            ticks: {
                maxTicksLimit: 5, // Customize the number of ticks on the y-axis
                beginAtZero: true
            },
        }
    },
    plugins: {
      legend: {
          display: false,
          labels: {
            color: 'rgb(255, 99, 132)'
        }
      }
    }
  }
};

new Chart(ctx, config)