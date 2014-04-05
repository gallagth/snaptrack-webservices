window.onload = function() {
    
    var normal = [];
    for (var i = 0; i < 24; i += 0.25) {
        normal.push([i, normalDistribSample(i,9,1)]);
    }

    xticks = [];
    for (var i=0; i< 24; i += 2) {
        xticks.push(i.toFixed(0));
    }

    var plot = $.plot("#placeholder", [
    { data: normal, label: "Monday"},
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
            ticks: xticks
        },
        grid: {
            hoverable: true,
            clickable: true
        }
    });

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
            y = item.datapoint[1].toFixed(2);

            $("#tooltip").html(y)
            .css({top: item.pageY+5, left: item.pageX+5})
            .fadeIn(200);
        } else {
            $("#tooltip").hide();
        }
    });

}

function normalDistribSample(x, mean, std) {

    return Math.exp(-(x-mean)*(x-mean)/(2*std*std))/(std*Math.sqrt(2*Math.PI));

}
