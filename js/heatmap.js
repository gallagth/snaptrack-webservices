var slider;
var heatmap;

window.onload = function() {

    slider = $( "#time_slider" );

    slider.slider({
        value:0,
        min: 0,
        max: 23,
        step: 1,
        slide: function( event, ui ) {
            updateHeatmap(ui.value);
        }
    });

    //draw the map
    var mapCanvas = document.getElementById("map");
    var context = mapCanvas.getContext("2d");

    var imageObj = new Image();
    imageObj.onload = function() {
        context.drawImage(imageObj, 0,0);
    };
    imageObj.src = 'images/CE_level4.png';

    // heatmap configuration
    var config = {
        element: document.getElementById("heatmapArea"),
        radius: 30,
        opacity: 50,
        legend: {
            position: 'br',
            title: 'Number of locations'
        }
    };

    //creates and initializes the heatmap
    heatmap = h337.create(config);

    updateHeatmap();
}

function updateHeatmap(sliderValue) {
    if (!sliderValue) {
        sliderValue = getSliderValue();
    }
    //get the selected day
    var day = $("#heatmap_day").val();
    var unix = parseDate(day).getTime()/1000;
    //get starttime
    var startHour = sliderValue;
    console.log(startHour);
    var startTime = unix + startHour*3600;
    var endTime = startTime + 24*3600;
    //data request
    var dataReq = new XMLHttpRequest();
    dataReq.onload = function() {
        var data = JSON.parse(this.responseText);
        var numLocations = data.length;
        var coordinates = [];
        for (var i=0; i<numLocations; i++) {
            coordinates.push({
                x: data[i].x,
                y: data[i].y,
                count: 1});
        }
        heatmap.store.setDataSet({
            max:1,
            data: coordinates
        });
    }
    dataReq.open("get", "/locations/timerange?start_time=" + startTime + "&end_time=" + endTime, true);
    dataReq.send();
}

function generateRandomData() {
    var max = (Math.random()*100+1) >> 0,
    data = [],
    length = 200,
    width = heatmap.get("width"),
    height = heatmap.get("height");

    while(length--){
        data.push({
            x: (Math.random()*width) >> 0,
            y: (Math.random()*height) >> 0,
            count: (Math.random()*max) >> 0
        });
    }

    return {
        max: max,
        data: data
    };
}

// parse a date in d_m_Y format
function parseDate(input) {
  var parts = input.split('_');
  // new Date(year, month [, day [, hours[, minutes[, seconds[, ms]]]]])
  return new Date(parts[2], parts[1]-1, parts[0]); // Note: months are 0-based
}

function getSliderValue() {
    var value = slider.slider("option", "value");
    console.log("getslidervalue " + value);
    return value;
}

