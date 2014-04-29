window.onload = function() {
    
    updateDayPlot();

    $("<div id='tooltip'></div>").css({
        position: "absolute",
        display: "none",
        border: "1px solid #fdd",
        padding: "2px",
        "background-color": "#fee",
        opacity: 0.80
    }).appendTo("body");

    $("#placeholder").bind("plothover", function (event, pos, item) {
        if (item) {
            var timestamp = new Date(item.datapoint[0]);
            var y = item.datapoint[1].toFixed(2);
            var string = timestamp.toUTCString() + "," + y;
            $("#tooltip").html(string)
            .css({top: item.pageY+5, left: item.pageX+5})
            .fadeIn(200);
        } else {
            $("#tooltip").hide();
        }
    });
}

function plotBarData(toPlot) {
    var plot = $.plot("#placeholder", [
        { data: toPlot, label: ""},
    ], {
        series: {
            lines: {
                show: true
            },
            points: {
                show: true
            }
        },
        xaxis: {
            mode: "time",
            tickLength: 5
        },
        grid: {
            hoverable: true,
            clickable: true
        }
    });
}

function updateDayPlot() {
    var startDayUnix = parseDate($("#start_day_dropdown").val()).getTime()/1000;
    var endDayUnix = parseDate($("#end_day_dropdown").val()).getTime()/1000;
    var dataReq = new XMLHttpRequest();
    dataReq.onload = function() {
        var data = JSON.parse(this.responseText);
        if (data.length == 0) {
            return;
        }
        var numScans = data.length;
        var points = [];
        var dataIdx = 0, currentBin = 0;
        for (var timeIndex = startDayUnix; timeIndex < endDayUnix; timeIndex+=3600) {
            var upperBound = timeIndex + 3600;
            if (dataIdx < data.length) {
                var dataTime = data[dataIdx].time/1000;
                while (timeIndex <= dataTime && dataTime < upperBound && dataIdx < data.length) {
                    currentBin++;
                    dataTime = data[dataIdx].time/1000;
                    dataIdx++;
                }
                points.push([timeIndex*1000, currentBin]);
                currentBin = 0;
            }
        }
        plotBarData(points);
    }
    dataReq.open("get", "/scans/range?start_time=" + startDayUnix + "&end_time=" + endDayUnix, true);
    dataReq.send();
}

// parse a date in d_m_Y format
function parseDate(input) {
  var parts = input.split('_');
  // new Date(year, month [, day [, hours[, minutes[, seconds[, ms]]]]])
  return new Date(parts[2], parts[1]-1, parts[0]); // Note: months are 0-based
}
