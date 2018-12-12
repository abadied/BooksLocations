mapboxgl.accessToken = 'pk.eyJ1IjoiYW1pdHVyOTEiLCJhIjoiY2pvbzhkeHN1MGx0ZzNwbHd6cmVkMXFiMyJ9.pXauUkubGnbAUaewUAJ42Q';
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/amitur91/cjoo8efrd2tbi2squnueoz7kv',
    center: [34.841999, 31.847261],
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
        '" /></div>' +
        '<div class="right-half">' +
        '<h3>' +
        feature_.properties.title +
        '</h3><h5>' +
        feature_.properties.author +
        '</h5>' +
        '<h5>' +
        feature_.properties.release_year +
        '</h5></div>';
    // Highlight corresponding feature on the map
    popup.setLngLat(feature_.geometry.coordinates)
        //.setLngLat(feature.geometry.coordinates)
        .setHTML(popup_html)
        .addTo(map);
    drawPolygon(feature_.properties.line);
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

    map.addLayer({
        "id": "books-layer",
        "source": {
            "type": "vector",
            "url": "mapbox://amitur91.cjoxb8xa00rkf2qrvj68j57kf-5dqeo"
        },
        "source-layer": "book_0.1",
        "type": "symbol",
        "layout": {
            "icon-image": "book-icon",
            "icon-padding": 0,
            "icon-allow-overlap": true
        }
    });

    var empty = document.createElement('p');
    empty.textContent = 'Drag the map to populate results';
    listingEl.appendChild(empty);
    // Hide the filter input
    //filterEl.parentNode.style.display = 'none';



    map.on('moveend', function () {
        var features = map.queryRenderedFeatures({
            layers: ['books-layer']
        });
        if (features) {
            var uniqueFeatures = getUniqueFeatures(features, "title");
            // Populate features for the listing overlay.
            renderListings(uniqueFeatures);

            // Clear the input container
            filterEl.value = '';

            // Store the current features in sn `airports` variable to
            // later use for filtering on `keyup`.
            books = uniqueFeatures;
        }
    });


    map.on('click', function (e) {
        var features = map.queryRenderedFeatures(e.point, {
            layers: ['books-layer']
        });
        var feature = features[0];
        if (feature)
            showPopAndLine(feature);
        map.flyTo({
            center: feature.geometry.coordinates
        });
    });

    filterEl.addEventListener('keyup', function (e) {
        var value = normalize(e.target.value);

        // Filter visible features that don't match the input value.
        var filtered = books.filter(function (feature) {
            var name1 = normalize(feature.properties.title);
            var author1 = normalize(feature.properties.author);
            return name1.indexOf(value) > -1 || author1.indexOf(value) > -1;
        });
        console.log(filtered)

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
            map.setLayoutProperty('books-layer', 'visibility', 'none');
        }

    });

    //range years filters
    var years_before = '2018';
    var years_after = '1770';
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
        map.setFilter('books-layer', filter1);
        
        // var filtered = books.filter(function (feature) {
        //     var name1 = normalize(feature.properties.title);
        //     var author1 = normalize(feature.properties.author);
        //     return name1.indexOf(value) > -1 || author1.indexOf(value) > -1;
        // });
        // renderListings(filtered);

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
            "line-width": 4,
            "line-opacity": 0.7
        }
    });

};
//search locations
map.addControl(new MapboxGeocoder({
    accessToken: mapboxgl.accessToken
}));

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());