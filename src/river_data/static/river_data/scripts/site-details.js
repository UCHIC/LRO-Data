const EXTENT_HOURS = 24;
const GAP_HOURS = 6;
const STALE_DATA_CUTOFF = new Date(new Date() - 1000 * 60 * 60 * EXTENT_HOURS);

function initMap() {
    let latitude = parseFloat(document.querySelector('div.map-container input#site-latitude').value);
    let longitude = parseFloat(document.querySelector('div.map-container input#site-longitude').value);
    let site_position = { lat: latitude, lng: longitude };

    let map = new google.maps.Map(document.getElementById('map'), {
        zoom: 17,
        center: site_position,
        mapTypeId: 'terrain'
    });
    let marker = new google.maps.Marker({position: site_position, map: map});
}

function getTimeSeriesData(sensorInfo) {
    if (!sensorInfo['influxUrl']) {return;}
    $.ajax({
        url: sensorInfo['influxUrl']
    }).done(function(influx_data) {
        var resultSet = influx_data.results ? influx_data.results.shift() : null;
        if (resultSet && resultSet.series && resultSet.series.length) {
            var influxSeries = resultSet.series.shift();
            var indexes = {
                time: influxSeries.columns.indexOf("time"),
                value: influxSeries.columns.indexOf("DataValue"),
                offset: influxSeries.columns.indexOf("UTCOffset")
            };
            var values = influxSeries.values.map(function(influxValue) {
                return {
                    DateTime: influxValue[indexes.time].match(/^(\d{4}\-\d\d\-\d\d([tT][\d:]*)?)/).shift(),
                    Value: influxValue[indexes.value],
                    TimeOffset: influxValue[indexes.offset]
                }
            });

            // fillValueTable($('table.data-values[data-result-id=' + sensorInfo['resultId'] + ']'), values);
            // drawSparklineOnResize(sensorInfo, values);
            drawSparklinePlot(sensorInfo, values);
        } else {
            console.log('No data values were found for this site');
            drawSparklinePlot(sensorInfo, []);  // Will just render the empty message
            // console.info(series.getdatainflux);
        }
    }).fail(function() {
        drawSparklinePlot(sensorInfo, []);  // Will just render the empty message
        console.log('data failed to load.');
    });
}

function drawSparklinePlot(seriesInfo, seriesData) {
    var card = $('div.plot_box[data-id="' + seriesInfo['id'] + '"]');
    var plotBox = card.find(".graph-container");

    plotBox.empty();

    var margin = {top: 5, right: 1, bottom: 5, left: 1};
    var width = plotBox.width() - margin.left - margin.right;
    var height = plotBox.height() - margin.top - margin.bottom;

    if (seriesData.length === 0) {
        card.find(".tsa-trigger").toggleClass("disabled", true);

        // Append message when there is no data
        d3.selectAll(plotBox.get(0)).append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("text")
                .text("No data exist for this variable.")
                .attr("font-size", "12px")
                .attr("fill", "#AAA")
                .attr("text-anchor", "left")
                .attr("transform", "translate(" + (margin.left + 10) + "," + (margin.top + 20) + ")");
        return;
    }

    seriesData.forEach(function(value){
        value.RealDateTime = new Date(value.DateTime)
    });

    var lastRead = getMax(seriesData);

    card.find('span.last-observation').text(lastRead.DateTime);
    card.find('h3.last-value').text(lastRead.Value);


    var dataTimeOffset = getMin(seriesData.map(function(value){
        return value.RealDateTime;
    }));

    var xAxis = d3.scaleTime().range([0, width]);
    var yAxis = d3.scaleLinear().range([height, 0]);

    var yDomain = d3.extent(seriesData, function(d) {
        return parseFloat(d.Value);
    });
    var yPadding = (yDomain[1] - yDomain[0]) / 20;  // 5% padding
    yDomain[0] -= yPadding;
    yDomain[1] += yPadding;

    xAxis.domain([dataTimeOffset, lastRead.RealDateTime]);
    yAxis.domain(yDomain);

    var line = d3.line()
        .x(function(d) {
            var date = new Date(d.DateTime);
            return xAxis(date);
        })
        .y(function(d) {
            return yAxis(d.Value);
        });

    var svg = d3.select(plotBox.get(0)).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("class", function() {
            if (lastRead.RealDateTime <= STALE_DATA_CUTOFF) {
                return "stale";
            }

            return "not-stale";
        })
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Rendering the paths
    var gapOffset;  // The minimum date required before being considered a gap.
    var previousDate;
    var start = 0;  // Latest start detected after a gap. Initially set to the start of the list.
    var paths = [];

    for (var i = 0; i < seriesData.length; i++) {
        var currentDate = new Date(seriesData[i].DateTime);

        if (previousDate) {
            gapOffset = new Date(currentDate - 1000 * 60 * 60 * GAP_HOURS);
        }

        if (previousDate && previousDate < gapOffset) {
            paths.push(seriesData.slice(start, i));
            start = i;
        }
        previousDate = currentDate;
    }

    if (start > 0) {
        paths.push(seriesData.slice(start, seriesData.length));
    }
    else {
        paths.push(seriesData); // No gaps were detected. Just plot the entire original data.
    }

    // Plot all paths separately to display gaps between them.
    for (var i = 0; i < paths.length; i++) {
        if (paths[i].length == 1) {
            svg.append("circle")
                .attr("r", 2)
                .style("fill", "steelblue")
                .attr("transform", "translate(" + xAxis(new Date(paths[i][0].DateTime)) + ", " + yAxis(paths[i][0].Value) + ")")
        }
        else {
            svg.append("path")
            .data([paths[i]])
            .attr("class", "line").attr("d", line)
            .attr("stroke", "steelblue");
        }
    }
}

$(document).ready(function () {
    var variables = document.querySelectorAll('.plot_box');
    for (var index = 0; index < variables.length; index++) {
        var variableDataset = variables[index].dataset;
        getTimeSeriesData(variableDataset);
    }

    $('[data-toggle="tooltip"]').tooltip()
});

function getMax(arr) {
    let len = arr.length;
    let max = {'RealDateTime': -Infinity};

    while (len--) {
        max = arr[len].RealDateTime > max.RealDateTime ? arr[len] : max;
    }
    return max;
}

function getMin(arr) {
    let len = arr.length;
    let min = Infinity;

    while (len--) {
        min = arr[len] < min ? arr[len] : min;
    }
    return min;
}