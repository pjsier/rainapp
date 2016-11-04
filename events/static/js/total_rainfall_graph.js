function drawTotalRainfall(graphDetails) {
    Highcharts.chart('totalRainfallGraph', {
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: 'Rainfall'
        },
        xAxis: [{
            categories: graphDetails.time_list,
            crosshair: true
        }],
        yAxis: [{ // Primary yAxis
            title: {
                text: 'Hourly Rainfall (inches)',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            }
        }, { // Secondary yAxis
            title: {
                text: 'Cumulative Rainfall (inches)',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            opposite: true
        }],
        tooltip: {
            shared: true
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            x: 120,
            verticalAlign: 'top',
            y: 100,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
        },
        series: [{
            name: 'Hourly',
            type: 'column',
            yAxis: 1,
            data: graphDetails.hourly_rainfall,
            tooltip: {
                valueSuffix: ' inches'
            }

        }, {
            name: 'Cumulative',
            type: 'spline',
            data: graphDetails.cumulative_rain,
            tooltip: {
                valueSuffix: ' inches'
            }
        }]
    });
}