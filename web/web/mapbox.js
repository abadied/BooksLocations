mapboxgl.accessToken = 'pk.eyJ1IjoiYW1pdHVyOTEiLCJhIjoiY2pvbzhkeHN1MGx0ZzNwbHd6cmVkMXFiMyJ9.pXauUkubGnbAUaewUAJ42Q';
const map = new mapboxgl.Map({
container: 'map',
style: 'mapbox://styles/amitur91/cjpl9tkca0qru2sryt2p06f2d',
center: [-90.405077, 24.283965],
zoom: 1.0
});


// Holds visible books features for filtering
var books = [];
var popup = new mapboxgl.Popup({});
var last_line = "0";

var filterEl = document.getElementById('feature-filter');
var listingEl = document.getElementById('feature-listing');

var filterYears1 = document.getElementById('years-after');
var filterYears1 = document.getElementById('years-before');

function showPopAndLine(feature_) {
    var popup_html = ' <div class="left-half">' +
        '<img src="' +
        feature_.properties.cover_url +
        '" onerror="this.onerror=null;this.src="./no_cover.jpg";" /></div>' +
        '<div class="right-half">' +
        '<h3>' +
        feature_.properties.title +
        '</h3>' +
        feature_.properties.author +
        '<img  style="float:right;" src="http://covers.openlibrary.org/a/olid/' +
        feature_.properties.author_key + '-S.jpg" />'+
        '<h5>' +
        feature_.properties.release_year +
        '</h5></div>';
    // Highlight corresponding feature on the map
    popup.setLngLat(feature_.geometry.coordinates)
        //.setLngLat(feature.geometry.coordinates)
        .setHTML(popup_html)
        .addTo(map);
        //drawPolygon(feature_.properties.line)
        drawCircles(feature_.properties.line);
        console.log(feature_.properties.author_key);
};

function removePopAndLine() {
    popup.remove();
    map.removeLayer(last_line);
    last_line = "0"
}

function renderListings(features) {
    // Clear any existing listings
    listingEl.innerHTML = '';
    if (features.length) {
        features.forEach(function (feature) {
            var prop = feature.properties;
            var item = document.createElement('a');
            //item.href = prop.wikipedia;
            //item.target = '_blank';
            item.textContent = prop.title;
            item.addEventListener('mouseover', function () {
                showPopAndLine(feature)
            });
            item.addEventListener('mouseleave', function () {
                removePopAndLine()
            });
            listingEl.appendChild(item);
        });
        // Show the filter input
        filterEl.parentNode.style.display = 'block';
    } else {

    }
}

function normalize(string) {
    return string.trim().toLowerCase();
}

function getUniqueFeatures(array, comparatorProperty) {
    var existingFeatureKeys = {};
    // Because features come from tiled vector data, feature geometries may be split
    // or duplicated across tile boundaries and, as a result, features may appear
    // multiple times in query results.
    var uniqueFeatures = array.filter(function (el) {
        if (existingFeatureKeys[el.properties[comparatorProperty]]) {
            return false;
        } else {
            existingFeatureKeys[el.properties[comparatorProperty]] = true;
            return true;
        }
    });
    return uniqueFeatures;
}

map.on('load', function () {
    var empty = document.createElement('p');
    empty.textContent = 'Drag the map to populate results';
    listingEl.appendChild(empty);

    map.on('moveend', function () {
        var features = map.queryRenderedFeatures({
            layers: ['books-layer']
        });
        if (features) {
            var uniqueFeatures = getUniqueFeatures(features, "title");
            // Populate features for the listing overlay.
            renderListings(uniqueFeatures);

            // Clear the input container
            //filterEl.value = '';

            // Store the current features in sn `airports` variable to
            // later use for filtering on `keyup`.
            books = uniqueFeatures;
        }
        else if (filterEl.value==''){
            
        }      

    });


    map.on('click', function (e) {
        var features = map.queryRenderedFeatures(e.point, {
            layers: ['books-layer']
        });
        var feature = features[0];
        //console.log(feature)
        if (feature!=undefined){
            showPopAndLine(feature);
        map.flyTo({
            center: feature.geometry.coordinates
        });
        }
    });

    filterEl.addEventListener('keyup', function (e) {
        var value = normalize(e.target.value);

        // Filter visible features that don't match the input value.
        var filtered = books.filter(function (feature) {
            var name1 = normalize(feature.properties.title);
            var author1 = normalize(feature.properties.author);
            var year_released = normalize(feature.properties.release_year);
            
            var inRange;
            if (years_after < years_before) {
                inRange = (year_released >= years_after) && (year_released < years_before);
                //console.log( "years_after<years_before, inrange is "+ inRange)
            }
            else{
                inRange = (year_released <= years_after) && (year_released > years_before);
                //console.log( "years_after>years_before, inrange is "+ inRange)
            }
            return (name1.indexOf(value) > -1 || author1.indexOf(value) > -1) && inRange;
        });

        // Populate the sidebar with filtered results
        renderListings(filtered);

        // Set the filter to populate features into the layer.
        if (filtered.length > 0) {
            let filter = ['match', ['get', 'title'], filtered.map(function (feature) {
                return feature.properties.title;
            }), true, false];

            map.setFilter('books-layer', filter, true);
            map.setLayoutProperty('books-layer', 'visibility', 'visible');
        } else {
           // map.setLayoutProperty('books-layer', 'visibility', 'none');
           //filterEl.value=='';
           //listingEl.innerHTML = '';

           // map.setFilter('books-layer', ['has', 'title']);
            filterByYears();
        }

    });

    //range years filters
    var years_before = '2018';
    var years_after = '1600';
    var filtered_by_years;
    document.getElementById('years-after').addEventListener('input', function (e) {
        years_after = e.target.value;
        filterByYears();
    });

    document.getElementById('years-before').addEventListener('input', function (e) {
        years_before = e.target.value;
        filterByYears();
    });

    function filterByYears() {
        var filter1;
        if (years_after < years_before) {
            console.log(years_after + '-' + years_before);
            filter1 = ["all",
                [">=", ["get", "release_year"], years_after],
                ["<=", ["get", "release_year"], years_before]
            ];
        } else {
            console.log(years_before + '-' + years_after);
            filter1 = ["all",
                ["<=", ["get", "release_year"], years_after],
                [">=", ["get", "release_year"], years_before]
            ];
        };
        filtered_by_years = map.setFilter('books-layer', filter1);
        //console.log(filtered_by_years);
    };

});
renderListings([]);

function drawPolygon(line) {

    if (last_line != "0") {
        map.removeLayer(last_line);
    }
    last_line = (Math.floor((Math.random() * 10000) + 1)).toString();;;
    var list1 = JSON.parse(line);

    map.addLayer({
        "id": last_line,
        "type": "line",
        "source": {
            "type": "geojson",
            "data": {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": list1
                }
            }
        },
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        "paint": {
            "line-color": "#972e2e",
            "line-width": 3,
            "line-opacity": 0.5
        }
    }, "books-layer");

};

function drawCircles(line){
    if (last_line != "0") {
        map.removeLayer(last_line);
    }
    last_line = (Math.floor((Math.random() * 10000) + 1)).toString();;;
    var list1 = JSON.parse(line);

    const allPoints = list1.map(point => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: point
        }
    }));

    map.addLayer({
        "id": last_line,
        "type": "circle",
        "source": {
            "type": 'geojson',
            "data": {
                "type": 'FeatureCollection',
                "features": allPoints
            }
        },
        "paint": {
        'circle-color': '#e27c06',
      'circle-radius': {'base': 15,
      'stops': [[12, 15], [18, 180]]},
      'circle-pitch-scale': 'map',
      'circle-stroke-width': 0,
      'circle-blur': 0.4,
      'circle-opacity':0.7,
        }
    }, "books-layer");

};

//search locations
map.addControl(new MapboxGeocoder({
    accessToken: mapboxgl.accessToken
}));

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());